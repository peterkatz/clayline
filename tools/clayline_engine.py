"""Frozen-process entry point for Clayline's managed desktop engine."""

from clayline.desktop_server import main


if __name__ == "__main__":
    raise SystemExit(main())
