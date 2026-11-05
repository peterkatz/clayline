"use strict";

// Clayline · lines from a drawing, the page's half of it.  The engine sorts a
// file and makes the lines (shape_lines.py); this holds what the page needs to
// read the result and to wait its turn, with no reach into the studio:
//
//   isConverted, marksOf, originOf
//        What a pass's own root attributes say.  They live on the drawing, so
//        they survive undo and reopen with no new pass fields.
//   originalOf, withoutOriginal
//        The file the lines were made from, kept as escaped text in <metadata>.
//        It never goes to the engine to measure or slice, and never prints.
//   answerOf, withAnswer, withoutAnswer
//        Only making lines can tell a photo, and a reopened project must not make
//        lines to find out, so that answer rides on the file's root tag.  It comes
//        off to the byte.
//   hashOf
//        A short stand-in for a whole drawing, for maps that outlive a version.
//   sentenceFor
//        A stored sentence may hold {size}, for the page to fill in its own units.
//   whereLinesMeet
//        A warning the engine raised about a line it made, at a join or a fork.
//   paintToBlob, blobToBase64
//        new Image(), then drawImage on a clear canvas.  createImageBitmap
//        refuses an SVG file.
//   createQueue
//        One drawing at a time.  Rows with the same file and settings share one
//        answer.  A job dropped while it runs lands nowhere and shares nothing.
((root, factory) => {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClaylineShapeLines = api;
})(typeof window !== "undefined" ? window : globalThis, (root) => {
  const ROOT_TAG = /<svg\b[^>]*>/;
  const ORIGINAL = /<metadata id="clayline-original">([\s\S]*?)<\/metadata>\n?/;
  const ORIGINAL_OPENS = '<metadata id="clayline-original">';
  const NO_LINES_MARK = /\sdata-clayline-no-lines="[^"]*"/;
  const LINE_ID = "from-shape-";
  const MEETING_CODES = new Set(["tight_radius", "under_spaced", "crossing", "lap", "fuse"]);

  function rootTag(svg) {
    const match = ROOT_TAG.exec(String(svg || ""));
    return match ? match[0] : "";
  }

  function unescapeAttribute(text) {
    return text.replace(/&(amp|quot|lt|gt);/g, (_all, name) => (
      name === "amp" ? "&" : name === "quot" ? '"' : name === "lt" ? "<" : ">"
    ));
  }

  function rootMark(svg, name) {
    const match = new RegExp(`\\sdata-clayline-${name}="([^"]*)"`).exec(rootTag(svg));
    return match ? unescapeAttribute(match[1]) : null;
  }

  function isConverted(svg) {
    return rootMark(svg, "converted") !== null;
  }

  function originOf(svg) {
    return rootMark(svg, "origin") || "";
  }

  function hasOriginal(svg) {
    return isConverted(svg) && String(svg).includes(ORIGINAL_OPENS);
  }

  function numberMark(svg, name) {
    const raw = rootMark(svg, name);
    if (raw === null || raw.trim() === "") return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  }

  function marksOf(svg) {
    if (!isConverted(svg)) return null;
    const box = /\sviewBox="\s*0\s+0\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s*"/.exec(rootTag(svg));
    const place = String(rootMark(svg, "place") || "").trim().split(/\s+/).map(Number);
    return {
      target: numberMark(svg, "target"),
      coil: numberMark(svg, "coil"),
      join: numberMark(svg, "join"),
      basis: rootMark(svg, "size-basis") || "",
      sentence: rootMark(svg, "sentence") || "",
      kind: rootMark(svg, "sentence-kind") || "",
      suggested: numberMark(svg, "suggested"),
      width: box ? Number(box[1]) : null,
      height: box ? Number(box[2]) : null,
      place: place.length === 6 && place.every(Number.isFinite) ? place : null,
    };
  }

  // Exactly what was added: the reader never parses it, so it can't be changed
  // by being read.  One pass over the text, so "&amp;lt;" stays "&lt;".
  function originalOf(svg) {
    if (!hasOriginal(svg)) return null;
    const match = ORIGINAL.exec(svg);
    if (!match) return null;
    return match[1].replace(/&(amp|lt|gt|#13);/g, (_all, name) => (
      name === "amp" ? "&" : name === "lt" ? "<" : name === "gt" ? ">" : "\r"
    ));
  }

  // A file sorted "leave" comes straight back as the identical string.
  function withoutOriginal(svg) {
    return hasOriginal(svg) ? svg.replace(ORIGINAL, "") : svg;
  }

  function answerOf(svg) {
    const kept = rootMark(svg, "no-lines");
    if (!kept) return null;
    try {
      const answer = JSON.parse(kept);
      return answer && typeof answer === "object" ? answer : null;
    } catch (_error) {
      return null;
    }
  }

  function withoutAnswer(svg) {
    const tag = rootTag(svg);
    const mark = NO_LINES_MARK.exec(tag);
    if (!mark) return svg;
    const at = svg.indexOf(tag) + mark.index;
    return svg.slice(0, at) + svg.slice(at + mark[0].length);
  }

  function withAnswer(svg, answer) {
    const file = withoutAnswer(svg);
    const tag = rootTag(file);
    if (!tag) return file;
    const kept = JSON.stringify(answer).replace(/[&"<>]/g, (one) => (
      one === "&" ? "&amp;" : one === '"' ? "&quot;" : one === "<" ? "&lt;" : "&gt;"
    ));
    const at = file.indexOf(tag) + "<svg".length;
    return `${file.slice(0, at)} data-clayline-no-lines="${kept}"${file.slice(at)}`;
  }

  function hashOf(text) {
    const value = String(text);
    let a = 0xdeadbeef;
    let b = 0x41c6ce57;
    for (let index = 0; index < value.length; index += 1) {
      const code = value.charCodeAt(index);
      a = Math.imul(a ^ code, 2654435761);
      b = Math.imul(b ^ code, 1597334677);
    }
    a = Math.imul(a ^ (a >>> 16), 2246822507) ^ Math.imul(b ^ (b >>> 13), 3266489909);
    b = Math.imul(b ^ (b >>> 16), 2246822507) ^ Math.imul(a ^ (a >>> 13), 3266489909);
    return `${value.length}:${(b >>> 0).toString(36)}${(a >>> 0).toString(36)}`;
  }

  function sentenceFor(sentence, suggestedMm, format) {
    const text = String(sentence || "");
    if (!text.includes("{size}")) return text;
    return Number.isFinite(suggestedMm) ? text.replace("{size}", format(suggestedMm)) : "";
  }

  function isLineId(id) {
    return typeof id === "string" && id.startsWith(LINE_ID);
  }

  function whereLinesMeet(warning) {
    return isLineId(warning?.provenance?.element_id) && MEETING_CODES.has(warning.code);
  }

  function paintToBlob(svgText, size = null, limitMs = 30000) {
    return new Promise((resolve, reject) => {
      const url = root.URL.createObjectURL(new root.Blob([svgText], { type: "image/svg+xml" }));
      const image = new root.Image();
      let settled = false;
      let timer = null;
      const finish = (settle, value) => {
        if (settled) return;
        settled = true;
        root.clearTimeout(timer);
        root.URL.revokeObjectURL(url);
        image.onload = null;
        image.onerror = null;
        settle(value);
      };
      timer = root.setTimeout(() => finish(reject, new Error("painting took too long")), limitMs);
      image.onerror = () => finish(reject, new Error("the drawing would not paint"));
      image.onload = () => {
        try {
          const longest = Math.max(image.naturalWidth, image.naturalHeight) || 1000;
          const grow = size ? 1 : 2000 / longest;
          const width = size ? size.width : Math.round((image.naturalWidth || 1000) * grow);
          const height = size ? size.height : Math.round((image.naturalHeight || 1000) * grow);
          const canvas = root.document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const context = canvas.getContext("2d");
          context.clearRect(0, 0, width, height);
          context.drawImage(image, 0, 0, width, height);
          // A tainted canvas throws here, or hands back nothing.
          canvas.toBlob((blob) => {
            if (blob) finish(resolve, blob);
            else finish(reject, new Error("the painting could not be read"));
          }, "image/png");
        } catch (error) {
          finish(reject, error);
        }
      };
      image.src = url;
    });
  }

  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new root.FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(reader.error || new Error("the painting could not be read"));
      reader.readAsDataURL(blob);
    });
  }

  function createQueue({ work, land, idle = () => {} }) {
    const waiting = [];
    let running = null;

    const pump = async () => {
      if (running) return;
      let job = waiting.shift();
      while (job && job.dropped) job = waiting.shift();
      if (!job) {
        idle();
        return;
      }
      running = job;
      let outcome;
      try {
        outcome = { answer: await work(job) };
      } catch (error) {
        outcome = { error };
      }
      running = null;
      // A job dropped on its way stops part done, so what it holds isn't an answer
      // to anyone. Those waiting on the same key run for themselves.
      const sharing = job.dropped ? [] : waiting.filter((other) => other.key === job.key);
      sharing.forEach((other) => waiting.splice(waiting.indexOf(other), 1));
      [job, ...sharing].forEach((each) => {
        if (!each.dropped) land(each, outcome);
      });
      pump();
    };

    return Object.freeze({
      add(job) {
        waiting.push(job);
        pump();
      },
      // The running job first, then the rest in the order they will run.
      jobs: () => (running ? [running, ...waiting] : [...waiting]),
    });
  }

  return Object.freeze({
    isConverted,
    hasOriginal,
    originOf,
    marksOf,
    originalOf,
    withoutOriginal,
    answerOf,
    withAnswer,
    withoutAnswer,
    hashOf,
    sentenceFor,
    isLineId,
    whereLinesMeet,
    paintToBlob,
    blobToBase64,
    createQueue,
  });
});
