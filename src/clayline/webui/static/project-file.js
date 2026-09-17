"use strict";

// The Clayline project container: one file holding a whole job — what is on
// the bed and every setting of its mode — so the work can be picked up again
// later.  The page owns this codec end to end; nothing here touches disk and
// nothing here talks to the engine.
//
// Inside the file:
//
//   project.json
//   sources/<mesh file name>              Weave only
//   references/<image id>.png|.jpg        Draw only
//
// project.json carries the mode's settings snapshot verbatim, so
// applyDrawSettings() / applyWeaveSettings() open it with no translation.
// When a later release changes a settings schema, add a migration from the
// old inner schema here: the reader must never silently apply a snapshot it
// does not recognise, and it must never half-apply one either — read() either
// returns a whole project or refuses, leaving the bed untouched.
//
// read() refuses with exactly the three messages in MESSAGES.  Everything it
// knows beyond that lives in error.detail, which is for the console and the
// tests, never for a person.  write() is handed studio state that is already
// valid, so bad input to it is a programming mistake and throws a plain Error.
((root, factory) => {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClaylineProjectFile = api;
})(typeof window !== "undefined" ? window : globalThis, () => {
  const PROJECT_SCHEMA = "clayline.project.v1";
  const PROJECT_MEDIA_TYPE = "application/vnd.clayline.project+zip";
  const SETTINGS_SCHEMA = Object.freeze({
    draw: "clayline.draw-settings.v2",
    weave: "clayline.weave-settings.v1",
  });
  const MANIFEST_NAME = "project.json";
  const SOURCE_FOLDER = "sources";
  const REFERENCE_FOLDER = "references";
  const REFERENCE_EXTENSIONS = Object.freeze({
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
  });

  // Own properties only, so a name every object carries — "constructor",
  // "__proto__" — is not mistaken for a kind of photo Clayline can open.
  const referenceExtension = (mediaType) =>
    (Object.prototype.hasOwnProperty.call(REFERENCE_EXTENSIONS, mediaType)
      ? REFERENCE_EXTENSIONS[mediaType]
      : undefined);

  // The whole file is bounded by the same rule the mesh upload already uses.
  const MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024;
  const MAX_MANIFEST_BYTES = 32 * 1024 * 1024;
  const MAX_REFERENCE_BYTES = 64 * 1024 * 1024;

  const MESSAGES = Object.freeze({
    "not-a-project": "That isn't a Clayline project file, or it's damaged.",
    "newer-version": "This project was saved by a newer Clayline. Update Clayline to open it.",
    "too-large": "This project is too large to open here.",
  });

  class ProjectFileError extends Error {
    constructor(code, detail = "") {
      const known = Object.prototype.hasOwnProperty.call(MESSAGES, code)
        ? code
        : "not-a-project";
      super(MESSAGES[known]);
      this.name = "ProjectFileError";
      this.code = known;
      this.detail = String(detail);
    }
  }

  const refuse = (detail) => new ProjectFileError("not-a-project", detail);
  const tooLarge = (detail) => new ProjectFileError("too-large", detail);
  const tooNew = (detail) => new ProjectFileError("newer-version", detail);

  const encoder = new TextEncoder();
  const decoder = new TextDecoder("utf-8");

  async function asBytes(value) {
    if (value instanceof Uint8Array) return value;
    if (value instanceof ArrayBuffer) return new Uint8Array(value);
    if (ArrayBuffer.isView(value)) {
      return new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
    }
    if (value && typeof value.arrayBuffer === "function") {
      return new Uint8Array(await value.arrayBuffer());
    }
    if (typeof value === "string") return encoder.encode(value);
    throw new Error("Clayline project: expected bytes, a Blob, or text");
  }

  function concat(parts) {
    let total = 0;
    for (const part of parts) total += part.length;
    const out = new Uint8Array(total);
    let at = 0;
    for (const part of parts) {
      out.set(part, at);
      at += part.length;
    }
    return out;
  }

  function u16(bytes, at) {
    return bytes[at] | (bytes[at + 1] << 8);
  }

  function u32(bytes, at) {
    return (
      (bytes[at] | (bytes[at + 1] << 8) | (bytes[at + 2] << 16)) + bytes[at + 3] * 0x1000000
    ) >>> 0;
  }

  function putU16(bytes, at, value) {
    bytes[at] = value & 0xff;
    bytes[at + 1] = (value >>> 8) & 0xff;
  }

  function putU32(bytes, at, value) {
    bytes[at] = value & 0xff;
    bytes[at + 1] = (value >>> 8) & 0xff;
    bytes[at + 2] = (value >>> 16) & 0xff;
    bytes[at + 3] = (value >>> 24) & 0xff;
  }

  const CRC_TABLE = (() => {
    const table = new Uint32Array(256);
    for (let n = 0; n < 256; n += 1) {
      let value = n;
      for (let bit = 0; bit < 8; bit += 1) {
        value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
      }
      table[n] = value >>> 0;
    }
    return table;
  })();

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (let at = 0; at < bytes.length; at += 1) {
      crc = CRC_TABLE[(crc ^ bytes[at]) & 0xff] ^ (crc >>> 8);
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function dosDateTime(when) {
    const stamp = when instanceof Date && !Number.isNaN(when.getTime()) ? when : new Date();
    const year = Math.min(2107, Math.max(1980, stamp.getFullYear()));
    return {
      time:
        ((stamp.getHours() & 31) << 11)
        | ((stamp.getMinutes() & 63) << 5)
        | ((stamp.getSeconds() >> 1) & 31),
      date:
        (((year - 1980) & 127) << 9)
        | (((stamp.getMonth() + 1) & 15) << 5)
        | (stamp.getDate() & 31),
    };
  }

  // `limit` is how many bytes the caller has already agreed to hold.  It is
  // weighed against what the stream actually hands over, chunk by chunk, so a
  // packed entry that claims to be small can never expand into the whole of
  // memory before anyone gets to check its claim.
  async function streamThrough(bytes, transform, limit = Infinity) {
    const reader = new Blob([bytes]).stream().pipeThrough(transform).getReader();
    const chunks = [];
    let produced = 0;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      produced += value.length;
      if (produced > limit) {
        await reader.cancel().catch(() => {});
        throw refuse("entry is not the size it claims");
      }
      chunks.push(value);
    }
    return concat(chunks);
  }

  const canDeflate = () => typeof CompressionStream === "function";

  async function deflateRaw(bytes) {
    return streamThrough(bytes, new CompressionStream("deflate-raw"));
  }

  async function inflateRaw(bytes, limit) {
    if (typeof DecompressionStream !== "function") {
      throw refuse("this browser cannot expand a packed entry");
    }
    try {
      return await streamThrough(bytes, new DecompressionStream("deflate-raw"), limit);
    } catch (error) {
      if (error instanceof ProjectFileError) throw error;
      throw refuse(`entry will not expand: ${error?.message || error}`);
    }
  }

  async function sha256Hex(bytes) {
    const subtle = globalThis.crypto?.subtle;
    if (!subtle) return null;
    const digest = await subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join(
      "",
    );
  }

  // ---------------------------------------------------------------- archive

  async function zipWrite(entries, { now = new Date() } = {}) {
    const rows = Array.from(entries || []);
    if (rows.length > 0xffff) throw new Error("Clayline project: too many entries");
    const { time, date } = dosDateTime(now);
    const parts = [];
    const central = [];
    let offset = 0;

    for (const row of rows) {
      const name = encoder.encode(String(row.name));
      if (name.length === 0 || name.length > 0xffff) {
        throw new Error("Clayline project: unusable entry name");
      }
      const data = await asBytes(row.bytes);
      if (data.length >= 0xffffffff) throw new Error("Clayline project: entry is too large");
      const crc = crc32(data);
      let method = 0;
      let payload = data;
      if (row.compress !== false && data.length > 0 && canDeflate()) {
        const squeezed = await deflateRaw(data);
        if (squeezed.length < data.length) {
          method = 8;
          payload = squeezed;
        }
      }

      const local = new Uint8Array(30 + name.length);
      putU32(local, 0, 0x04034b50);
      putU16(local, 4, 20);
      putU16(local, 6, 0x0800); // Names are UTF-8 (general purpose bit 11).
      putU16(local, 8, method);
      putU16(local, 10, time);
      putU16(local, 12, date);
      putU32(local, 14, crc);
      putU32(local, 18, payload.length);
      putU32(local, 22, data.length);
      putU16(local, 26, name.length);
      local.set(name, 30);
      parts.push(local, payload);

      const record = new Uint8Array(46 + name.length);
      putU32(record, 0, 0x02014b50);
      putU16(record, 4, 20);
      putU16(record, 6, 20);
      putU16(record, 8, 0x0800);
      putU16(record, 10, method);
      putU16(record, 12, time);
      putU16(record, 14, date);
      putU32(record, 16, crc);
      putU32(record, 20, payload.length);
      putU32(record, 24, data.length);
      putU16(record, 28, name.length);
      putU32(record, 42, offset);
      record.set(name, 46);
      central.push(record);

      offset += local.length + payload.length;
    }

    const directoryOffset = offset;
    let directorySize = 0;
    for (const record of central) {
      parts.push(record);
      directorySize += record.length;
    }
    const end = new Uint8Array(22);
    putU32(end, 0, 0x06054b50);
    putU16(end, 8, central.length);
    putU16(end, 10, central.length);
    putU32(end, 12, directorySize);
    putU32(end, 16, directoryOffset);
    parts.push(end);
    return concat(parts);
  }

  function findEndRecord(bytes) {
    const floor = Math.max(0, bytes.length - (0xffff + 22));
    for (let at = bytes.length - 22; at >= floor; at -= 1) {
      if (u32(bytes, at) !== 0x06054b50) continue;
      if (at + 22 + u16(bytes, at + 20) === bytes.length) return at;
    }
    return -1;
  }

  async function zipRead(input) {
    const bytes = await asBytes(input);
    if (bytes.length < 22) throw refuse("far too short to be an archive");
    const end = findEndRecord(bytes);
    if (end < 0) throw refuse("no end-of-archive record");
    if (end >= 20 && u32(bytes, end - 20) === 0x07064b50) {
      throw refuse("64-bit archives are not supported");
    }

    const count = u16(bytes, end + 10);
    const directorySize = u32(bytes, end + 12);
    const directoryOffset = u32(bytes, end + 16);
    if (
      u16(bytes, end + 4) !== 0
      || u16(bytes, end + 6) !== 0
      || u16(bytes, end + 8) !== count
      || count === 0xffff
      || directorySize === 0xffffffff
      || directoryOffset === 0xffffffff
    ) {
      throw refuse("split or 64-bit archives are not supported");
    }
    if (directoryOffset + directorySize > bytes.length) throw refuse("archive is cut short");

    const rows = [];
    const byName = new Map();
    let at = directoryOffset;
    for (let index = 0; index < count; index += 1) {
      if (at + 46 > directoryOffset + directorySize) throw refuse("index runs past its end");
      if (u32(bytes, at) !== 0x02014b50) throw refuse("index entry is damaged");
      const flags = u16(bytes, at + 8);
      if (flags & 0x0001 || flags & 0x0040) throw refuse("locked archives cannot be opened");
      const nameLength = u16(bytes, at + 28);
      const extraLength = u16(bytes, at + 30);
      const commentLength = u16(bytes, at + 32);
      const next = at + 46 + nameLength + extraLength + commentLength;
      if (next > directoryOffset + directorySize) throw refuse("index entry runs past its end");
      const row = {
        name: decoder.decode(bytes.subarray(at + 46, at + 46 + nameLength)),
        method: u16(bytes, at + 10),
        crc32: u32(bytes, at + 16),
        compressed_size: u32(bytes, at + 20),
        size: u32(bytes, at + 24),
        offset: u32(bytes, at + 42),
      };
      if (row.size === 0xffffffff || row.compressed_size === 0xffffffff) {
        throw refuse("64-bit entries are not supported");
      }
      rows.push(row);
      if (!byName.has(row.name)) byName.set(row.name, row);
      at = next;
    }

    async function entryBytes(name) {
      const row = byName.get(name);
      if (!row) throw refuse(`no entry named ${name}`);
      if (row.method !== 0 && row.method !== 8) throw refuse("entry is packed an unknown way");
      const head = row.offset;
      if (head + 30 > bytes.length || u32(bytes, head) !== 0x04034b50) {
        throw refuse("entry header is damaged");
      }
      // Sizes come from the index, so a writer that used trailing sizes still
      // reads; only the data's position comes from this header, because its
      // extra field may differ from the index's.
      const start = head + 30 + u16(bytes, head + 26) + u16(bytes, head + 28);
      const stop = start + row.compressed_size;
      if (stop > bytes.length) throw refuse("entry runs past the end of the file");
      const stored = bytes.subarray(start, stop);
      // The index's size is the budget the expansion runs under, not a claim
      // checked after the fact: the size caps above are bounds only if an
      // entry cannot grow past what it says it is.
      const data = row.method === 8 ? await inflateRaw(stored, row.size) : stored;
      if (data.length !== row.size) throw refuse("entry is not the size it claims");
      if (crc32(data) !== row.crc32) throw refuse("entry does not match its checksum");
      return data;
    }

    return Object.freeze({
      names: rows.map((row) => row.name),
      has: (name) => byName.has(name),
      info: (name) => (byName.has(name) ? Object.freeze({ ...byName.get(name) }) : null),
      bytes: entryBytes,
    });
  }

  // ---------------------------------------------------------------- project

  function schemaParts(value) {
    if (typeof value !== "string") return null;
    const match = /^(.+)\.v(\d+)$/.exec(value);
    return match ? { base: match[1], version: Number(match[2]) } : null;
  }

  function checkSchema(found, expected, what) {
    if (found === expected) return;
    const a = schemaParts(found);
    const b = schemaParts(expected);
    if (a && b && a.base === b.base && a.version > b.version) {
      throw tooNew(`${what} ${found} is newer than ${expected}`);
    }
    throw refuse(`${what} ${JSON.stringify(found)} is not ${expected}`);
  }

  function plainName(path, folder) {
    if (typeof path !== "string") return null;
    const head = `${folder}/`;
    if (!path.startsWith(head)) return null;
    const name = path.slice(head.length);
    if (!name || name === "." || name === "..") return null;
    if (name.includes("/") || name.includes("\\") || name.includes("\0")) return null;
    return name;
  }

  function isoStamp(when) {
    const stamp = when instanceof Date && !Number.isNaN(when.getTime()) ? when : new Date();
    return `${stamp.toISOString().slice(0, 19)}Z`;
  }

  async function write({
    mode,
    settings,
    state = {},
    sources = [],
    references = [],
    savedWith = null,
    savedAt = null,
  } = {}) {
    if (mode !== "draw" && mode !== "weave") {
      throw new Error(`Clayline project: unknown mode ${JSON.stringify(mode)}`);
    }
    if (!settings || typeof settings !== "object" || Array.isArray(settings)) {
      throw new Error("Clayline project: settings snapshot is missing");
    }
    if (settings.schema !== SETTINGS_SCHEMA[mode]) {
      throw new Error(
        `Clayline project: ${mode} settings must be ${SETTINGS_SCHEMA[mode]}, `
        + `not ${JSON.stringify(settings.schema)}`,
      );
    }

    const entries = [];
    const sourceRows = [];
    for (const source of sources || []) {
      const name = String(source?.name || "").trim();
      if (!name || name.includes("/") || name.includes("\\") || name === "." || name === "..") {
        throw new Error(`Clayline project: unusable source name ${JSON.stringify(source?.name)}`);
      }
      const data = await asBytes(source.bytes ?? source.data ?? source.file);
      const path = `${SOURCE_FOLDER}/${name}`;
      entries.push({ name: path, bytes: data });
      const row = { path, name, size: data.length };
      const digest = source.sha256 || (await sha256Hex(data));
      if (digest) row.sha256 = digest;
      sourceRows.push(row);
    }

    const referenceRows = [];
    for (const reference of references || []) {
      const imageId = String(reference?.image_id || "");
      if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(imageId)) {
        throw new Error(`Clayline project: unusable photo id ${JSON.stringify(imageId)}`);
      }
      const mediaType = String(reference?.media_type || "");
      const extension = referenceExtension(mediaType);
      if (!extension) {
        throw new Error(`Clayline project: unsupported photo kind ${JSON.stringify(mediaType)}`);
      }
      const data = await asBytes(reference.bytes ?? reference.data ?? reference.blob);
      const path = `${REFERENCE_FOLDER}/${imageId}.${extension}`;
      // Photos are already compressed; packing them again only costs time.
      entries.push({ name: path, bytes: data, compress: false });
      referenceRows.push({ path, image_id: imageId, media_type: mediaType, size: data.length });
    }

    const manifest = {
      schema: PROJECT_SCHEMA,
      mode,
      saved_at: isoStamp(savedAt),
      state: { sliced: Boolean(state?.sliced) },
      settings,
      sources: sourceRows,
      references: referenceRows,
    };
    if (savedWith) manifest.saved_with = String(savedWith);

    entries.unshift({ name: MANIFEST_NAME, bytes: encoder.encode(JSON.stringify(manifest)) });
    const archive = await zipWrite(entries, { now: savedAt instanceof Date ? savedAt : new Date() });
    return new Blob([archive], { type: PROJECT_MEDIA_TYPE });
  }

  async function read(input, { maxBytes = MAX_ARCHIVE_BYTES } = {}) {
    const bytes = await asBytes(input);
    if (bytes.length > maxBytes) {
      throw tooLarge(`${bytes.length} bytes is over the ${maxBytes} byte bound`);
    }

    const archive = await zipRead(bytes);
    const manifestInfo = archive.info(MANIFEST_NAME);
    if (!manifestInfo) throw refuse("no project.json inside");
    if (manifestInfo.size > MAX_MANIFEST_BYTES) {
      throw tooLarge(`project.json is ${manifestInfo.size} bytes`);
    }

    let manifest = null;
    try {
      manifest = JSON.parse(decoder.decode(await archive.bytes(MANIFEST_NAME)));
    } catch (error) {
      if (error instanceof ProjectFileError) throw error;
      throw refuse(`project.json will not parse: ${error?.message || error}`);
    }
    if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
      throw refuse("project.json is not a record");
    }

    checkSchema(manifest.schema, PROJECT_SCHEMA, "project schema");
    const mode = manifest.mode;
    if (mode !== "draw" && mode !== "weave") {
      throw refuse(`unknown mode ${JSON.stringify(mode)}`);
    }
    const settings = manifest.settings;
    if (!settings || typeof settings !== "object" || Array.isArray(settings)) {
      throw refuse("settings are missing");
    }
    checkSchema(settings.schema, SETTINGS_SCHEMA[mode], `${mode} settings schema`);

    const sourceRows = Array.isArray(manifest.sources) ? manifest.sources : [];
    const referenceRows = Array.isArray(manifest.references) ? manifest.references : [];

    let referenceBytes = 0;
    for (const row of referenceRows) {
      const name = plainName(row?.path, REFERENCE_FOLDER);
      if (!name) throw refuse(`photo path ${JSON.stringify(row?.path)} is out of place`);
      const info = archive.info(row.path);
      if (!info) throw refuse(`photo ${row.path} is missing from the file`);
      referenceBytes += info.size;
    }
    if (referenceBytes > MAX_REFERENCE_BYTES) {
      throw tooLarge(`photos are ${referenceBytes} bytes together`);
    }

    // The meshes are counted the same way the photos are, and before a single
    // one is unpacked: a small packed file can claim to hold far more than it
    // is, and the whole-file bound above only ever saw the packed bytes.
    let sourceBytes = 0;
    for (const row of sourceRows) {
      const name = plainName(row?.path, SOURCE_FOLDER);
      if (!name) throw refuse(`source path ${JSON.stringify(row?.path)} is out of place`);
      const info = archive.info(row.path);
      if (!info) throw refuse(`source ${row.path} is missing from the file`);
      sourceBytes += info.size;
    }
    if (sourceBytes > maxBytes) {
      throw tooLarge(`meshes are ${sourceBytes} bytes together`);
    }

    const sources = [];
    for (const row of sourceRows) {
      const name = plainName(row.path, SOURCE_FOLDER);
      const data = await archive.bytes(row.path);
      sources.push({
        path: row.path,
        name: typeof row.name === "string" && row.name ? row.name : name,
        size: data.length,
        sha256: typeof row.sha256 === "string" ? row.sha256 : null,
        bytes: data,
        blob: new Blob([data]),
      });
    }

    const references = [];
    for (const row of referenceRows) {
      const data = await archive.bytes(row.path);
      const mediaType = referenceExtension(row.media_type) ? row.media_type : "";
      if (!mediaType) throw refuse(`unsupported photo kind ${JSON.stringify(row?.media_type)}`);
      const imageId = String(row.image_id || "");
      if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(imageId)) {
        throw refuse(`unusable photo id ${JSON.stringify(row?.image_id)}`);
      }
      references.push({
        path: row.path,
        image_id: imageId,
        media_type: mediaType,
        size: data.length,
        bytes: data,
        blob: new Blob([data], { type: mediaType }),
      });
    }

    return {
      mode,
      settings,
      state: { sliced: Boolean(manifest.state?.sliced) },
      saved_at: typeof manifest.saved_at === "string" ? manifest.saved_at : null,
      saved_with: typeof manifest.saved_with === "string" ? manifest.saved_with : null,
      sources,
      references,
    };
  }

  return Object.freeze({
    PROJECT_SCHEMA,
    PROJECT_MEDIA_TYPE,
    SETTINGS_SCHEMA,
    MESSAGES,
    MAX_ARCHIVE_BYTES,
    MAX_MANIFEST_BYTES,
    MAX_REFERENCE_BYTES,
    ProjectFileError,
    write,
    read,
    zip: Object.freeze({ write: zipWrite, read: zipRead }),
  });
});
