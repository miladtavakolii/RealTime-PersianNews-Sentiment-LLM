from loguru import logger

logger.add("data/logs/runtime.log")

def get_logger():
    return logger
