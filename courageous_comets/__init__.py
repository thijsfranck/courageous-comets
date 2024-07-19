import logging

from courageous_comets.settings import Settings

log_level_name = Settings.LOG_LEVEL
log_level = logging.getLevelNamesMapping().get(log_level_name, logging.INFO)

logger = logging.getLogger("courageous_comets")

if not logger.hasHandlers():
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s: %(levelname)s] %(message)s"))
    logger.addHandler(handler)
