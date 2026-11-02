"use strict";

// Settings stay in their existing controls. These editors send the same single
// gesture as a slider, so preview, automatic defaults and Undo share one path.
(() => {
  const editors = new Map();
  const dimensionIds = new Set(["flattenTol", "drawSmooth", "weaveAmplitude"]);
  const precise = (value) => String(Number(Number(value).toPrecision(12)));
  const units = () => window.claylineUnits;

  function dimension(range) {
    return range.dataset.unit === "mm" || dimensionIds.has(range.id)
      || range.dataset.imageKey === "amplitude";
  }

  function displayed(range, value) {
    return dimension(range) && range.dataset.unit !== "mm" ? units().fromMm(value) : value;
  }

  function stored(range, value) {
    return dimension(range) && range.dataset.unit !== "mm" ? units().toMm(value) : value;
  }

  function suffix(range) {
    if (dimension(range)) return units().label();
    if (range.id === "weaveTwist") return `cycles · ${precise(Number(range.value) * 360)}°`;
    if (range.dataset.imageKey === "rotation_deg") return "°";
    if (range.id === "drawArrangeFade") return "%";
    if (/follow|coves|lobes/i.test(range.id + (range.dataset.imageKey || ""))) return "(0 = unchanged)";
    return "×";
  }

  function syncEditor(range) {
    const entry = editors.get(range);
    if (!entry) return;
    entry.input.disabled = range.disabled;
    entry.unit.textContent = suffix(range);
    if (document.activeElement !== entry.input || !entry.editing) {
      entry.input.value = precise(displayed(range, Number(range.value)));
    }
    const min = displayed(range, Number(range.min || 0));
    const max = displayed(range, Number(range.max || 100));
    entry.input.title = `Type a value from ${precise(min)} to ${precise(max)} ${suffix(range)}`;
  }

  function attachEditor(range) {
    if (editors.has(range)) return;
    const label = range.closest("label");
    if (!label) return;
    const name = (label.querySelector("span")?.childNodes[0]?.textContent || "Value").trim();
    const readout = label.querySelector("output");
    const row = document.createElement("span");
    row.className = "slider-value-editor";
    const input = document.createElement("input");
    input.type = "text";
    input.inputMode = "decimal";
    input.className = "slider-number";
    input.id = `${range.id || `image-${range.dataset.imageKey}`}-value`;
    input.setAttribute("aria-label", `${name} value`);
    input.dataset.sliderFor = range.id || range.dataset.imageKey;
    const unit = document.createElement("small");
    const error = document.createElement("small");
    error.id = `${input.id}-error`;
    error.className = "slider-value-error";
    error.hidden = true;
    error.setAttribute("role", "status");
    input.setAttribute("aria-describedby", error.id);
    row.append(input, unit);
    if (readout) {
      readout.classList.add("slider-original-output");
      readout.before(row);
    } else {
      (label.querySelector("span") || label).append(row);
    }
    label.append(error);
    // The thumb remains continuous; its old increment is retained for keyboard
    // nudging. A browser range with step=.1 otherwise destroys typed 2.35.
    const dragStep = range.step;
    const integer = range.id === "drawArrangeFade";
    if (!integer) range.step = "any";
    const entry = { input, unit, editing: false };
    editors.set(range, entry);
    const clearError = () => {
      error.hidden = true;
      input.removeAttribute("aria-invalid");
    };
    const commit = () => {
      if (entry.committing) return;
      const raw = input.value.trim();
      const validNumber = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(raw);
      const value = stored(range, Number(raw));
      const min = Number(range.min || 0);
      const max = Number(range.max || 100);
      if (!validNumber || !Number.isFinite(value) || value < min || value > max
          || (integer && !Number.isInteger(value))) {
        input.setAttribute("aria-invalid", "true");
        error.textContent = `Use ${integer ? "a whole number" : "a number"} from ${precise(displayed(range, min))} to ${precise(displayed(range, max))} ${suffix(range)}.`;
        error.hidden = false;
        return;
      }
      clearError();
      entry.editing = false;
      if (range.disabled || value === Number(range.value)) return;
      // The studio leaves focused fields on pointerdown. Its blur lands back
      // here, so guard the gesture against applying an action slider twice.
      entry.committing = true;
      try {
        range.dispatchEvent(new Event("pointerdown", { bubbles: true }));
        range.value = String(value);
        range.dispatchEvent(new Event("input", { bubbles: true }));
        range.dispatchEvent(new Event("change", { bubbles: true }));
        range.dispatchEvent(new Event("pointerup", { bubbles: true }));
        // Action sliders such as Smooth return to zero after committing.
        input.value = precise(displayed(range, Number(range.value)));
      } finally {
        entry.committing = false;
      }
    };
    input.addEventListener("focus", () => { clearError(); entry.editing = false; input.select(); });
    input.addEventListener("input", () => { entry.editing = true; });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") { event.preventDefault(); commit(); }
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        clearError();
        entry.editing = false;
        input.value = precise(displayed(range, Number(range.value)));
        input.blur();
      }
    });
    input.addEventListener("blur", commit);
    range.addEventListener("keydown", (event) => {
      if (integer || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
      event.preventDefault();
      const direction = ["ArrowRight", "ArrowUp"].includes(event.key) ? 1 : -1;
      const step = Number(dragStep) || 0.1;
      range.value = String(Math.max(Number(range.min), Math.min(Number(range.max), Number(range.value) + direction * step)));
      range.dispatchEvent(new Event("input", { bubbles: true }));
      range.dispatchEvent(new Event("change", { bubbles: true }));
    });
    ["input", "change"].forEach((event) => range.addEventListener(event, () => syncEditor(range)));
    const observer = new MutationObserver(() => syncEditor(range));
    observer.observe(range, { attributes: true, attributeFilter: ["disabled", "min", "max", "value"] });
    if (readout) observer.observe(readout, { childList: true, characterData: true, subtree: true });
    syncEditor(range);
  }

  const panels = [];
  const text = (selector) => document.querySelector(selector)?.textContent.trim() || "";
  const value = (selector) => document.querySelector(selector)?.value || "";
  function summary(key, mode) {
    if (mode === "tiles") {
      return ({ design: text("#fileSummary"), passes: text("#stackCaption"),
        layers: `${value("#layerHeight")} ${units().label()} layers`, path: "Curves and joins",
        character: "Coil shaping", printer: value("#profile") })[key] || "";
    }
    if (key === "form") return text("#weaveModelName") || text("#weavePreviewTitle");
    if (key === "printer") return `${value("#weaveNozzle")} mm nozzle · ${value("#weaveLayerHeight")} ${units().label()} layers`;
    if (key === "wall") return document.querySelector("#weaveZBlend")?.checked ? "Vase mode" : "Layer by layer";
    if (key === "pattern") {
      const active = [...document.querySelectorAll("[data-weave-tab]")].filter((tab) => !tab.classList.contains("is-off")).length;
      return `${active} active · ${text("#weaveWaveState") || "Wave shape, depth and rhythm"}`;
    }
    if (key === "images") return document.querySelector("#weaveImageControls")?.hidden
      ? "No images" : `${text("#weaveImageSourceName")} · ${text("#weaveImageFit")}`;
    if (key === "inside") return `${document.querySelector('input[name="weaveInterior"]:checked')?.value || "Hollow"} · ${value("#weaveBottomLayers")} bottom layers`;
    if (key === "print") return text("#weaveRangeReadout");
    return "";
  }

  function initAccordions() {
    document.querySelectorAll(".rail-section").forEach((section, index) => {
      const body = section.querySelector(":scope > .section-body");
      const heading = body?.querySelector("h2");
      if (!body || !heading) return;
      const mode = section.closest("[data-mode-panel]").dataset.modePanel;
      const key = section.dataset.weaveSection || section.dataset.section;
      const storageKey = `clayline.palette.${mode}.${key}`;
      const content = document.createElement("div");
      content.id = `palette-content-${index}`;
      content.className = "palette-content";
      // Images has a title row with an Add button: the button belongs inside
      // its panel, outside the accordion heading's own button.
      heading.remove();
      while (body.firstChild) content.append(body.firstChild);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "palette-toggle";
      button.setAttribute("aria-controls", content.id);
      const title = document.createElement("strong");
      title.textContent = key === "pattern" ? "Weaves" : heading.textContent;
      button.setAttribute("aria-label", title.textContent);
      const description = document.createElement("small");
      description.className = "palette-summary";
      button.append(title, description);
      heading.replaceChildren(button);
      body.append(heading, content);
      let open = key === "form" || key === "design";
      try {
        const saved = localStorage.getItem(storageKey);
        if (saved !== null) open = saved === "open";
      } catch { /* Local layout preferences are optional. */ }
      const apply = (next) => {
        open = next;
        content.hidden = !open;
        section.classList.toggle("palette-closed", !open);
        button.setAttribute("aria-expanded", String(open));
        if (open) requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
      };
      button.addEventListener("click", () => {
        apply(!open);
        try { localStorage.setItem(storageKey, open ? "open" : "closed"); } catch { /* Optional. */ }
      });
      panels.push({ section, description, key, mode, reveal: () => apply(true) });
      apply(open);
    });
    // Warning links often call focus() or scrollIntoView() directly. Reveal
    // their containing panels before the browser tries to focus a hidden field.
    const reveal = (target) => {
      panels.forEach((panel) => { if (panel.section.contains(target)) panel.reveal(); });
      let parent = target.parentElement;
      while (parent) {
        if (parent.tagName === "DETAILS") parent.open = true;
        parent = parent.parentElement;
      }
    };
    window.claylinePalette = Object.freeze({ reveal });
    ["focus", "scrollIntoView"].forEach((method) => {
      const prototype = method === "focus" ? HTMLElement.prototype : Element.prototype;
      const original = prototype[method];
      prototype[method] = function (...args) { reveal(this); return original.apply(this, args); };
    });
    const refresh = () => panels.forEach((panel) => {
      const next = summary(panel.key, panel.mode);
      if (panel.description.textContent !== next) panel.description.textContent = next;
      panel.description.title = next;
    });
    document.addEventListener("input", refresh);
    document.addEventListener("change", refresh);
    // Server responses and restored projects also change summaries.
    const observer = new MutationObserver(refresh);
    document.querySelectorAll(".parameter-rail, #weavePreviewTitle").forEach((rail) => {
      observer.observe(rail, { childList: true, characterData: true, subtree: true });
    });
    refresh();
  }

  document.addEventListener("DOMContentLoaded", () => {
    initAccordions();
    document.querySelectorAll('input[type="range"]').forEach(attachEditor);
    units().onChange(() => editors.forEach((_, range) => syncEditor(range)));
  });
})();
