# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


PROJECT_ROOT = Path(SPECPATH).resolve().parent

# The reference lightbox's HEIC fallback (/api/convert-image) is easy to lose
# silently if a hook regresses: libheif is a compiled dylib pi_heif loads at
# runtime, not a pure-Python import, so it is collected here explicitly rather
# than trusted to hiddenimports alone. pi_heif is the decode-only build of
# pillow_heif, so no GPL HEVC encoder (libx265) lands in the app.
datas = collect_data_files("clayline") + collect_data_files("pi_heif")
binaries = collect_dynamic_libs("pi_heif")

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
        "pi_heif",
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
