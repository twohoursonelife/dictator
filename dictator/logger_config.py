import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<d>{time:YYYY-MM-DD HH:mm:ss}</d> <lvl>{level}</lvl>     {message}",
    colorize=True,
    level="INFO",
)
