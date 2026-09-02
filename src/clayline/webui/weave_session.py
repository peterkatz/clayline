"""Private, bounded in-memory state for the local Weave HTTP workflow.

Browser clients receive only opaque identifiers.  Meshes, slices, and settled
results never cross sessions, and every cache is both time- and size-bounded.
The stored domain objects are immutable, so worker threads can safely reuse
them without copying large NumPy arrays.
"""

from __future__ import annotations

import secrets
import sys
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

CacheKind = Literal["recipe", "mesh", "slice", "prepared", "result"]
SessionKind = CacheKind | Literal["session"]

CACHE_SESSION_COOKIE = "clayline_weave_session"
DEFAULT_TTL_SECONDS = 8 * 60 * 60
DEFAULT_TOUCH_INTERVAL_SECONDS = 3 * 60
DEFAULT_ITEMS_PER_KIND = 2
DEFAULT_MAX_SESSIONS = 4
DEFAULT_SESSION_BYTES = 256 * 1024 * 1024
DEFAULT_TOTAL_BYTES = 768 * 1024 * 1024


class WeaveSessionError(LookupError):
    """Raised when an opaque cache id is absent, expired, or out of scope."""

    def __init__(self, kind: SessionKind) -> None:
        self.kind = kind
        label = "Weave session" if kind == "session" else f"{kind} id"
        super().__init__(f"unknown or expired {label}")


class WeaveCacheLimitError(ValueError):
    """Raised when one value cannot fit inside the bounded session cache."""


@dataclass(slots=True)
class _Entry:
    value: Any
    size_bytes: int
    touched: float


@dataclass(slots=True)
class WeaveSessionCache:
    """One browser session's bounded per-stage LRU caches."""

    ttl_seconds: float = DEFAULT_TTL_SECONDS
    items_per_kind: int = DEFAULT_ITEMS_PER_KIND
    max_bytes: int = DEFAULT_SESSION_BYTES
    clock: Callable[[], float] = time.monotonic
    _items: dict[CacheKind, OrderedDict[str, _Entry]] = field(
        default_factory=lambda: {
            "recipe": OrderedDict(),
            "mesh": OrderedDict(),
            "slice": OrderedDict(),
            "prepared": OrderedDict(),
            "result": OrderedDict(),
        },
        init=False,
        repr=False,
    )
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)
    last_touched: float = field(init=False)

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0:
            raise ValueError("session TTL must be positive")
        if self.items_per_kind <= 0:
            raise ValueError("items_per_kind must be positive")
        if self.max_bytes <= 0:
            raise ValueError("session byte limit must be positive")
        self.last_touched = self.clock()

    def put(self, kind: CacheKind, value: Any, *, size_bytes: int | None = None) -> str:
        """Store a value and return a non-derivable, session-local identifier."""

        self._require_kind(kind)
        estimated = estimate_cache_bytes(value) if size_bytes is None else int(size_bytes)
        if estimated < 0:
            raise ValueError("cache size cannot be negative")
        if estimated > self.max_bytes:
            raise WeaveCacheLimitError(
                f"{kind} needs about {estimated:,} bytes, above this session's "
                f"{self.max_bytes:,}-byte cache limit"
            )
        with self._lock:
            now = self.clock()
            self._expire_locked(now)
            item_id = f"{kind}_{secrets.token_urlsafe(18)}"
            bucket = self._items[kind]
            bucket[item_id] = _Entry(value=value, size_bytes=estimated, touched=now)
            while len(bucket) > self.items_per_kind:
                bucket.popitem(last=False)
            self._evict_to_byte_limit_locked()
            if item_id not in bucket:
                raise WeaveCacheLimitError(
                    f"{kind} could not fit inside this session's bounded cache"
                )
            self.last_touched = now
            return item_id

    def get(self, kind: CacheKind, item_id: str, *, touch: bool = True) -> Any:
        """Return and LRU-touch a session-local value, or fail without leaking scope."""

        return self._get(kind, item_id, touch=touch, min_touch_interval=None)

    def get_throttled(
        self,
        kind: CacheKind,
        item_id: str,
        *,
        min_touch_interval: float = DEFAULT_TOUCH_INTERVAL_SECONDS,
    ) -> Any:
        """Return a value, refreshing its LRU age at most once per interval."""

        if min_touch_interval <= 0:
            raise ValueError("minimum touch interval must be positive")
        return self._get(
            kind,
            item_id,
            touch=True,
            min_touch_interval=float(min_touch_interval),
        )

    def _get(
        self,
        kind: CacheKind,
        item_id: str,
        *,
        touch: bool,
        min_touch_interval: float | None,
    ) -> Any:
        """Resolve one value and optionally refresh its entry age atomically."""

        self._require_kind(kind)
        if not isinstance(item_id, str) or not item_id:
            raise WeaveSessionError(kind)
        with self._lock:
            now = self.clock()
            self._expire_locked(now)
            bucket = self._items[kind]
            entry = bucket.get(item_id)
            if entry is None:
                raise WeaveSessionError(kind)
            touch_is_due = min_touch_interval is None or now - entry.touched >= min_touch_interval
            if touch and touch_is_due:
                entry.touched = now
                bucket.move_to_end(item_id)
                self.last_touched = now
            return entry.value

    def count(self, kind: CacheKind) -> int:
        """Return the live item count; intended for diagnostics and tests."""

        self._require_kind(kind)
        with self._lock:
            self._expire_locked(self.clock())
            return len(self._items[kind])

    def clear(self) -> None:
        """Release every retained object in this browser session."""

        with self._lock:
            for bucket in self._items.values():
                bucket.clear()

    @property
    def estimated_bytes(self) -> int:
        with self._lock:
            self._expire_locked(self.clock())
            return sum(
                entry.size_bytes for bucket in self._items.values() for entry in bucket.values()
            )

    def expired(self, now: float | None = None) -> bool:
        at = self.clock() if now is None else now
        return at - self.last_touched > self.ttl_seconds

    def _expire_locked(self, now: float) -> None:
        for bucket in self._items.values():
            expired_ids = [
                item_id
                for item_id, entry in bucket.items()
                if now - entry.touched > self.ttl_seconds
            ]
            for item_id in expired_ids:
                del bucket[item_id]

    def _evict_to_byte_limit_locked(self) -> None:
        while self._total_bytes_locked() > self.max_bytes:
            oldest: tuple[float, CacheKind, str] | None = None
            for kind, bucket in self._items.items():
                if not bucket:
                    continue
                item_id = next(iter(bucket))
                candidate = (bucket[item_id].touched, kind, item_id)
                if oldest is None or candidate < oldest:
                    oldest = candidate
            if oldest is None:
                break
            _, kind, item_id = oldest
            del self._items[kind][item_id]

    def _total_bytes_locked(self) -> int:
        return sum(entry.size_bytes for bucket in self._items.values() for entry in bucket.values())

    @staticmethod
    def _require_kind(kind: str) -> None:
        if kind not in {"recipe", "mesh", "slice", "prepared", "result"}:
            raise ValueError(f"unknown Weave cache kind {kind!r}")


@dataclass(slots=True)
class WeaveSessionManager:
    """Bound the number of local browser sessions as well as each session."""

    ttl_seconds: float = DEFAULT_TTL_SECONDS
    items_per_kind: int = DEFAULT_ITEMS_PER_KIND
    max_session_bytes: int = DEFAULT_SESSION_BYTES
    max_sessions: int = DEFAULT_MAX_SESSIONS
    max_total_bytes: int = DEFAULT_TOTAL_BYTES
    clock: Callable[[], float] = time.monotonic
    _sessions: OrderedDict[str, WeaveSessionCache] = field(
        default_factory=OrderedDict, init=False, repr=False
    )
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def resolve_fixed(self, token: str) -> tuple[WeaveSessionCache, str, bool]:
        """Get-or-create the session under an EXACT caller-owned key.

        The desktop app is a single artist behind one per-launch secret
        token (already unguessable — it is the auth token). Its one session
        must live under that exact key so every request finds the same
        mesh/slice cache regardless of whether the WKWebView round-trips the
        separate weave cookie. Browsers still get opaque minted tokens via
        :meth:`resolve` (a web tab must never pin a guessable session key).
        """

        if not isinstance(token, str) or not token:
            raise ValueError("fixed session token must be non-empty")
        with self._lock:
            now = self.clock()
            self._expire_locked(now)
            cache = self._sessions.get(token)
            if cache is None:
                cache = WeaveSessionCache(
                    ttl_seconds=self.ttl_seconds,
                    items_per_kind=self.items_per_kind,
                    max_bytes=self.max_session_bytes,
                    clock=self.clock,
                )
                self._sessions[token] = cache
                while len(self._sessions) > self.max_sessions:
                    self._sessions.popitem(last=False)
                return cache, token, True
            cache.last_touched = now
            self._sessions.move_to_end(token)
            return cache, token, False

    def resolve(self, token: str | None) -> tuple[WeaveSessionCache, str, bool]:
        """Resolve an existing token or allocate a fresh opaque browser session."""

        with self._lock:
            now = self.clock()
            self._expire_locked(now)
            if isinstance(token, str) and token in self._sessions:
                cache = self._sessions[token]
                cache.last_touched = now
                self._sessions.move_to_end(token)
                return cache, token, False
            resolved = secrets.token_urlsafe(32)
            cache = WeaveSessionCache(
                ttl_seconds=self.ttl_seconds,
                items_per_kind=self.items_per_kind,
                max_bytes=self.max_session_bytes,
                clock=self.clock,
            )
            self._sessions[resolved] = cache
            while len(self._sessions) > self.max_sessions:
                self._sessions.popitem(last=False)
            return cache, resolved, True

    def put(
        self,
        token: str,
        kind: CacheKind,
        value: Any,
        *,
        size_bytes: int | None = None,
    ) -> str:
        """Store through the manager so the process-wide ceiling is enforced."""

        with self._lock:
            cache = self._sessions.get(token)
            if cache is None:
                raise WeaveSessionError("session")
            item_id = cache.put(kind, value, size_bytes=size_bytes)
            self._sessions.move_to_end(token)
            self._trim_total_locked(protected_token=token)
            return item_id

    def clear(self, token: str | None = None) -> None:
        """Clear one session, or all sessions during application shutdown."""

        with self._lock:
            if token is None:
                for cache in self._sessions.values():
                    cache.clear()
                self._sessions.clear()
                return
            cache = self._sessions.pop(token, None)
            if cache is not None:
                cache.clear()

    @property
    def estimated_bytes(self) -> int:
        with self._lock:
            return sum(cache.estimated_bytes for cache in self._sessions.values())

    def _expire_locked(self, now: float) -> None:
        for token in [token for token, cache in self._sessions.items() if cache.expired(now)]:
            del self._sessions[token]

    def _trim_total_locked(self, *, protected_token: str) -> None:
        while (
            sum(cache.estimated_bytes for cache in self._sessions.values()) > self.max_total_bytes
        ):
            victim = next(
                (token for token in self._sessions if token != protected_token),
                None,
            )
            if victim is None:
                # The active cache is independently capped below this manager
                # ceiling, so this indicates inconsistent custom limits.
                self._sessions[protected_token].clear()
                raise WeaveCacheLimitError(
                    "Weave data exceeds the process-wide in-memory cache limit"
                )
            self._sessions.pop(victim).clear()


def estimate_cache_bytes(value: Any) -> int:
    """Conservatively estimate the large owned buffers in a cached domain value."""

    from clayline.weave_models import MeshForm, SlicedForm
    from clayline.weave_restore import WeaveRestoreRecipe
    from clayline.weave_restore_codec import encode_restore_capsule
    from clayline.weave_workflow import PreparedWeaveResult, WeaveResult

    if isinstance(value, WeaveRestoreRecipe):
        capsule = encode_restore_capsule(
            source_mesh_name=value.source_mesh_name,
            source_mesh_sha256=value.source_mesh_sha256,
            pattern=value.pattern,
            profile=value.profile,
            profile_prime_mm=value.profile_prime_mm,
            profile_end_early_mm=value.profile_end_early_mm,
            up_axis=value.up_axis,
            scale=value.scale,
            offset=value.offset,
            rotation_deg=value.rotation_deg,
            rotation_x_deg=value.rotation_x_deg,
            rotation_y_deg=value.rotation_y_deg,
            layer_height=value.layer_height,
            first_layer_height=value.first_layer_height,
            sample_spacing=value.sample_spacing,
            bead_width=value.bead_width,
            layer_range=value.layer_range,
            source_layer_total=value.source_layer_total,
            flow_multiplier=value.flow_multiplier,
            wet_density_g_cm3=value.wet_density_g_cm3,
            prime_mm=value.prime_mm,
            end_early_mm=value.end_early_mm,
            reproducible=value.reproducible,
            job_id=value.job_id,
        )
        return len(capsule.encode("ascii")) + 16_384
    if isinstance(value, MeshForm):
        return int(value.vertices.nbytes + value.faces.nbytes + 4096)
    if isinstance(value, SlicedForm):
        arrays = sum(
            ring.points.nbytes + ring.outward_normals.nbytes + ring.u.nbytes
            for layer in value.layers
            for ring in layer.rings
        )
        return int(arrays + value.point_count * 32 + 8192)
    if isinstance(value, PreparedWeaveResult):
        prepared_motions = len(value.prepared.events) * 320
        stream_moves = len(value.stream.moves) * 256
        return estimate_cache_bytes(value.sliced) + prepared_motions + stream_moves + 16_384
    if isinstance(value, WeaveResult):
        prepared_motions = len(value.emission.prepared.events) * 320
        stream_moves = len(value.emission.stream.moves) * 256
        return (
            estimate_cache_bytes(value.sliced)
            + len(value.emission.gcode.encode("utf-8"))
            + prepared_motions
            + stream_moves
            + 16_384
        )
    return max(1, sys.getsizeof(value))


__all__ = [
    "CACHE_SESSION_COOKIE",
    "DEFAULT_ITEMS_PER_KIND",
    "DEFAULT_TOTAL_BYTES",
    "DEFAULT_TTL_SECONDS",
    "WeaveCacheLimitError",
    "WeaveSessionCache",
    "WeaveSessionError",
    "WeaveSessionManager",
    "estimate_cache_bytes",
]
