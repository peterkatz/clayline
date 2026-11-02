"""Mesh exports use current placement before Slice and expose native failures."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from weave_page_rig import run_page

MESH = base64.b64encode(
    (Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj").read_bytes()
).decode("ascii")


def test_surface_export_waits_for_initial_upload_then_uses_current_placement_before_slice() -> None:
    result = run_page(
        f"const meshBytes = {json.dumps(MESH)};"
        + r"""
        weaveMode.importMesh({ name: "cylinder.obj", base64: meshBytes });
        out.first = await weaveMode.exportDesignedSurface();
        out.firstSliced = Boolean(page.S.slice);
        type("#weaveOffsetX", "12.5");
        // No debounce advance: export must flush this placement itself.
        out.second = await weaveMode.exportDesignedSurface();
        out.meshRequests = requests.filter((r) => r.url.startsWith("/api/weave/mesh"));
        out.surfaceRequests = requests.filter((r) => r.url === "/api/weave/surface");
        out.currentMesh = page.S.mesh.mesh_id;
        out.stillUnsliced = !page.S.slice;
        out.message = $("#weaveSurfaceStatus").textContent;
        out.menuOpen = $("#weaveSurfaceStatus").closest("details").open;
        """
    )
    assert result["first"] and result["second"]
    assert not result["firstSliced"] and result["stillUnsliced"]
    assert len(result["meshRequests"]) == len(result["surfaceRequests"]) == 2
    assert "offset_x=12.5" in result["meshRequests"][-1]["url"]
    exported = json.loads(result["surfaceRequests"][-1]["body"])
    assert exported["mesh_id"] == result["currentMesh"]
    assert "slice_id" not in exported and "layer_range" not in exported
    assert "exported" in result["message"]
    assert result["menuOpen"]


def test_native_export_refusals_are_visible_and_do_not_hide_current_preview() -> None:
    result = run_page(
        f"const meshBytes = {json.dumps(MESH)};"
        + r"""
        out.empty = await weaveMode.exportDesignedSurface();
        out.emptyMessage = $("#weaveSurfaceStatus").textContent;
        weaveMode.importMesh({ name: "cylinder.obj", base64: meshBytes });
        await settle(0);
        out.noCoils = await weaveMode.exportMesh();
        out.coilMessage = $("#weaveSurfaceStatus").textContent;
        type("#weaveAmplitude", "0.4");
        page.S.wave = [{ u: 0, value: 1 }, { u: 0.5, value: -1 }];
        toggle("#weaveZBlend", true);
        out.vase = await weaveMode.exportDesignedSurface();
        out.message = $("#weaveSurfaceStatus").textContent;
        out.menuOpen = $("#weaveSurfaceStatus").closest("details").open;
        out.focused = document.activeElement === $("#weaveSurfaceStatus");
        out.previewVisible = !$("#weaveActiveState").hidden;
        """
    )
    assert result["empty"] is False and "Load a mesh" in result["emptyMessage"]
    assert result["noCoils"] is False and "Slice the form" in result["coilMessage"]
    assert result["vase"] is False
    assert "turn off Vase mode in Wall" in result["message"]
    assert result["menuOpen"] and result["focused"] and result["previewVisible"]


def test_printed_coils_button_unlocks_after_audit_downloads_then_locks_on_edit() -> None:
    result = run_page(
        f"const meshBytes = {json.dumps(MESH)};"
        + r"""
        weaveMode.importMesh({ name: "cylinder.obj", base64: meshBytes });
        await settle(0);
        click("#weaveSettleButton");
        await settle(2000);
        out.finalized = Boolean(page.S.exactResult?.exportable && page.S.exactResult?.result_id);
        out.enabled = !$("#weaveExportCoils").disabled && !$("#weaveDownloadButton").disabled;
        click("#weaveExportCoils");
        await settle(0);
        out.objRequests = requests.filter((r) => (
          r.method === "GET" && /\/result\/.*\/obj$/.test(r.url)
        ));
        out.message = $("#weaveSurfaceStatus").textContent;
        type("#weaveAmplitude", "0.35");
        out.lockedOnEdit = $("#weaveExportCoils").disabled && $("#weaveDownloadButton").disabled;
        out.noExactResult = !page.S.exactResult;
        """
    )
    assert result["finalized"] and result["enabled"]
    assert len(result["objRequests"]) == 1
    assert "Printed coils exported" in result["message"]
    assert result["lockedOnEdit"] and result["noExactResult"]
