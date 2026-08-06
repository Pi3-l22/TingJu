"""Download and safely unpack the NLTK tokenizer data used by TingJu.

This intentionally avoids ``nltk.download``.  Recent NLTK releases added
platform-specific downloader path checks that reject temporary files on some
GitHub-hosted macOS runners.
"""

from __future__ import annotations

import io
import os
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from zipfile import ZipFile


BASE_URL = os.environ.get(
    "NLTK_DATA_BASE_URL",
    "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers",
).rstrip("/")
OUTPUT_DIR = Path(os.environ.get("NLTK_DATA_DIR", "nltk_data"))


def _safe_extract(zip_bytes: bytes, destination: Path) -> None:
    root = destination.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with ZipFile(io.BytesIO(zip_bytes)) as archive:
        for member in archive.infolist():
            relative = PurePosixPath(member.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe NLTK archive member: {member.filename}")

            target = (root / Path(*relative.parts)).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"NLTK archive escaped destination: {member.filename}")

            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as output:
                output.write(source.read())


def download_package(name: str) -> None:
    url = f"{BASE_URL}/{name}.zip"
    request = Request(url, headers={"User-Agent": "TingJu-NLTK-Bundler/1.0"})
    print(f"Downloading {url}")
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    _safe_extract(payload, OUTPUT_DIR / "tokenizers")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for package in ("punkt", "punkt_tab"):
        download_package(package)

    required = [OUTPUT_DIR / "tokenizers" / "punkt", OUTPUT_DIR / "tokenizers" / "punkt_tab"]
    missing = [str(path) for path in required if not path.is_dir()]
    if missing:
        raise RuntimeError("Missing unpacked NLTK resources: " + ", ".join(missing))

    print(f"NLTK tokenizer data is ready in {OUTPUT_DIR.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
