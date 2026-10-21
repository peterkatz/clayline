// Runs the studio's Weave page under node for tests/weave_page_rig.py.
//
// weave.js runs whole, as the page runs it, in a small stand-in for the browser
// document built from index.html. Every request it makes is written to stdout
// as one "@@REQ" line and answered on stdin by the studio app in the test's
// process; the test's script runs once the page has loaded, and what it puts
// in `out` comes back as one "@@OUT" line. Nothing here is the app.
"use strict";
const fs = require("node:fs");
const readline = require("node:readline");
const vm = require("node:vm");
const { webcrypto } = require("node:crypto");

const TREE = JSON.parse(fs.readFileSync(process.env.CLAYLINE_PAGE_TREE, "utf8"));
const WEAVE_SOURCE = fs.readFileSync(process.env.CLAYLINE_PAGE_WEAVE, "utf8");
const STATIC = process.env.CLAYLINE_PAGE_STATIC;

// ---------------------------------------------------------------- clock
const clock = { now: 0, timers: [], id: 0 };
const fakeSetTimeout = (callback, wait = 0, ...args) => {
  clock.id += 1;
  clock.timers.push({ id: clock.id, at: clock.now + Math.max(0, Number(wait) || 0), seq: clock.id, callback: () => callback(...args) });
  return clock.id;
};
const fakeClearTimeout = (id) => { clock.timers = clock.timers.filter((timer) => timer.id !== id); };
const fakeSetInterval = () => 0;
const fakeClearInterval = () => {};

// ---------------------------------------------------------------- events
class FakeEvent {
  constructor(type, init = {}) {
    this.type = type;
    this.bubbles = Boolean(init.bubbles);
    this.defaultPrevented = false;
    this.isTrusted = false;
    this.target = null;
    this.currentTarget = null;
    Object.keys(init).forEach((key) => { if (!(key in this)) this[key] = init[key]; });
  }
  preventDefault() { this.defaultPrevented = true; }
  stopPropagation() { this.stopped = true; }
  stopImmediatePropagation() { this.stopped = true; }
}

class Listeners {
  constructor() { this.byType = new Map(); }
  add(type, fn) { if (!this.byType.has(type)) this.byType.set(type, []); this.byType.get(type).push(fn); }
  remove(type, fn) { const list = this.byType.get(type) || []; const at = list.indexOf(fn); if (at >= 0) list.splice(at, 1); }
  run(target, event) {
    (this.byType.get(event.type) || []).slice().forEach((fn) => {
      event.currentTarget = target;
      if (typeof fn === "function") fn.call(target, event); else fn?.handleEvent?.(event);
    });
  }
}

// ---------------------------------------------------------------- nodes
class FakeText {
  constructor(text) { this.nodeType = 3; this.data = String(text); this.parentNode = null; }
  get textContent() { return this.data; }
  set textContent(value) { this.data = String(value); }
  cloneNode() { return new FakeText(this.data); }
  remove() { if (this.parentNode) this.parentNode._removeChild(this); }
}

const decimalsOf = (value) => {
  const text = String(value);
  if (/e-/i.test(text)) return Number(text.split(/e-/i)[1]) || 0;
  const dot = text.indexOf(".");
  return dot < 0 ? 0 : text.length - dot - 1;
};
const VALID_FLOAT = /^-?(\d+(\.\d+)?|\.\d+)([eE][-+]?\d+)?$/;

class FakeElement {
  constructor(tag, attrs = {}) {
    this.nodeType = 1;
    this.localName = tag.toLowerCase();
    this.tagName = tag.toUpperCase();
    this.nodeName = this.tagName;
    this.attrs = new Map(Object.entries(attrs));
    this.childNodes = [];
    this.parentNode = null;
    this.listeners = new Listeners();
    this.style = {};
    this.scrollTop = 0;
    this.scrollLeft = 0;
    this._checked = this.attrs.has("checked");
    this._selected = this.attrs.has("selected");
    this._value = null;
    this.files = null;
    const element = this;
    this.classList = {
      _list() { return (element.getAttribute("class") || "").split(/\s+/).filter(Boolean); },
      _set(list) { element.setAttribute("class", list.join(" ")); },
      contains(name) { return this._list().includes(name); },
      add(...names) { const list = this._list(); names.forEach((name) => { if (!list.includes(name)) list.push(name); }); this._set(list); },
      remove(...names) { this._set(this._list().filter((name) => !names.includes(name))); },
      toggle(name, force) {
        const has = this._list().includes(name);
        const want = force === undefined ? !has : Boolean(force);
        if (want && !has) this.add(name); else if (!want && has) this.remove(name);
        return want;
      },
    };
    this.dataset = new Proxy({}, {
      get(_target, key) {
        if (typeof key !== "string") return undefined;
        const name = `data-${key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`;
        return element.attrs.has(name) ? element.attrs.get(name) : undefined;
      },
      set(_target, key, value) {
        element.setAttribute(`data-${String(key).replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`, String(value));
        return true;
      },
      deleteProperty(_target, key) {
        element.removeAttribute(`data-${String(key).replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`);
        return true;
      },
      has(_target, key) {
        return element.attrs.has(`data-${String(key).replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`);
      },
    });
    if (this.localName === "canvas") {
      this._context = new Proxy({}, {
        get(target, key) {
          if (key in target) return target[key];
          if (key === "measureText") return () => ({ width: 10 });
          if (key === "createLinearGradient" || key === "createRadialGradient") return () => ({ addColorStop() {} });
          if (key === "getImageData") return () => ({ data: new Uint8ClampedArray(4) });
          return () => {};
        },
        set(target, key, value) { target[key] = value; return true; },
      });
    }
  }

  // --- attributes
  getAttribute(name) { return this.attrs.has(name) ? this.attrs.get(name) : null; }
  setAttribute(name, value) { this.attrs.set(name, String(value)); }
  hasAttribute(name) { return this.attrs.has(name); }
  removeAttribute(name) { this.attrs.delete(name); }
  toggleAttribute(name, force) {
    const want = force === undefined ? !this.attrs.has(name) : Boolean(force);
    if (want) this.attrs.set(name, ""); else this.attrs.delete(name);
    return want;
  }
  get id() { return this.getAttribute("id") || ""; }
  set id(value) { this.setAttribute("id", value); }
  get className() { return this.getAttribute("class") || ""; }
  set className(value) { this.setAttribute("class", value); }
  get title() { return this.getAttribute("title") || ""; }
  set title(value) { this.setAttribute("title", value); }
  get hidden() { return this.attrs.has("hidden"); }
  set hidden(value) { this.toggleAttribute("hidden", Boolean(value)); }
  get disabled() { return this.attrs.has("disabled"); }
  set disabled(value) { this.toggleAttribute("disabled", Boolean(value)); }
  get type() { return (this.getAttribute("type") || (this.localName === "button" ? "submit" : "text")).toLowerCase(); }
  set type(value) { this.setAttribute("type", value); }
  get name() { return this.getAttribute("name") || ""; }
  set name(value) { this.setAttribute("name", value); }
  get placeholder() { return this.getAttribute("placeholder") || ""; }
  set placeholder(value) { this.setAttribute("placeholder", value); }
  get min() { return this.getAttribute("min") || ""; }
  set min(value) { this.setAttribute("min", value); }
  get max() { return this.getAttribute("max") || ""; }
  set max(value) { this.setAttribute("max", value); }
  get step() { return this.getAttribute("step") || ""; }
  set step(value) { this.setAttribute("step", value); }
  get href() { return this.getAttribute("href") || ""; }
  set href(value) { this.setAttribute("href", value); }
  get download() { return this.getAttribute("download") || ""; }
  set download(value) { this.setAttribute("download", value); }
  get width() { return Number(this.getAttribute("width") || 300); }
  set width(value) { this.setAttribute("width", value); }
  get height() { return Number(this.getAttribute("height") || 150); }
  set height(value) { this.setAttribute("height", value); }
  get open() { return this.attrs.has("open"); }
  set open(value) { this.toggleAttribute("open", Boolean(value)); }

  // --- form state, held the way a browser holds it
  _sanitize(raw) {
    const text = raw === null || raw === undefined ? "" : String(raw);
    if (this.localName !== "input") return text;
    if (this.type === "range") {
      const min = this.attrs.has("min") ? Number(this.getAttribute("min")) : 0;
      const max = this.attrs.has("max") ? Number(this.getAttribute("max")) : 100;
      const stepText = this.getAttribute("step");
      const step = stepText === "any" ? null : Number(stepText || 1);
      let value = Number(text);
      if (text.trim() === "" || !Number.isFinite(value)) value = max < min ? min : min + (max - min) / 2;
      value = Math.min(Math.max(value, min), Math.max(min, max));
      if (step) {
        const places = Math.max(decimalsOf(step), decimalsOf(min));
        const count = Math.round((value - min) / step);
        let snapped = Number((min + count * step).toFixed(places));
        if (snapped > max) snapped = Number((min + (count - 1) * step).toFixed(places));
        value = snapped;
      }
      return String(value);
    }
    if (this.type === "number") return VALID_FLOAT.test(text.trim()) ? text.trim() : "";
    return text;
  }
  get value() {
    if (this.localName === "select") {
      const option = this.options.find((item) => item._selected) || this.options[0];
      return option ? option.value : "";
    }
    if (this.localName === "option") return this.attrs.has("value") ? this.getAttribute("value") : this.textContent;
    if (this.localName === "input" && ["checkbox", "radio"].includes(this.type)) {
      return this.attrs.has("value") ? this.getAttribute("value") : "on";
    }
    if (this._value === null) this._value = this._sanitize(this.getAttribute("value"));
    return this._value;
  }
  set value(raw) {
    if (this.localName === "select") {
      const text = String(raw);
      let found = false;
      this.options.forEach((option) => {
        const match = !found && option.value === text;
        option._selected = match;
        if (match) found = true;
      });
      this._noneSelected = !found;
      return;
    }
    if (this.localName === "option") { this.setAttribute("value", raw); return; }
    this._value = this._sanitize(raw);
  }
  get valueAsNumber() { return Number(this.value); }
  get options() { return this.querySelectorAll("option"); }
  get selectedIndex() { return this.options.findIndex((option) => option._selected); }
  set selectedIndex(index) { this.options.forEach((option, at) => { option._selected = at === index; }); }
  get selected() { return this._selected; }
  set selected(value) { this._selected = Boolean(value); }
  get checked() { return this._checked; }
  set checked(value) {
    this._checked = Boolean(value);
    if (this._checked && this.type === "radio" && this.name) {
      document.querySelectorAll(`input[name="${this.name}"]`).forEach((other) => {
        if (other !== this) other._checked = false;
      });
    }
  }

  // --- tree
  get children() { return this.childNodes.filter((node) => node.nodeType === 1); }
  get firstElementChild() { return this.children[0] || null; }
  get lastElementChild() { const list = this.children; return list[list.length - 1] || null; }
  get firstChild() { return this.childNodes[0] || null; }
  get parentElement() { return this.parentNode && this.parentNode.nodeType === 1 ? this.parentNode : null; }
  get childElementCount() { return this.children.length; }
  get isConnected() { let node = this; while (node.parentNode) node = node.parentNode; return node === document.documentElement || node === document; }
  get textContent() { return this.childNodes.map((node) => node.textContent).join(""); }
  set textContent(value) { this.replaceChildren(); if (value !== "" && value !== null && value !== undefined) this._adopt(new FakeText(value)); }
  get innerText() { return this.textContent; }
  set innerText(value) { this.textContent = value; }
  get innerHTML() { return this.textContent; }
  set innerHTML(value) { this.textContent = value; }
  _node(value) { return value && (value.nodeType === 1 || value.nodeType === 3) ? value : new FakeText(value); }
  _adopt(node, before = null) {
    if (node.parentNode) node.parentNode._removeChild(node);
    node.parentNode = this;
    const at = before ? this.childNodes.indexOf(before) : -1;
    if (at >= 0) this.childNodes.splice(at, 0, node); else this.childNodes.push(node);
    return node;
  }
  _removeChild(node) { const at = this.childNodes.indexOf(node); if (at >= 0) this.childNodes.splice(at, 1); node.parentNode = null; }
  append(...nodes) { nodes.forEach((node) => this._adopt(this._node(node))); }
  prepend(...nodes) { const first = this.childNodes[0] || null; nodes.forEach((node) => this._adopt(this._node(node), first)); }
  appendChild(node) { return this._adopt(node); }
  insertBefore(node, before) { return this._adopt(node, before); }
  removeChild(node) { this._removeChild(node); return node; }
  replaceChildren(...nodes) { this.childNodes.slice().forEach((node) => this._removeChild(node)); this.append(...nodes); }
  remove() { if (this.parentNode) this.parentNode._removeChild(this); }
  contains(node) { while (node) { if (node === this) return true; node = node.parentNode; } return false; }
  cloneNode(deep = false) {
    const copy = new FakeElement(this.localName, Object.fromEntries(this.attrs));
    if (this._value !== null) copy._value = null;
    if (deep) this.childNodes.forEach((node) => copy.append(node.cloneNode(true)));
    return copy;
  }
  _descendants() {
    const out = [];
    const walk = (node) => node.children.forEach((child) => { out.push(child); walk(child); });
    walk(this);
    return out;
  }
  querySelectorAll(selector) { return this._descendants().filter((node) => matches(node, selector)); }
  querySelector(selector) { return this._descendants().find((node) => matches(node, selector)) || null; }
  matches(selector) { return matches(this, selector); }
  closest(selector) { let node = this; while (node && node.nodeType === 1) { if (matches(node, selector)) return node; node = node.parentNode; } return null; }

  // --- events and the rest of an element
  addEventListener(type, fn) { this.listeners.add(type, fn); }
  removeEventListener(type, fn) { this.listeners.remove(type, fn); }
  dispatchEvent(event) {
    event.target = event.target || this;
    this.listeners.run(this, event);
    if (event.bubbles && !event.stopped) {
      let node = this.parentNode;
      while (node && !event.stopped) {
        node.listeners?.run(node, event);
        node = node.parentNode;
      }
      if (!event.stopped) windowListeners.run(globalThis, event);
    }
    return !event.defaultPrevented;
  }
  click() {
    if (this.disabled) return;
    if (this.localName === "input" && this.type === "checkbox") this.checked = !this.checked;
    if (this.localName === "input" && this.type === "radio") this.checked = true;
    this.dispatchEvent(new FakeEvent("click", { bubbles: true }));
    if (this.localName === "input" && ["checkbox", "radio"].includes(this.type)) {
      this.dispatchEvent(new FakeEvent("input", { bubbles: true }));
      this.dispatchEvent(new FakeEvent("change", { bubbles: true }));
    }
  }
  focus() {
    const previous = document.activeElement;
    if (previous === this) return;
    if (previous && previous !== document.body) previous.dispatchEvent(new FakeEvent("blur"));
    document.activeElement = this;
    this.dispatchEvent(new FakeEvent("focus"));
  }
  blur() {
    if (document.activeElement !== this) return;
    document.activeElement = document.body;
    this.dispatchEvent(new FakeEvent("blur"));
  }
  getContext() { return this._context || null; }
  getBoundingClientRect() { return { left: 0, top: 0, right: this.width, bottom: this.height, x: 0, y: 0, width: this.width, height: this.height }; }
  get clientWidth() { return this.width; }
  get clientHeight() { return this.height; }
  get offsetWidth() { return this.width; }
  get offsetHeight() { return this.height; }
  scrollIntoView() {}
  scrollTo() {}
  setPointerCapture() {}
  releasePointerCapture() {}
  hasPointerCapture() { return false; }
  toDataURL() { return "data:image/png;base64,"; }
  showModal() { this.open = true; }
  close() { this.open = false; }
}

class FakeInputElement extends FakeElement {}

// ---------------------------------------------------------------- selectors
function splitTop(text, separator) {
  const parts = [];
  let depth = 0;
  let quote = null;
  let current = "";
  for (const char of text) {
    if (quote) { if (char === quote) quote = null; current += char; continue; }
    if (char === "'" || char === '"') { quote = char; current += char; continue; }
    if (char === "[" || char === "(") depth += 1;
    if (char === "]" || char === ")") depth -= 1;
    if (depth === 0 && (separator === " " ? /\s/.test(char) : char === separator)) {
      if (current.trim()) parts.push(current.trim());
      current = "";
      continue;
    }
    current += char;
  }
  if (current.trim()) parts.push(current.trim());
  return parts;
}

const compiled = new Map();
function compound(text) {
  const tests = [];
  const pattern = /([a-zA-Z][a-zA-Z0-9-]*)|#([A-Za-z0-9_-]+)|\.([A-Za-z0-9_-]+)|\[\s*([^\]=~^$*|\s]+)\s*(?:=\s*(?:"([^"]*)"|'([^']*)'|([^\]\s]+)))?\s*\]|:(checked|disabled|not\(([^)]*)\))/g;
  let match;
  let consumed = 0;
  while ((match = pattern.exec(text))) {
    if (match.index !== consumed) throw new Error(`selector not understood: ${text}`);
    consumed = pattern.lastIndex;
    const [, tag, id, cls, attr, dq, sq, bare, pseudo, notInner] = match;
    if (tag) tests.push((node) => node.localName === tag.toLowerCase());
    else if (id) tests.push((node) => node.getAttribute("id") === id);
    else if (cls) tests.push((node) => node.classList.contains(cls));
    else if (attr) {
      const want = dq ?? sq ?? bare;
      tests.push((node) => node.attrs.has(attr) && (want === undefined || node.attrs.get(attr) === want));
    } else if (pseudo === "checked") tests.push((node) => Boolean(node._checked));
    else if (pseudo === "disabled") tests.push((node) => node.disabled);
    else if (notInner !== undefined) {
      const inner = compile(notInner);
      tests.push((node) => !inner(node));
    }
  }
  if (consumed !== text.length) throw new Error(`selector not understood: ${text}`);
  return (node) => tests.every((test) => test(node));
}

function compile(selector) {
  if (compiled.has(selector)) return compiled.get(selector);
  const groups = splitTop(selector, ",").map((group) => splitTop(group, " ").filter((part) => part !== ">").map(compound));
  const test = (node) => groups.some((chain) => {
    if (!chain[chain.length - 1](node)) return false;
    let ancestor = node.parentNode;
    for (let index = chain.length - 2; index >= 0; index -= 1) {
      while (ancestor && ancestor.nodeType === 1 && !chain[index](ancestor)) ancestor = ancestor.parentNode;
      if (!ancestor || ancestor.nodeType !== 1) return false;
      ancestor = ancestor.parentNode;
    }
    return true;
  });
  compiled.set(selector, test);
  return test;
}
function matches(node, selector) { return node.nodeType === 1 && compile(selector)(node); }

// ---------------------------------------------------------------- document
function build(item) {
  if (typeof item === "string") return new FakeText(item);
  const [tag, attrs, children] = item;
  const element = tag === "input" ? new FakeInputElement(tag, attrs) : new FakeElement(tag, attrs);
  children.forEach((child) => element._adopt(build(child)));
  return element;
}
const htmlNode = TREE[2].find((item) => Array.isArray(item) && item[0] === "html");
const documentElement = build(htmlNode || ["html", {}, TREE[2]]);
const body = documentElement.querySelector("body") || documentElement;
const windowListeners = new Listeners();
const documentListeners = new Listeners();
const document = {
  nodeType: 9,
  documentElement,
  body,
  activeElement: body,
  listeners: documentListeners,
  createElement: (tag) => (tag === "input" ? new FakeInputElement(tag) : new FakeElement(tag)),
  createTextNode: (text) => new FakeText(text),
  querySelector: (selector) => documentElement.querySelector(selector) || (matches(documentElement, selector) ? documentElement : null),
  querySelectorAll: (selector) => documentElement.querySelectorAll(selector),
  getElementById: (id) => documentElement.querySelector(`#${id}`),
  addEventListener: (type, fn) => documentListeners.add(type, fn),
  removeEventListener: (type, fn) => documentListeners.remove(type, fn),
  dispatchEvent: (event) => { event.target = event.target || document; documentListeners.run(document, event); return true; },
  hidden: false,
  visibilityState: "visible",
};
documentElement.parentNode = document;
document._removeChild = () => {};
document.nodeType = 9;

// ---------------------------------------------------------------- the server
const inflight = new Set();
const waiting = new Map();
const requests = [];
let requestId = 0;
const lines = readline.createInterface({ input: process.stdin });
lines.on("line", (line) => {
  const message = JSON.parse(line);
  const resolve = waiting.get(message.id);
  waiting.delete(message.id);
  if (resolve) resolve(message);
});

async function bodyText(body) {
  if (body === undefined || body === null) return { text: null, binary: false };
  if (typeof body === "string") return { text: body, binary: false };
  const bytes = Buffer.from(await body.arrayBuffer());
  return { text: bytes.toString("base64"), binary: true };
}

function fakeFetch(url, init = {}) {
  requestId += 1;
  const id = requestId;
  const task = (async () => {
    const { text, binary } = await bodyText(init.body);
    const request = { id, method: init.method || "GET", url: String(url), body: text, binary, headers: init.headers || {} };
    requests.push({ method: request.method, url: request.url, body: binary ? null : text });
    process.stdout.write(`@@REQ ${JSON.stringify(request)}\n`);
    const answer = await new Promise((resolve) => waiting.set(id, resolve));
    return {
      ok: answer.status >= 200 && answer.status < 300,
      status: answer.status,
      headers: { get: (name) => (answer.headers || {})[String(name).toLowerCase()] ?? null },
      json: async () => JSON.parse(answer.body),
      text: async () => answer.body,
      blob: async () => new Blob([answer.body]),
    };
  })();
  inflight.add(task);
  task.then(() => inflight.delete(task), () => inflight.delete(task));
  return task;
}

// ---------------------------------------------------------------- window
const memory = new Map();
const storage = {
  getItem: (key) => (memory.has(key) ? memory.get(key) : null),
  setItem: (key, value) => { memory.set(key, String(value)); },
  removeItem: (key) => { memory.delete(key); },
};
const unitListeners = [];
const units = {
  current: "mm",
  toMm: (value) => value,
  fromMm: (value) => value,
  roundDisplay: (value) => (Number.isFinite(value) ? Math.round(value * 100) / 100 : value),
  fmt: (mm, digits = 1) => (Number.isFinite(mm) ? `${mm.toFixed(digits)} mm` : "—"),
  fmtBare: (mm, digits = 1) => (Number.isFinite(mm) ? mm.toFixed(digits) : "—"),
  label: () => "mm",
  onChange: (fn) => unitListeners.push(fn),
};
const blobs = [];
const realUrl = URL;
class FakeUrl extends realUrl {}
FakeUrl.createObjectURL = (blob) => { blobs.push(blob); return `blob:clayline/${blobs.length}`; };
FakeUrl.revokeObjectURL = () => {};

const browserGlobals = {
  window: globalThis,
  self: globalThis,
  document,
  navigator: { userAgent: "node", platform: "MacIntel" },
  location: { href: "http://127.0.0.1/", origin: "http://127.0.0.1", protocol: "http:", search: "" },
  localStorage: storage,
  sessionStorage: storage,
  claylineUnits: units,
  fetch: fakeFetch,
  setTimeout: fakeSetTimeout,
  clearTimeout: fakeClearTimeout,
  setInterval: fakeSetInterval,
  clearInterval: fakeClearInterval,
  requestAnimationFrame: (callback) => fakeSetTimeout(() => callback(clock.now), 16),
  cancelAnimationFrame: fakeClearTimeout,
  performance: { now: () => clock.now },
  Event: FakeEvent,
  CustomEvent: FakeEvent,
  KeyboardEvent: FakeEvent,
  PointerEvent: FakeEvent,
  MouseEvent: FakeEvent,
  Element: FakeElement,
  HTMLElement: FakeElement,
  HTMLInputElement: FakeInputElement,
  Node: FakeElement,
  URL: FakeUrl,
  matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {} }),
  getComputedStyle: () => ({ getPropertyValue: () => "" }),
  addEventListener: (type, fn) => windowListeners.add(type, fn),
  removeEventListener: (type, fn) => windowListeners.remove(type, fn),
  atob: (text) => Buffer.from(text, "base64").toString("binary"),
  btoa: (text) => Buffer.from(text, "binary").toString("base64"),
};
// Some of these are getters on node's own global; each is replaced outright.
Object.entries(browserGlobals).forEach(([key, value]) => {
  Object.defineProperty(globalThis, key, { value, writable: true, configurable: true, enumerable: true });
});
if (!globalThis.crypto) globalThis.crypto = webcrypto;

// The page's own modules, loaded as the page loads them.
vm.runInThisContext(fs.readFileSync(`${STATIC}/studio-state.js`, "utf8"), { filename: "studio-state.js" });
vm.runInThisContext(fs.readFileSync(`${STATIC}/project-file.js`, "utf8"), { filename: "project-file.js" });
// weave.js itself, with one line added at its end that hands the test its
// internals. Nothing else in it changes.
const marker = "\n  initialise();\n})();";
if (!WEAVE_SOURCE.includes(marker)) throw new Error("weave.js no longer ends the way the rig expects");
const exposed = WEAVE_SOURCE.replace(
  marker,
  "\n  window.__weavePage = { S, patternObject, weaveSettingsSnapshot, validWeaveSettings,"
  + " applyWeaveSettings, settingsSnapshotFromRestore, renderPatternVisuals, renderWarnings };"
  + marker,
);
vm.runInThisContext(exposed, { filename: "weave.js" });

// ---------------------------------------------------------------- driving
async function drain() {
  for (let quiet = 0; quiet < 3;) {
    await new Promise((resolve) => setImmediate(resolve));
    if (inflight.size) {
      quiet = 0;
      await Promise.allSettled([...inflight]);
    } else {
      quiet += 1;
    }
  }
}

async function settle(ms = 0) {
  const end = clock.now + ms;
  await drain();
  for (;;) {
    const due = clock.timers
      .filter((timer) => timer.at <= end)
      .sort((a, b) => a.at - b.at || a.seq - b.seq)[0];
    if (!due) break;
    clock.timers = clock.timers.filter((timer) => timer !== due);
    clock.now = Math.max(clock.now, due.at);
    due.callback();
    await drain();
  }
  clock.now = end;
  await drain();
}

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);
function element(selector) {
  const found = typeof selector === "string" ? $(selector) : selector;
  if (!found) throw new Error(`no element ${selector}`);
  return found;
}
function click(selector) { element(selector).click(); }
function type(selector, value) {
  const control = element(selector);
  control.value = String(value);
  control.dispatchEvent(new FakeEvent("input", { bubbles: true }));
  control.dispatchEvent(new FakeEvent("change", { bubbles: true }));
}
function toggle(selector, on) {
  const control = element(selector);
  if (on === undefined || Boolean(on) !== control.checked) control.click();
}

const page = window.__weavePage;
const weaveMode = window.claylineWeaveMode;
const codec = window.ClaylineProjectFile;
const out = {};

// The test's own script, the body of an async function given the helpers.
const AsyncFunction = (async () => {}).constructor;
const script = new AsyncFunction(
  "page", "$", "$$", "click", "type", "toggle", "settle", "requests", "weaveMode", "codec", "out",
  fs.readFileSync(process.env.CLAYLINE_PAGE_SCRIPT, "utf8"),
);

(async () => {
  await settle(0);
  await script(page, $, $$, click, type, toggle, settle, requests, weaveMode, codec, out);
  // A pipe takes a long line in pieces: leave only once it is all written.
  process.stdout.write(`@@OUT ${JSON.stringify(out)}\n`, () => process.exit(0));
})().catch((error) => {
  process.stderr.write(`${error && error.stack ? error.stack : error}\n`);
  process.exit(1);
});
