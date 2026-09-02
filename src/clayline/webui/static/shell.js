"use strict";

// Shared studio shell: the global mm/in display toggle and the collapsible
// inspection panels (interface charter, 2026-07-19). The engine, payloads,
// and G-code are millimeters forever; units are a display-layer contract.
(() => {
  const IN = 25.4;
  const UNIT_KEY = "clayline-units";
  const PANEL_KEY = "clayline-inspector";
  const listeners = new Set();
  let current = "mm";
  try {
    current = window.localStorage.getItem(UNIT_KEY) === "in" ? "in" : "mm";
  } catch {
    current = "mm";
  }

  function roundDisplay(value) {
    if (!Number.isFinite(value)) return value;
    return current === "in"
      ? Math.round(value * 1000) / 1000
      : Math.round(value * 100) / 100;
  }

  const units = {
    get current() {
      return current;
    },
    toMm(value) {
      return current === "in" ? value * IN : value;
    },
    fromMm(value) {
      return current === "in" ? value / IN : value;
    },
    roundDisplay,
    // One formatter for every client-built dimension readout.
    fmt(mm, digits = 1) {
      if (!Number.isFinite(mm)) return "—";
      return current === "in"
        ? `${(mm / IN).toFixed(Math.max(digits, 2))} in`
        : `${mm.toFixed(digits)} mm`;
    },
    fmtBare(mm, digits = 1) {
      if (!Number.isFinite(mm)) return "—";
      return current === "in"
        ? (mm / IN).toFixed(Math.max(digits, 2))
        : mm.toFixed(digits);
    },
    label() {
      return current;
    },
    onChange(fn) {
      listeners.add(fn);
    },
  };

  function swapLabelTokens() {
    // Field labels carry their unit inline: "(mm)" <-> "(in)".
    const from = current === "in" ? "(mm)" : "(in)";
    const to = current === "in" ? "(in)" : "(mm)";
    document.querySelectorAll("label.field > span, .compact-field > span").forEach((span) => {
      span.childNodes.forEach((node) => {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.includes(from)) {
          node.textContent = node.textContent.replaceAll(from, to);
        }
      });
    });
  }

  function convertInputs(previous) {
    document.querySelectorAll('input[data-unit="mm"]').forEach((input) => {
      const raw = Number(input.value);
      if (input.value !== "" && Number.isFinite(raw)) {
        const mm = previous === "in" ? raw * IN : raw;
        input.value = String(roundDisplay(current === "in" ? mm / IN : mm));
      }
      if (input.dataset.mmStep === undefined && input.step) input.dataset.mmStep = input.step;
      if (input.dataset.mmMin === undefined && input.min) input.dataset.mmMin = input.min;
      if (current === "in") {
        input.step = "any";
        if (input.dataset.mmMin) input.min = String(Number(input.dataset.mmMin) / IN);
      } else {
        if (input.dataset.mmStep) input.step = input.dataset.mmStep;
        if (input.dataset.mmMin) input.min = input.dataset.mmMin;
      }
    });
  }

  function setUnit(next) {
    const normalized = next === "in" ? "in" : "mm";
    if (normalized === current) return;
    const previous = current;
    current = normalized;
    try {
      window.localStorage.setItem(UNIT_KEY, current);
    } catch {
      // Private-mode storage failures never break the studio.
    }
    convertInputs(previous);
    swapLabelTokens();
    syncToggle();
    listeners.forEach((fn) => fn(current));
  }

  function syncToggle() {
    document.querySelectorAll("[data-unit-choice]").forEach((button) => {
      const active = button.dataset.unitChoice === current;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function initToggle() {
    document.querySelectorAll("[data-unit-choice]").forEach((button) => {
      button.addEventListener("click", () => setUnit(button.dataset.unitChoice));
    });
    syncToggle();
    if (current === "in") {
      convertInputs("mm");
      swapLabelTokens();
    }
  }

  // --- collapsible inspection panels -------------------------------------
  function initInspectors() {
    let collapsed = false;
    try {
      collapsed = window.localStorage.getItem(PANEL_KEY) === "collapsed";
    } catch {
      collapsed = false;
    }
    const apply = () => {
      document.querySelectorAll(".workspace").forEach((workspace) => {
        workspace.classList.toggle("inspector-collapsed", collapsed);
      });
      document.querySelectorAll("[data-inspector-toggle]").forEach((button) => {
        button.setAttribute("aria-expanded", String(!collapsed));
        button.title = collapsed
          ? "Show the Before-you-print panel"
          : "Tuck the panel away — the warning count stays visible";
      });
    };
    document.addEventListener("click", (event) => {
      const toggle = event.target.closest?.("[data-inspector-toggle]");
      if (!toggle) return;
      collapsed = !collapsed;
      try {
        window.localStorage.setItem(PANEL_KEY, collapsed ? "collapsed" : "open");
      } catch {
        // ignore
      }
      apply();
    });
    apply();
  }

  window.claylineUnits = Object.freeze(units);
  document.addEventListener("DOMContentLoaded", () => {
    initToggle();
    initInspectors();
  });
})();
