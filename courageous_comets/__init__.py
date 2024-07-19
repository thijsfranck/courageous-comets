import logging

from courageous_comets.settings import Settings

logger = logging.getLogger("courageous_comets")

if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s: %(levelname)s] %(message)s"))
    logger.addHandler(handler)
