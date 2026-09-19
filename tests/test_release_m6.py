from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SVG_FIXTURE = ROOT / "tests" / "fixtures" / "svg" / "unitless.svg"


@pytest.fixture(scope="module")
def built_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the distribution without granting the build process network access."""
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("wheel audit requires the uv build frontend")

    output_dir = tmp_path_factory.mktemp("clayline-wheel")
    environment = os.environ.copy()
    environment.update({"UV_OFFLINE": "1", "UV_NO_PROGRESS": "1"})
    completed = subprocess.run(
        [uv, "build", "--wheel", "--offline", "--out-dir", str(output_dir)],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    wheels = tuple(output_dir.glob("clayline-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def test_built_wheel_contains_runtime_profiles_offline_ui_and_license(
    built_wheel: Path,
) -> None:
    with zipfile.ZipFile(built_wheel) as archive:
        names = set(archive.namelist())
        required_package_files = {
            "clayline/__init__.py",
            "clayline/cli.py",
            "clayline/workflow.py",
            "clayline/profiles/generic-marlin-paste.toml",
            "clayline/profiles/generic-reprap-paste.toml",
            "clayline/profiles/delta-wasp-2040-clay.toml",
            "clayline/profiles/eazao-matrix-m500.toml",
            "clayline/profiles/eazao-zero.toml",
            "clayline/profiles/potterbot-10-micro.toml",
            "clayline/profiles/potterbot-10-pro.toml",
            "clayline/profiles/potterbot-super-10.toml",
            "clayline/profiles/potterbot-xl.toml",
            "clayline/profiles/wasp-40100-ldm.toml",
            "clayline/textures.py",
            "clayline/texture_presets/dripper-edge-wave.pattern.json",
            "clayline/texture_presets/dripper-rib.pattern.json",
            "clayline/texture_presets/dripper-weave.pattern.json",
            "clayline/texture_presets/edge-boost.pattern.json",
            "clayline/webui/__init__.py",
            "clayline/webui/app.py",
            "clayline/webui/static/index.html",
            "clayline/webui/static/app.js",
            "clayline/webui/static/app.css",
            "clayline/webui/static/favicon.svg",
            "clayline/webui/static/three.min.js",
            "clayline/webui/static/viewport3d.js",
        }
        assert required_package_files <= names
        assert archive.getinfo("clayline/webui/static/three.min.js").file_size > 400_000

        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
        assert not any(name.startswith(("tests/", "output/", "docs/")) for name in names)

        dist_info = next(
            name.removesuffix("METADATA") for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = archive.read(f"{dist_info}METADATA").decode("utf-8")
        entry_points = archive.read(f"{dist_info}entry_points.txt").decode("utf-8")
        wheel_metadata = archive.read(f"{dist_info}WHEEL").decode("utf-8")

        assert "git+" not in metadata
        assert "Requires-Dist: lxml>=5.3" in metadata
        assert "Provides-Extra: ui" in metadata
        assert "fastapi>=0.115; extra == 'ui'" in metadata
        assert "uvicorn>=0.30; extra == 'ui'" in metadata
        assert "clayline = clayline.cli:main" in entry_points
        assert "Root-Is-Purelib: true" in wheel_metadata
        assert "Tag: py3-none-any" in wheel_metadata
        assert f"{dist_info}licenses/LICENSE" in names


def test_extracted_wheel_runs_cli_and_serves_vendored_ui_assets(
    built_wheel: Path,
    tmp_path: Path,
) -> None:
    installed = tmp_path / "site-packages"
    with zipfile.ZipFile(built_wheel) as archive:
        archive.extractall(installed)

    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONPATH": str(installed),
            "PYTHONNOUSERSITE": "1",
        }
    )
    smoke_script = textwrap.dedent(
        """
        import sys
        from pathlib import Path

        import clayline
        from fastapi.testclient import TestClient
        from clayline.webui.app import create_app

        install_root = Path(sys.argv[1]).resolve()
        package_path = Path(clayline.__file__).resolve()
        assert package_path.is_relative_to(install_root), package_path
        assert clayline.texture_preset_names() == (
            "dripper-rib",
            "dripper-weave",
            "dripper-edge-wave",
            "edge-boost",
        )
        assert clayline.load_texture_preset("Edge").name == "dripper-edge-wave"
        assert clayline.load_texture_preset("Edge Boost").version == 2

        client = TestClient(create_app())
        shell = client.get("/")
        three = client.get("/static/three.min.js")
        assert shell.status_code == 200
        assert 'src="/static/three.min.js"' in shell.text
        assert three.status_code == 200
        assert len(three.content) > 400_000
        assert b"Three.js Authors" in three.content[:200]
        """
    )
    served = subprocess.run(
        [sys.executable, "-c", smoke_script, str(installed)],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert served.returncode == 0, served.stdout + served.stderr

    version = subprocess.run(
        [sys.executable, "-m", "clayline.cli", "--version"],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert version.returncode == 0, version.stdout + version.stderr
    assert version.stdout.strip() == "clayline 0.3.1"

    output = tmp_path / "wheel-smoke.gcode"
    planned = subprocess.run(
        [
            sys.executable,
            "-m",
            "clayline.cli",
            "plan",
            str(SVG_FIXTURE),
            "--profile",
            "potterbot-xl",
            "--nozzle",
            "5",
            "--layers",
            "1",
            "--scale",
            "fit:45",
            "--reproducible",
            "-o",
            str(output),
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert output.is_file()
    assert "; profile_name=potterbot-xl" in output.read_text(encoding="utf-8")

    linted = subprocess.run(
        [sys.executable, "-m", "clayline.cli", "lint", str(output)],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert linted.returncode == 0, linted.stdout + linted.stderr
    assert "Clayline G-code lint: PASS" in linted.stdout
