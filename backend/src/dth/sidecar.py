"""Entry point of the packaged backend started by the desktop shell (ADR 0003).

The shell picks a free port and a random token and passes them on the command line:

    dabitur-backend --port 51234 --token <random>

When frozen by PyInstaller, configuration files ship inside the bundle and user data goes to
``%LOCALAPPDATA%\\Dabitur`` (or ``~/.local/share/Dabitur`` elsewhere).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


def user_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "Dabitur"
    return Path.home() / ".local" / "share" / "Dabitur"


def configure_environment(bundle_dir: Path | None) -> None:
    """Set DTH_* defaults before settings are first read; explicit env vars win."""
    if bundle_dir is not None:
        os.environ.setdefault("DTH_CONFIG_DIR", str(bundle_dir / "config"))
    data = Path(os.environ.setdefault("DTH_DATA_DIR", str(user_data_dir())))
    data.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="dabitur-backend")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token", default=None)
    args = parser.parse_args(argv)

    frozen_dir = getattr(sys, "_MEIPASS", None)
    configure_environment(Path(frozen_dir) if frozen_dir else None)
    if args.token:
        os.environ["DTH_API_TOKEN"] = args.token

    log_file = Path(os.environ["DTH_DATA_DIR"]) / "dabitur-backend.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )

    import uvicorn

    from dth.api.main import app

    # Only loopback: the API is never reachable from the network.
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_config=None, access_log=False)


if __name__ == "__main__":
    main()
