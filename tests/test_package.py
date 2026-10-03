import clayline


def test_core_import_does_not_require_ui() -> None:
    assert clayline.__version__ == "0.6.0"
    assert "Job" in clayline.__all__
