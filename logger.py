import logging

logger = logging.getLogger("solana")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("logger.log", mode="a")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
