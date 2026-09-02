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

    return Object.freeze({ schedule, flush, cancel, suspend, clear });
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

    return Object.freeze({ seed, push, undo, redo, current, state });
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
    weaveRestoreAction,
  });
});
