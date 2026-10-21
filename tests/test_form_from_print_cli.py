"""`clayline weave --from <print file> --form-from-print`.

docs/plan-form-from-print-file.md, "CLI".  Today's refusal stays the default;
the flag makes the form from the printed surface only when no model is given
and none sits beside the print file, writes it beside the output once the run
has succeeded, places it as it printed over the whole range, and switches
every weave off.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

import clayline as cl
from clayline.cli import main
from clayline.weave_restore import parse_weave_gcode

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
MADE = (
    "MADE form from saved.gcode: cylinder.obj is not beside it, so the printed surface is the form"
)
WEAVES_OFF = "WARNING [form_from_print] weaves are off: the pattern is already in the form"


def _saved(folder: Path, *, model_beside: bool = False, **settings: object) -> Path:
    """A woven cylinder printed from a model in its own folder, away from the print."""

    models = folder / "models"
    models.mkdir()
    model = models / MESH.name
    shutil.copyfile(MESH, model)
    result = (
        cl.load_mesh(model)
        .slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
        .modulate(
            "sine",
            amplitude=2.0,
            wavelength=18.0,
            reproducible=True,
            wet_density_g_cm3=2.05,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="form-from-print-cli",
            **settings,
        )
    )
    prints = folder / "prints"
    prints.mkdir()
    saved = prints / "saved.gcode"
    saved.write_text(result.emission.gcode, encoding="utf-8")
    if model_beside:
        shutil.copyfile(model, prints / MESH.name)
    return saved


def _stderr_lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return capsys.readouterr().err.splitlines()


def test_the_flag_makes_the_form_from_the_printed_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    out = tmp_path / "out"
    again = out / "again.gcode"

    status = main(["weave", "--from", str(saved), "--form-from-print", "-o", str(again)])

    assert status == 0
    form = out / "saved-as-printed.obj"
    assert form.is_file() and again.is_file()
    err = _stderr_lines(capsys)
    # The form is written, and said so, only once the run has succeeded.
    assert err[0] == WEAVES_OFF
    assert err[-3:] == [MADE, f"WROTE {form}", f"WROTE {again}"]
    assert not any("source_mesh_hash" in line for line in err)

    recipe = parse_weave_gcode(again)
    assert recipe.source_mesh_name == form.name
    # Placed as it printed, over the whole form, with every weave off and
    # every other setting the file's own.
    assert (recipe.scale, recipe.scale_x, recipe.scale_y, recipe.scale_z) == (1, 1, 1, 1)
    assert recipe.rotation_deg == recipe.rotation_x_deg == recipe.rotation_y_deg == 0
    text = again.read_text(encoding="utf-8")
    assert "; parameter.layer_range_from=1" in text
    assert "; parameter.layer_range_to=15" in text
    assert "; parameter.layer_range_total=15" in text
    original = parse_weave_gcode(saved)
    assert original.pattern.settings.wave_on is True
    assert recipe.pattern.settings.wave_on is False
    assert recipe.pattern.settings.amplitude == original.pattern.settings.amplitude

    # The form written is the form used: restored beside it, the new print
    # comes back byte for byte with no warning.
    capsys.readouterr()
    twice = out / "twice.gcode"
    assert main(["weave", "--from", str(again), "-o", str(twice)]) == 0
    assert twice.read_bytes() == again.read_bytes()
    assert not any(line.startswith("WARNING") for line in _stderr_lines(capsys))


def test_a_model_beside_the_print_wins_over_the_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path, model_beside=True)
    out = tmp_path / "out"
    again = out / "again.gcode"

    status = main(["weave", "--from", str(saved), "--form-from-print", "-o", str(again)])

    assert status == 0
    assert again.read_bytes() == saved.read_bytes()
    assert sorted(path.name for path in out.iterdir()) == ["again.gcode"]
    err = _stderr_lines(capsys)
    assert (
        "NOTE: cylinder.obj is beside saved.gcode, so it is the form; "
        "--form-from-print is not needed."
    ) in err
    assert MADE not in err and WEAVES_OFF not in err


def test_a_given_model_wins_over_the_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    model = tmp_path / "models" / MESH.name
    out = tmp_path / "out"
    again = out / "again.gcode"

    status = main(
        ["weave", str(model), "--from", str(saved), "--form-from-print", "-o", str(again)]
    )

    assert status == 0
    assert again.read_bytes() == saved.read_bytes()
    assert sorted(path.name for path in out.iterdir()) == ["again.gcode"]
    err = _stderr_lines(capsys)
    assert "NOTE: cylinder.obj is given, so it is the form; --form-from-print is not needed." in err
    assert MADE not in err


def test_a_layer_range_must_fit_the_form(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    out = tmp_path / "out"
    refused = out / "refused.gcode"

    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--layer-range",
            "3",
            "40",
            "-o",
            str(refused),
        ]
    )

    assert status == 1
    # Refused before anything is made or written: no form is left behind.
    assert _stderr_lines(capsys) == [
        "ERROR: --layer-range 3 40 does not fit the form made from saved.gcode: it has 15 layers"
    ]
    assert not out.exists()

    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--layer-range",
            "5",
            "2",
            "-o",
            str(refused),
        ]
    )
    assert status == 1
    assert _stderr_lines(capsys) == [
        "ERROR: --layer-range 5 2 does not fit the form made from saved.gcode: it has 15 layers"
    ]
    assert not out.exists()

    trimmed = out / "trimmed.gcode"
    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--layer-range",
            "2",
            "4",
            "-o",
            str(trimmed),
        ]
    )
    assert status == 0
    text = trimmed.read_text(encoding="utf-8")
    assert "; parameter.layer_range_from=2" in text
    assert "; parameter.layer_range_to=4" in text


def test_without_the_flag_the_old_refusal_stands(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    out = tmp_path / "out"

    status = main(["weave", "--from", str(saved), "-o", str(out / "again.gcode")])

    assert status == 1
    assert _stderr_lines(capsys) == [
        "ERROR: restored recipe needs source mesh 'cylinder.obj'; "
        "pass the matching mesh path after the G-code"
    ]
    assert not out.exists()


def _edited(saved: Path) -> None:
    lines = saved.read_text(encoding="utf-8").splitlines()
    index = next(i for i, line in enumerate(lines) if " note=weave wall" in line)
    lines[index] = re.sub(r"X(\d+)\.", lambda m: f"X{int(m.group(1)) + 1}.", lines[index], count=1)
    saved.write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("settings", "edit", "why"),
    [
        (
            {"stack_pieces": True, "nozzle_clearance_mm": 10.0},
            False,
            "Clayline can't yet make a form from saved.gcode: it was printed with Stack pieces",
        ),
        (
            {},
            True,
            "saved.gcode has been changed since Clayline wrote it, "
            "so Clayline can't make a form from it",
        ),
    ],
)
def test_a_print_with_no_form_stops_and_says_why(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    settings: dict[str, object],
    edit: bool,
    why: str,
) -> None:
    saved = _saved(tmp_path, **settings)
    if edit:
        _edited(saved)
    out = tmp_path / "out"

    status = main(
        ["weave", "--from", str(saved), "--form-from-print", "-o", str(out / "again.gcode")]
    )

    assert status == 1
    assert _stderr_lines(capsys) == [
        f"ERROR: {why}. Pass cylinder.obj after the print file to go on with the job."
    ]
    assert not out.exists()


def test_placing_flags_and_a_missing_print_file_are_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    out = tmp_path / "out"

    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--scale",
            "2",
            "--offset",
            "5",
            "0",
            "-o",
            str(out / "again.gcode"),
        ]
    )
    assert status == 1
    assert _stderr_lines(capsys) == [
        "ERROR: the form made from saved.gcode stays the size and in the place it printed; "
        "leave out --scale, --offset"
    ]
    assert not out.exists()

    assert main(["weave", str(MESH), "--form-from-print", "-o", str(out / "x.gcode")]) == 1
    assert _stderr_lines(capsys) == [
        "ERROR: --form-from-print makes the form from the print file --from names"
    ]


@pytest.mark.parametrize(
    ("reason", "why"),
    [
        (
            "profile_missing",
            "Clayline can't make a form from saved.gcode: it was made with a printer that is "
            "no longer in the list",
        ),
        (
            "profile_changed",
            "Clayline can't make a form from saved.gcode: its printer's bed has changed since "
            "it printed",
        ),
    ],
)
def test_a_printer_that_is_gone_or_changed_is_named(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
    why: str,
) -> None:
    import clayline.form_from_print as ffp

    saved = _saved(tmp_path)
    monkeypatch.setattr(
        ffp,
        "form_from_print",
        lambda text, *, print_file, recipe: ffp.FormFromPrint(
            kind=ffp.NO_FORM,
            reason=reason,
            print_file=print_file,
            model_name=MESH.name,
            model_sha256=None,
        ),
    )
    out = tmp_path / "out"

    status = main(
        ["weave", "--from", str(saved), "--form-from-print", "-o", str(out / "again.gcode")]
    )

    assert status == 1
    assert _stderr_lines(capsys) == [
        f"ERROR: {why}. Pass cylinder.obj after the print file to go on with the job."
    ]
    assert not out.exists()


def test_a_dry_run_is_refused_and_no_output_means_the_current_folder(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    saved = _saved(tmp_path)
    here = tmp_path / "here"
    here.mkdir()
    monkeypatch.chdir(here)

    assert main(["weave", "--from", str(saved), "--form-from-print", "--dry-run"]) == 1
    assert _stderr_lines(capsys) == [
        "ERROR: --dry-run writes nothing, and --form-from-print writes a form; leave one out"
    ]
    assert list(here.iterdir()) == []

    assert main(["weave", "--from", str(saved), "--form-from-print"]) == 0
    form = here.resolve() / "saved-as-printed.obj"
    assert form.is_file()
    assert _stderr_lines(capsys)[-2:] == [MADE, f"WROTE {form}"]


def test_weave_one_flags_are_refused_unless_a_new_wave_is_given(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saved = _saved(tmp_path)
    out = tmp_path / "out"

    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--amplitude",
            "3",
            "--twist",
            "0.5",
            "-o",
            str(out / "again.gcode"),
        ]
    )
    assert status == 1
    assert _stderr_lines(capsys) == [
        "ERROR: every weave is off on the form made from saved.gcode; "
        "leave out --amplitude, --twist, or give --wave for a new pattern"
    ]
    assert not out.exists()

    waved = out / "waved.gcode"
    status = main(
        [
            "weave",
            "--from",
            str(saved),
            "--form-from-print",
            "--wave",
            "sine",
            "--amplitude",
            "3",
            "-o",
            str(waved),
        ]
    )
    assert status == 0
    assert "NOTE: --wave lays its pattern over the one already in the form." in _stderr_lines(
        capsys
    )
    assert parse_weave_gcode(waved).pattern.settings.amplitude == 3
