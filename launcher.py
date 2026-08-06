"""Standard-library-only entry point for the packaged application."""

from __future__ import annotations

import faulthandler
import os
import platform
import sys
import time
import traceback
from pathlib import Path


def _application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _log_path() -> Path:
    candidates = [_application_dir() / "logs"]
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "TingJu" / "logs")
    candidates.append(Path(os.environ.get("TEMP", Path.cwd())) / "TingJu" / "logs")
    for directory in candidates:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            probe = directory / ".tingju-startup-write-test"
            probe.touch(exist_ok=False)
            probe.unlink()
            return directory / "startup.log"
        except (OSError, PermissionError):
            continue
    fallback = Path(os.environ.get("TEMP", Path.cwd())) / "TingJu-startup.log"
    try:
        fallback.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return fallback


START_TIME = time.monotonic()
STARTUP_LOG = _log_path()
_FAULT_HANDLE = None


def _write(message: str, exc_info: bool = False) -> None:
    elapsed = time.monotonic() - START_TIME
    line = f"{elapsed:8.3f}s {message}\n"
    try:
        with STARTUP_LOG.open("a", encoding="utf-8") as handle:
            handle.write(line)
            if exc_info:
                handle.write(traceback.format_exc())
                handle.flush()
    except OSError:
        pass


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, OSError):
            pass


def main() -> int:
    _configure_console()
    try:
        global _FAULT_HANDLE
        _FAULT_HANDLE = STARTUP_LOG.open("ab")
        faulthandler.enable(file=_FAULT_HANDLE)
    except (RuntimeError, OSError):
        _write("faulthandler could not be enabled")

    _write(
        "bootstrap start "
        f"exe={sys.executable!r} cwd={os.getcwd()!r} "
        f"argv={sys.argv!r} frozen={getattr(sys, 'frozen', False)!r} "
        f"meipass={getattr(sys, '_MEIPASS', None)!r} "
        f"python={sys.version.split()[0]} platform={platform.platform()} "
        f"arch={platform.machine()}"
    )
    print("TingJu bootstrap starting...", flush=True)
    print(f"Startup log: {STARTUP_LOG}", flush=True)
    # translators 6.x performs geolocation during import unless this is set.
    # It is still loaded lazily by the application, but this protects any
    # compatibility code that imports it before the first request.
    os.environ.setdefault("translators_default_region", "CN")

    try:
        _write("importing app")
        from app import run
        _write("app imported")
        return run()
    except BaseException:
        _write("startup failed", exc_info=True)
        message = f"TingJu startup failed; details: {STARTUP_LOG}"
        try:
            print(message, file=sys.stderr, flush=True)
        except OSError:
            pass
        if (
            getattr(sys, "frozen", False)
            and os.environ.get("TINGJU_NO_PAUSE") != "1"
            and getattr(sys.stdin, "isatty", lambda: False)()
        ):
            try:
                input("Press Enter to exit...")
            except (EOFError, OSError):
                pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
