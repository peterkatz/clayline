"""Focused G-code contract for Revision-3 weave continuity metadata."""

from __future__ import annotations

from dataclasses import replace

from clayline.emit import EmissionMotion, EmissionPoint, EmissionSettings, _render_emission_body
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile


def _render_print_comment(source_move: Move) -> str:
    event = EmissionMotion(
        point=EmissionPoint(82.0, 80.0, 2.0),
        command="G1",
        extrude=True,
        area_mm2=1.0,
        feed_mm_s=10.0,
        kind=MoveKind.PRINT,
        page=source_move.page_index,
        layer=source_move.layer_index,
        stroke=source_move.stroke_id,
        source_move=source_move,
        comment="deposited climb",
    )
    stream = MoveStream("continuity-comment", "potterbot-xl", (source_move,))
    body, _stats, _offsets = _render_emission_body(
        (event,),
        stream,
        load_profile("potterbot-xl"),
        EmissionSettings(bead_width=3.5, layer_height=1.05),
        initial_point=EmissionPoint(80.0, 80.0, 2.0),
    )
    line = next(line for line in body if "kind=print" in line)
    return line.partition("; clayline ")[2]


def test_print_comment_exposes_continuity_metadata_in_fixed_order() -> None:
    proof_hash = "a" * 64
    # Deliberately reverse the source ordering: emitted order is a contract,
    # not an accident of tuple construction or dict insertion order.
    metadata = tuple(
        reversed(
            (
                ("clay_thread_id", "thread-0"),
                ("deposition_run_id", "run-0"),
                ("interior_role", "layer_climb"),
                ("continuity_from_layer", 26),
                ("continuity_to_layer", 27),
                ("continuity_route_class", "wall_corridor"),
                ("continuity_supported", True),
                ("continuity_candidate_xy_mm", 2.58),
                ("continuity_support_max_xy_mm", 1.75),
                ("continuity_proof_hash", proof_hash),
                ("layer_climb_flow_multiplier", 0.625),
                ("layer_climb_feed_mm_s", 7.25),
                ("terminal_release_tail", False),
            )
        )
    )
    source = Move(
        MoveKind.PRINT,
        3,
        27,
        "entry",
        x=82.0,
        y=80.0,
        z=2.0,
        metadata=metadata,
    )

    assert _render_print_comment(source) == (
        "kind=print page=3 layer=27 stroke=entry "
        "clay_thread_id=thread-0 deposition_run_id=run-0 "
        "interior_role=layer_climb continuity_from_layer=26 continuity_to_layer=27 "
        "continuity_route_class=wall_corridor continuity_supported=true "
        "continuity_candidate_xy_mm=2.58 continuity_support_max_xy_mm=1.75 "
        f"continuity_proof_hash={proof_hash} "
        "layer_climb_flow_multiplier=0.625 layer_climb_feed_mm_s=7.25 "
        "terminal_release_tail=false note=deposited climb"
    )


def test_legacy_deposition_run_metadata_preserves_print_comment_bytes() -> None:
    source = Move(MoveKind.PRINT, 0, 0, "legacy", x=82.0, y=80.0, z=2.0)

    assert _render_print_comment(
        replace(
            source,
            metadata=(
                ("deposition_run_id", "legacy-run"),
                ("page_name", "owner metadata"),
            ),
        )
    ) == _render_print_comment(source)
