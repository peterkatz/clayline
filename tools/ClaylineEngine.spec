# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


PROJECT_ROOT = Path(SPECPATH).resolve().parent

# pyinstaller-hooks-contrib ships hooks for both PIL and pillow_heif, but the
# reference lightbox's HEIC fallback (/api/convert-image) is easy to lose
# silently if a hook regresses: libheif is a compiled dylib pillow_heif loads
# at runtime, not a pure-Python import, so it is collected here explicitly
# rather than trusted to hiddenimports alone.
datas = collect_data_files("clayline") + collect_data_files("pillow_heif")
binaries = collect_dynamic_libs("pillow_heif")

analysis = Analysis(
    [str(PROJECT_ROOT / "tools" / "clayline_engine.py")],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "fullcontrol.devices.community.singletool.generic",
        "fullcontrol.gcode.primer_library.no_primer",
        "PIL",
        "PIL.Image",
        "PIL.JpegImagePlugin",
        "PIL.PngImagePlugin",
        "PIL.WebPImagePlugin",
        "pillow_heif",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="ClaylineEngine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ClaylineEngine",
)
