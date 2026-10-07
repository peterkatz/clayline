"use strict";

// Browser-local settings only. Results, cache ids, and source mesh identity
// deliberately never enter this envelope.
((root, factory) => {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClaylineStudioState = api;
})(typeof window !== "undefined" ? window : globalThis, () => {
  const STORAGE_KEY = "clayline-ui-state.v1";
  const ENVELOPE_SCHEMA = "clayline.ui-state.v1";

  function clone(value) {
    return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
  }

  function emptyEnvelope() {
    return { schema: ENVELOPE_SCHEMA, modes: {} };
  }

  function settingsStorage(root) {
    try {
      return root?.claylineSettingsStorage || root?.localStorage || null;
    } catch (_error) {
      return root?.claylineSettingsStorage || null;
    }
  }

  function parseEnvelope(storage, { repair = true } = {}) {
    try {
      const raw = storage?.getItem(STORAGE_KEY);
      if (raw === null || raw === undefined || raw === "") return emptyEnvelope();
      const parsed = JSON.parse(raw);
      if (
        !parsed
        || parsed.schema !== ENVELOPE_SCHEMA
        || !parsed.modes
        || typeof parsed.modes !== "object"
        || Array.isArray(parsed.modes)
      ) {
        throw new Error("unsupported Clayline settings envelope");
      }
      return parsed;
    } catch (_error) {
      // Corrupt or old-schema storage must never white-screen the studio.
      // Removing it makes the next launch a true factory fallback.
      if (repair) {
        try { storage?.removeItem(STORAGE_KEY); } catch (_removeError) { /* storage may be unavailable */ }
      }
      return emptyEnvelope();
    }
  }

  function loadMode(storage, mode, validate = () => true) {
    const envelope = parseEnvelope(storage);
    const snapshot = envelope.modes[mode];
    if (snapshot === undefined) return null;
    try {
      if (!validate(snapshot)) throw new Error("unsupported mode snapshot");
      return clone(snapshot);
    } catch (_error) {
      // A bad snapshot in one mode should heal without discarding the other.
      delete envelope.modes[mode];
      try {
        if (Object.keys(envelope.modes).length) {
          storage?.setItem(STORAGE_KEY, JSON.stringify(envelope));
        } else {
          storage?.removeItem(STORAGE_KEY);
        }
      } catch (_storageError) { /* factory state remains usable */ }
      return null;
    }
  }

  function saveMode(storage, mode, snapshot) {
    try {
      const envelope = parseEnvelope(storage);
      envelope.modes[mode] = clone(snapshot);
      storage?.setItem(STORAGE_KEY, JSON.stringify(envelope));
      return true;
    } catch (_error) {
      // Quota/private-mode failures must not interrupt slicing.
      return false;
    }
  }

  function clearMode(storage, mode) {
    try {
      const envelope = parseEnvelope(storage);
      delete envelope.modes[mode];
      if (Object.keys(envelope.modes).length) {
        storage?.setItem(STORAGE_KEY, JSON.stringify(envelope));
      } else {
        storage?.removeItem(STORAGE_KEY);
      }
      return true;
    } catch (_error) {
      return false;
    }
  }

  function createSettledWriter({
    storage,
    mode,
    capture,
    delay = 600,
    setTimer = (callback, wait) => setTimeout(callback, wait),
    clearTimer = (timer) => clearTimeout(timer),
    onSettled = () => {},
  }) {
    let timer = null;
    let suspended = 0;

    const cancel = () => {
      if (timer !== null) clearTimer(timer);
      timer = null;
    };
    const flush = () => {
      cancel();
      if (suspended) return false;
      const snapshot = capture();
      const saved = saveMode(storage, mode, snapshot);
      onSettled(clone(snapshot), saved);
      return saved;
    };
    const schedule = () => {
      if (suspended) return;
      cancel();
      timer = setTimer(flush, delay);
    };
    const suspend = (callback) => {
      suspended += 1;
      cancel();
      try {
        return callback();
      } finally {
        suspended -= 1;
      }
    };
    const clear = () => {
      cancel();
      return clearMode(storage, mode);
    };
    // Whether an edit is still waiting out the debounce. Undo flushes it into
    // its own step first, so a quick Command-Z never steps back past it.
    const pending = () => timer !== null;

    return Object.freeze({ schedule, flush, cancel, suspend, clear, pending });
  }

  function createHistory({ limit = 100, onChange = () => {} } = {}) {
    const capacity = Math.max(2, Math.trunc(Number(limit)) || 100);
    let entries = [];
    let index = -1;

    const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
    const state = () => Object.freeze({
      canUndo: index > 0,
      canRedo: index >= 0 && index < entries.length - 1,
      length: entries.length,
      index,
    });
    const changed = () => onChange(state());
    const seed = (snapshot) => {
      entries = [clone(snapshot)];
      index = 0;
      changed();
    };
    const push = (snapshot) => {
      const next = clone(snapshot);
      if (index >= 0 && same(entries[index], next)) return false;
      entries = entries.slice(0, index + 1);
      entries.push(next);
      if (entries.length > capacity) entries.shift();
      index = entries.length - 1;
      changed();
      return true;
    };
    const undo = () => {
      if (index <= 0) return null;
      index -= 1;
      changed();
      return clone(entries[index]);
    };
    const redo = () => {
      if (index < 0 || index >= entries.length - 1) return null;
      index += 1;
      changed();
      return clone(entries[index]);
    };
    const current = () => index < 0 ? null : clone(entries[index]);
    // Rewrites the step the potter is on without making a new one and without
    // touching Redo. For what the studio fills in by itself after a change has
    // been recorded (the layer count a slice reports, the island stop it
    // proposes): that belongs to the step it came from, never a step of its own.
    const amend = (update) => {
      if (index < 0) return false;
      const next = clone(update(clone(entries[index])));
      if (next === undefined || same(entries[index], next)) return false;
      entries[index] = next;
      return true;
    };
    // The distinct values one key takes along the whole history, oldest first.
    const distinct = (key) => {
      const seen = [];
      entries.forEach((entry) => {
        const value = entry ? entry[key] : undefined;
        if (!seen.includes(value)) seen.push(value);
      });
      return seen;
    };
    // Lets the oldest steps fall off the bottom, as the step cap does, while
    // they match. The step the potter is on is never dropped.
    const forgetOldestWhile = (predicate) => {
      let dropped = 0;
      while (index > 0 && entries.length > 1 && predicate(entries[0])) {
        entries.shift();
        index -= 1;
        dropped += 1;
      }
      if (dropped) changed();
      return dropped;
    };

    return Object.freeze({
      seed, push, undo, redo, current, state, amend, distinct, forgetOldestWhile,
    });
  }

  // What the studio changed by itself, carried into the step the potter is on.
  // `before` and `after` are the live settings either side of the studio's own
  // change; `entry` is the recorded step. Only what moved between before and
  // after is written, so a number the potter is still typing (live, but not yet
  // in the step) stays out of the step and is recorded as its own one later.
  // Where nothing of the potter's is waiting, the step simply becomes `after`.
  // A setting kept as JSON text (the pattern) is carried field by field too.
  function carryStudioChange(entry, before, after) {
    const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
    const plain = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
    const parsed = (value) => {
      if (typeof value !== "string") return null;
      try {
        const object = JSON.parse(value);
        return plain(object) ? object : null;
      } catch (_error) {
        return null;
      }
    };
    const carry = (mine, was, now) => {
      if (same(was, now)) return mine;
      if (same(mine, was)) return clone(now);
      if (plain(mine) && plain(was) && plain(now)) {
        const out = { ...mine };
        new Set([...Object.keys(was), ...Object.keys(now)]).forEach((key) => {
          const next = carry(mine[key], was[key], now[key]);
          if (next === undefined) delete out[key];
          else out[key] = next;
        });
        return out;
      }
      const [mineObject, wasObject, nowObject] = [parsed(mine), parsed(was), parsed(now)];
      if (mineObject && wasObject && nowObject) {
        return JSON.stringify(carry(mineObject, wasObject, nowObject));
      }
      return clone(now);
    };
    return carry(clone(entry), clone(before), clone(after));
  }

  // One Undo or Redo. Whatever is still waiting out the debounce is recorded
  // first, as its own step, so the step taken back is always the last change
  // the potter made and nothing waiting is thrown away.
  function stepHistory({ writer, history, direction, apply, beforeStep = () => {} }) {
    beforeStep();
    writer?.flush();
    const entry = direction === "redo" ? history?.redo() : history?.undo();
    if (!entry) return false;
    apply(entry);
    return true;
  }

  // A small most-recently-used shelf. Undo uses it for the model files of the
  // last few steps and for slices already made this session; nothing on it is
  // ever written to disk.
  function createRecentShelf({ limit = 3, prefix = "item" } = {}) {
    const capacity = Math.max(1, Math.trunc(Number(limit)) || 1);
    const items = new Map();
    let counter = 0;
    const touch = (key, value) => {
      items.delete(key);
      items.set(key, value);
      while (items.size > capacity) items.delete(items.keys().next().value);
    };
    const add = (value) => {
      counter += 1;
      const key = `${prefix}-${counter}`;
      touch(key, value);
      return key;
    };
    const put = (key, value) => {
      touch(key, value);
      return key;
    };
    const get = (key) => {
      if (!items.has(key)) return null;
      const value = items.get(key);
      touch(key, value);
      return value;
    };
    const has = (key) => items.has(key);
    // Reads without counting as a use, so sizing the shelf never reorders it.
    const peek = (key) => (items.has(key) ? items.get(key) : null);
    const keep = (keys) => {
      const wanted = new Set(keys);
      [...items.keys()].forEach((key) => { if (!wanted.has(key)) items.delete(key); });
    };
    const drop = (predicate) => {
      [...items.entries()].forEach(([key, value]) => { if (predicate(value, key)) items.delete(key); });
    };
    const keys = () => [...items.keys()];
    return Object.freeze({ add, put, get, peek, has, keep, drop, keys, size: () => items.size });
  }

  function weaveRestoreAction(current, next, { hasFile = false, hasSlice = false } = {}) {
    const currentPlacement = { ...current.placement, profile: current.slice.profile };
    const nextPlacement = { ...next.placement, profile: next.slice.profile };
    if (hasFile && JSON.stringify(currentPlacement) !== JSON.stringify(nextPlacement)) {
      return "mesh";
    }
    const coreSliceKeys = [
      "nozzle", "layer_height", "first_layer_height", "sample_spacing", "bead_width",
    ];
    if (coreSliceKeys.some((key) => current.slice[key] !== next.slice[key])) return "slice";
    // How the top is sliced is part of the slice too. A print file 0.5.1 saved
    // says "below" and every other job leaves the key out, so an old file over
    // the same model at the same numbers slices again to its own layers rather
    // than settling on a stack one layer taller than the one it was saved with.
    const topLayer = (slice) => (slice.top_layer === "below" ? "below" : "nearest");
    if (topLayer(current.slice) !== topLayer(next.slice)) return "slice";
    // Whether hollows are ignored changes the rings themselves. Every save that
    // says nothing about it kept them, so an absent key reads as "keep".
    const hollows = (slice) => (slice.hollows === "ignore" ? "ignore" : "keep");
    if (hollows(current.slice) !== hollows(next.slice)) return "slice";
    return hasSlice ? "settle" : "invalidate";
  }

  return Object.freeze({
    STORAGE_KEY,
    ENVELOPE_SCHEMA,
    settingsStorage,
    loadMode,
    saveMode,
    clearMode,
    createSettledWriter,
    createHistory,
    stepHistory,
    carryStudioChange,
    createRecentShelf,
    weaveRestoreAction,
  });
});
