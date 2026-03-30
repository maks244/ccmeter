"""Version checking and self-update."""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from ccmeter import __version__

PYPI_URL = "https://pypi.org/pypi/ccmeter/json"
CACHE_PATH = Path.home() / ".ccmeter" / "version_check.json"
CHECK_INTERVAL = 86400  # 24 hours


def _fetch_latest() -> str | None:
    try:
        with urlopen(PYPI_URL, timeout=3) as resp:
            data = json.loads(resp.read())
        return data["info"]["version"]
    except Exception:
        return None


def _read_cache() -> tuple[str | None, float]:
    try:
        with CACHE_PATH.open() as f:
            d = json.load(f)
        return d.get("latest"), d.get("checked_at", 0)
    except Exception:
        return None, 0


def _write_cache(latest: str):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps({"latest": latest, "checked_at": time.time()}))


def check_version(quiet: bool = False) -> str | None:
    """Check if a newer version exists. Returns latest version if outdated, None if current."""
    cached, checked_at = _read_cache()
    if time.time() - checked_at < CHECK_INTERVAL and cached:
        latest = cached
    else:
        latest = _fetch_latest()
        if latest:
            _write_cache(latest)

    if not latest or latest == __version__:
        return None

    if _version_tuple(latest) > _version_tuple(__version__):
        if not quiet:
            print(f"  update available: {__version__} -> {latest} (pip install -U ccmeter)")
        return latest
    return None


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def _detect_installer() -> tuple[str, list[str]]:
    """Figure out how ccmeter was installed and return the upgrade command."""
    exe = sys.executable
    # pipx: executable lives in a pipx venv
    if "pipx" in exe:
        return "pipx", ["pipx", "upgrade", "ccmeter"]
    # uv: check if uv is available and we're in a uv-managed env
    if shutil.which("uv"):
        return "uv", ["uv", "pip", "install", "-U", "ccmeter"]
    # fallback: pip
    return "pip", [sys.executable, "-m", "pip", "install", "-U", "ccmeter"]


def run_update():
    """Check for updates and install if available."""
    print(f"current: {__version__}")
    latest = _fetch_latest()
    if not latest:
        print("could not reach PyPI")
        return

    _write_cache(latest)

    if _version_tuple(latest) <= _version_tuple(__version__):
        print("already up to date")
        return

    installer, cmd = _detect_installer()
    print(f"updating to {latest} via {installer}...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"updated to {latest}")
    else:
        print(f"update failed (exit {result.returncode})")
        print(f"try manually: {' '.join(cmd)}")
        raise SystemExit(1)
