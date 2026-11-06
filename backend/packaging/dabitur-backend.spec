# PyInstaller spec for the Dabitur sidecar (one-folder build: fast start, no temp extraction).
# Build from the repo root:  pyinstaller backend/packaging/dabitur-backend.spec --noconfirm
# Output: dist/dabitur-backend/  (copied into the Tauri bundle as a resource by CI)
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).resolve().parents[1]  # noqa: F821 (SPECPATH is set by PyInstaller)
CONFIG = ROOT / "config"
datas = [(str(p), "config") for p in CONFIG.glob("*.yaml")]
datas.append((str(CONFIG / "seed_prices_eur.csv.gz"), "config"))

hidden = collect_submodules("uvicorn") + ["dth.api.main", "yfinance"]

a = Analysis(  # noqa: F821
    [str(ROOT / "backend" / "src" / "dth" / "sidecar.py")],
    pathex=[str(ROOT / "backend" / "src")],
    datas=datas,
    hiddenimports=hidden,
    # Heavy optional extras never go into the desktop build (CLAUDE.md rule 6).
    excludes=["torch", "timesfm", "chronos", "skfolio", "ccxt", "matplotlib", "tkinter",
              "IPython", "pytest", "polars", "sklearn", "scipy", "duckdb"],
    noarchive=False,
)
pyz = PYZ(a.pure)  # noqa: F821
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="dabitur-backend",
    console=False,  # no black window for the tester
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="dabitur-backend", upx=False)  # noqa: F821
