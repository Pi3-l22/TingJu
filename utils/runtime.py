"""Runtime paths shared by source and PyInstaller builds.

The packaged application can be launched from any working directory.  Resources
are read from the application directory, while writable data is kept beside the
portable bundle when possible and falls back to the user's local app-data dir.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


APP_DIR = _application_dir()


def resource_path(*parts: str) -> Path:
    """Return a read-only bundled resource path."""
    return APP_DIR.joinpath(*parts)


def _local_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "TingJu"
    return Path(os.environ.get("TEMP", Path.cwd())) / "TingJu"


def _is_writable(directory: Path) -> bool:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / ".tingju-write-test"
        probe.touch(exist_ok=False)
        probe.unlink()
        return True
    except (OSError, PermissionError):
        return False


def get_data_dir() -> Path:
    """Return a writable directory for logs and user-generated files."""
    configured = os.environ.get("TINGJU_DATA_DIR")
    if configured:
        configured_path = Path(configured).expanduser()
        if _is_writable(configured_path):
            return configured_path

    if _is_writable(APP_DIR):
        return APP_DIR

    fallback = _local_data_dir()
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


DATA_DIR = get_data_dir()
