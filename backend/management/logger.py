from loguru import logger


def configure_logger(prefix: str):
    if not logger._core.handlers:
        logger.add(
            lambda msg: print(msg, end=""),
            level="INFO",
            format=(
                f"<CYAN>{{time:YYYY-MM-DD HH:mm:ss}}</CYAN> | "
                "<level>{level:<8}</level> | "
                f"<cyan>{prefix}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True
        )
    return logger