"use strict";

// Clayline · reference photos — the pixels behind the drawing surface's
// lightbox.  A reference is a photo the artist traces over; it never prints,
// never enters a slice request, and never appears in an export.
//
// The settings envelope carries placement only ({image_id, x, y, width_mm,
// rotation_deg, opacity}); the image bytes live here, in IndexedDB, written
// exactly once per import.  Decoded bitmaps are cached in memory by image_id
// so the draw loop never waits on the database twice for the same photo.
//
//   importImage(file) -> Promise<{imageId, width, height, bitmap}>
//        Decode, shrink so the longest edge is at most 2048 px, re-encode
//        (PNG keeps the photo's transparency, JPEG otherwise), store the
//        bytes once, and hand back a bitmap ready to draw.  Decode tries the
//        browser first; a HEIC photo the browser can't open (any engine but
//        Safari's) is sent once to /api/convert-image, the packaged app's
//        Pillow/pillow-heif fallback, before importImage rejects.
//   bitmap(imageId, onReady) -> drawable | null
//        Synchronous cache read.  A miss kicks off the IndexedDB load and
//        calls onReady once the bitmap is drawable — the canvas draws nothing
//        in the meantime, no placeholder.
//   imageBlob(imageId) -> Promise<Blob|null>
//        The stored bytes for one photo, so a project file can carry it.
//        Null when the photo was never stored or the database is unavailable.
//   storeImage(imageId, blob) -> Promise<boolean>
//        Puts a photo back under the id its placement already names — opening
//        a project restores the pixels the placement points at.  The bitmap
//        cache is seeded from the same blob, so the photo draws even where
//        the database refused the write.
//   sweep(keepIds) -> Promise
//        Deletes every stored photo whose id is not in keepIds.  BOOT ONLY:
//        mid-session an undo may still restore a removed photo, so orphans
//        wait for the next launch.
((root, factory) => {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClaylineReferenceStore = api;
})(typeof window !== "undefined" ? window : globalThis, (root) => {
  const DB_NAME = "clayline-reference-images.v1";
  const STORE = "images";
  const MAX_EDGE_PX = 2048;
  const JPEG_QUALITY = 0.9;

  let dbPromise = null;

  function openDb() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
      let request;
      try {
        request = root.indexedDB.open(DB_NAME, 1);
      } catch (error) {
        reject(error);
        return;
      }
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE);
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("IndexedDB unavailable"));
    });
    return dbPromise;
  }

  function transact(mode, run) {
    return openDb().then((db) => new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE, mode);
      const request = run(transaction.objectStore(STORE));
      transaction.oncomplete = () => resolve(request ? request.result : undefined);
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    }));
  }

  const putBlob = (id, blob) => transact("readwrite", (store) => store.put(blob, id));
  const getBlob = (id) => transact("readonly", (store) => store.get(id));

  function sweep(keepIds) {
    const wanted = new Set(Array.isArray(keepIds) ? keepIds : []);
    return transact("readwrite", (store) => {
      const keys = store.getAllKeys();
      keys.onsuccess = () => {
        for (const key of keys.result) {
          if (!wanted.has(key)) store.delete(key);
        }
      };
      return null;
    }).catch(() => undefined);
  }

  /* ---------- decode and cache ------------------------------------------- */

  const bitmaps = new Map();   // image_id -> drawable (bitmap or canvas)
  const loading = new Map();   // image_id -> Promise<drawable|null>

  function newId() {
    return `ref-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function hasAlpha(context, width, height) {
    const data = context.getImageData(0, 0, width, height).data;
    for (let i = 3; i < data.length; i += 4) {
      if (data[i] < 255) return true;
    }
    return false;
  }

  function encode(canvas, type, quality) {
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error("photo re-encode failed"))),
        type,
        quality,
      );
    });
  }

  function decodeBlob(blob) {
    // createImageBitmap is the fast path; an <img> over an object URL is the
    // fallback for engines that cannot bitmap a stored blob.  drawImage
    // accepts either, and both carry width/height.
    if (typeof root.createImageBitmap === "function") {
      return root.createImageBitmap(blob).catch(() => decodeViaImage(blob));
    }
    return decodeViaImage(blob);
  }

  function decodeViaImage(blob) {
    return new Promise((resolve, reject) => {
      const url = root.URL.createObjectURL(blob);
      const image = new root.Image();
      image.onload = () => { root.URL.revokeObjectURL(url); resolve(image); };
      image.onerror = () => { root.URL.revokeObjectURL(url); reject(new Error("photo decode failed")); };
      image.src = url;
    });
  }

  // Local decode first (in the packaged app's WKWebView this is where HEIC
  // already works — Safari's engine decodes it natively), the engine's
  // Pillow/pillow-heif round-trip second, and an honest failure only once
  // both have declined. convertViaEngine only ever runs after a local
  // rejection, so the common PNG/JPEG/WebP/HEIC-on-Safari path never leaves
  // the browser.
  async function decodeSource(file) {
    const local = await decodeBlob(file).catch(() => null);
    if (local) return local;
    const converted = await convertViaEngine(file);
    if (converted) {
      const decoded = await decodeBlob(converted).catch(() => null);
      if (decoded) return decoded;
    }
    throw new Error(
      "Clayline couldn't read that photo. It reads PNG, JPEG, WebP, and HEIC.",
    );
  }

  function convertViaEngine(file) {
    return root
      .fetch("/api/convert-image", {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: file,
      })
      .then((response) => (response.ok ? response.blob() : null))
      .catch(() => null);
  }

  async function importImage(file) {
    const source = await decodeSource(file);
    const scale = Math.min(1, MAX_EDGE_PX / Math.max(source.width, source.height));
    const width = Math.max(1, Math.round(source.width * scale));
    const height = Math.max(1, Math.round(source.height * scale));
    const canvas = root.document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    context.drawImage(source, 0, 0, width, height);
    if (typeof source.close === "function") source.close();
    const blob = hasAlpha(context, width, height)
      ? await encode(canvas, "image/png")
      : await encode(canvas, "image/jpeg", JPEG_QUALITY);
    const imageId = newId();
    // The photo is already decoded, so a store that cannot take the bytes —
    // the packaged app's WebKit data store is ephemeral and may have no
    // IndexedDB at all — must not unplace it. The in-memory cache below
    // carries the session, which is as long as anything lives here anyway:
    // restart is a clean slate. Only a photo that cannot be DECODED rejects.
    await putBlob(imageId, blob).catch(() => undefined);
    // The canvas the photo was shrunk onto is itself the drawable: caching it
    // skips a second decode, and drawImage takes a canvas as happily as a
    // bitmap.
    bitmaps.set(imageId, canvas);
    return { imageId, width, height, bitmap: canvas };
  }

  function imageBlob(imageId) {
    if (typeof imageId !== "string" || !imageId) return Promise.resolve(null);
    return getBlob(imageId).then((blob) => blob || null).catch(() => null);
  }

  function storeImage(imageId, blob) {
    if (typeof imageId !== "string" || !imageId || !blob) return Promise.resolve(false);
    // A photo arriving under an id the session already drew must replace it,
    // never lose the race with a load already in flight.
    bitmaps.delete(imageId);
    loading.delete(imageId);
    return putBlob(imageId, blob)
      .catch(() => undefined)
      .then(() => decodeBlob(blob).catch(() => null))
      .then((decoded) => {
        if (decoded) bitmaps.set(imageId, decoded);
        return Boolean(decoded);
      });
  }

  function bitmap(imageId, onReady) {
    if (typeof imageId !== "string" || !imageId) return null;
    const cached = bitmaps.get(imageId);
    if (cached) return cached;
    let pending = loading.get(imageId);
    if (!pending) {
      pending = getBlob(imageId)
        .then((blob) => (blob ? decodeBlob(blob) : null))
        .catch(() => null)
        .then((decoded) => {
          loading.delete(imageId);
          if (decoded) bitmaps.set(imageId, decoded);
          return decoded;
        });
      loading.set(imageId, pending);
    }
    if (typeof onReady === "function") {
      pending.then((decoded) => { if (decoded) onReady(imageId); });
    }
    return null;
  }

  return Object.freeze({ importImage, bitmap, imageBlob, storeImage, sweep });
});
