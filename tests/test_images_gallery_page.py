"""Browse visual sources without changing an Image's carefully tuned settings."""

from __future__ import annotations

import json

import pytest
from weave_page_rig import run_page

IMAGE_BROWSER = """
globalThis.Image = class {
  set src(_value) { queueMicrotask(() => this.onload?.()); }
};
"""


def test_gallery_searches_names_numbers_and_paisleys_without_editing_the_pattern() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      const before = JSON.stringify(page.patternObject());
      const history = weaveMode.historyState().length;
      out.initialCards = $$("[data-image-source-id]").length;
      click("#weaveImageBrowse"); await settle(0);
      const visible = () => $$("[data-image-source-id]").filter(card => !card.hidden);
      out.open = !$("#weaveImageGalleryOverlay").hidden;
      out.all = visible().length;
      type("#weaveImageGallerySearch", "moths");
      out.moths = visible().map(card => card.dataset.imageSourceId);
      type("#weaveImageGallerySearch", "64");
      out.number = visible().map(card => card.dataset.imageSourceId);
      type("#weaveImageGallerySearch", "");
      click('[data-image-gallery-filter="paisley"]');
      out.paisleys = visible().map(card => card.dataset.imageSourceId);
      type("#weaveImageGallerySearch", "no matching motif");
      out.empty = visible().length;
      out.emptyMessage = $("#weaveImageGalleryStatus").textContent;
      click("#weaveImageGalleryClose"); await settle(0);
      out.closed = $("#weaveImageGalleryOverlay").hidden;
      out.unchanged = before === JSON.stringify(page.patternObject());
      out.historyUnchanged = history === weaveMode.historyState().length;
      out.focus = document.activeElement?.id;
    """
    )
    assert result["initialCards"] == 0
    assert result["open"] and result["all"] == 80
    assert result["moths"] == ["48-night-moths"]
    assert result["number"] == ["64-marigold-vine"]
    assert len(result["paisleys"]) == 20
    assert all(61 <= int(source[:2]) <= 80 for source in result["paisleys"])
    assert result["empty"] == 0 and result["emptyMessage"]
    assert result["closed"] and result["unchanged"] and result["historyUnchanged"]
    assert result["focus"] == "weaveImageBrowse"


def test_gallery_selection_preserves_stamp_settings_and_undoes_as_one_edit() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      Object.assign(page.S.images[0], {
        source_id: "48-night-moths", name: "48 Night Moths",
        placement: "once", repeats: 7, width_mm: 36, height_mm: 52,
        rotation_deg: 19, offset_around_deg: 359, offset_height_mm: 43,
        amplitude: 2.3, enabled: false, flip_x: true, invert: true,
        follow_lobes: 1.4, flow_coves: 0.7, extrusion_phase_offset: 0.27,
        fade_in_layers: 3, fade_out_layers: 4, layer_skip_enabled: true,
      });
      click('[data-image-tab="0"]');
      type('[data-image-key="amplitude"]', "2.3"); await settle(1000);
      const before = JSON.parse(JSON.stringify(page.patternObject().images[0]));
      const history = weaveMode.historyState().length;
      click("#weaveImageBrowse"); await settle(0);
      click('[data-image-source-id="64-marigold-vine"]'); await settle(1000);
      out.after = JSON.parse(JSON.stringify(page.patternObject().images[0]));
      out.before = before;
      out.historyDelta = weaveMode.historyState().length - history;
      out.closed = $("#weaveImageGalleryOverlay").hidden;
      out.label = $("#weaveImageSourceName").textContent;
      weaveMode.undo(); await settle(1000);
      out.undo = JSON.parse(JSON.stringify(page.patternObject().images[0]));
      weaveMode.redo(); await settle(1000);
      out.redo = JSON.parse(JSON.stringify(page.patternObject().images[0]));
    """
    )
    before = result["before"]
    expected = {
        **before,
        "source_id": "64-marigold-vine",
        "name": "64 Marigold Vine",
        "data_base64": None,
        "blend_edges": False,
    }
    assert result["after"] == expected
    assert result["undo"] == before and result["redo"] == expected
    assert result["historyDelta"] == 1 and result["closed"]
    assert result["label"] == "64 Marigold Vine"


def test_gallery_changes_only_the_selected_image() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); click("#weaveAddImage"); click("#weaveAddImage");
      await settle(1000);
      const before = JSON.parse(JSON.stringify(page.patternObject().images));
      click('[data-image-tab="1"]');
      click("#weaveImageBrowse"); await settle(0);
      click('[data-image-source-id="78-babushka-boteh"]'); await settle(1000);
      out.before = before;
      out.after = JSON.parse(JSON.stringify(page.patternObject().images));
      click("#weaveImageBrowse"); await settle(0);
      out.selected = $$('[data-image-source-id]')
        .filter(card => card.getAttribute("aria-pressed") === "true")
        .map(card => card.dataset.imageSourceId);
      $("#weaveImageGalleryOverlay").dispatchEvent(new KeyboardEvent("keydown", {
        key: "Escape", bubbles: true,
      }));
      out.closed = $("#weaveImageGalleryOverlay").hidden;
    """
    )
    assert result["after"][0] == result["before"][0]
    assert result["after"][2] == result["before"][2]
    assert result["after"][1]["source_id"] == "78-babushka-boteh"
    assert result["selected"] == ["78-babushka-boteh"]
    assert result["closed"]


def test_gallery_traps_tab_focus_and_escape_returns_to_the_picker() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      click("#weaveImageBrowse"); await settle(0);
      const overlay = $("#weaveImageGalleryOverlay");
      $("#weaveImageGalleryClose").focus();
      overlay.dispatchEvent(new KeyboardEvent("keydown", {
        key: "Tab", shiftKey: true, bubbles: true,
      }));
      out.wrappedLast = document.activeElement?.dataset.imageSourceId;
      overlay.dispatchEvent(new KeyboardEvent("keydown", {key: "Tab", bubbles: true}));
      out.wrappedFirst = document.activeElement?.id;
      overlay.dispatchEvent(new KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
      out.closed = overlay.hidden;
      out.returned = document.activeElement?.id;
    """
    )
    assert result["wrappedLast"] == "80-flower-power-hour"
    assert result["wrappedFirst"] == "weaveImageGalleryClose"
    assert result["closed"] and result["returned"] == "weaveImageBrowse"


@pytest.mark.parametrize("source_id", ["01-slipstream", "64-marigold-vine"])
def test_a_late_upload_cannot_replace_a_newer_gallery_choice(source_id: str) -> None:
    scenario = r"""
      click("#weaveAddImage"); await settle(1000);
      const originalFetch = globalThis.fetch;
      let releaseUpload;
      globalThis.FileReader = class {
        readAsDataURL() {
          this.result = "data:image/png;base64,b2xkLWltYWdl";
          queueMicrotask(() => this.onload?.());
        }
      };
      globalThis.fetch = (url, options) => {
        if (String(url).includes("/api/images/upload")) {
          return new Promise(resolve => {
            releaseUpload = () => resolve(new Response(JSON.stringify({
              image: {name: "Older upload", data_base64: "b2xkLWltYWdl", placement: "once"},
            }), {headers: {"Content-Type": "application/json"}}));
          });
        }
        return originalFetch(url, options);
      };
      const input = $("#weaveImageFile");
      input.files = [{name: "older.png"}];
      input.dispatchEvent(new Event("change", {bubbles: true}));
      await settle(0);
      out.started = typeof releaseUpload === "function";
      click("#weaveImageBrowse"); await settle(0);
      click(`[data-image-source-id="${__SOURCE__}"]`); await settle(0);
      releaseUpload(); await settle(1000);
      out.image = page.patternObject().images[0];
      out.hint = $("#weaveImageSourceHint").textContent;
    """
    result = run_page(IMAGE_BROWSER + scenario.replace("__SOURCE__", json.dumps(source_id)))
    assert result["started"]
    assert result["image"]["source_id"] == source_id
    assert result["image"]["data_base64"] is None
    assert result["image"]["placement"] == "repeat"
    assert "Opening image" not in result["hint"]
