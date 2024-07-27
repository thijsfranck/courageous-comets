from pathlib import Path

CACHE_ROOT = Path("artifacts/charts").resolve()
CACHE_ROOT.mkdir(parents=True, exist_ok=True)

__all__ = ["CACHE_ROOT"]
