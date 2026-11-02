import tomllib
from pathlib import Path

import clayline


def test_core_import_does_not_require_ui() -> None:
    project = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert clayline.__version__ == project["project"]["version"]
    assert "Job" in clayline.__all__
