import importlib.metadata
import logging

from .client import bot

__all__ = ["bot"]

# Package version may not be available in CI.
try:
    __version__ = f"v{importlib.metadata.version("courageous_comets")}"
except importlib.metadata.PackageNotFoundError:
    logging.warning("Could not determine the package version.")
    __version__ = "latest"
