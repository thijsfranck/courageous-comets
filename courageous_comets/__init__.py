import importlib.metadata

from .client import bot

__all__ = ["bot"]
__version__ = importlib.metadata.version("courageous_comets")
