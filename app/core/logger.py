import logging
from pathlib import Path

# logs/ sits next to main.py
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ImmediateFileHandler(logging.FileHandler):
    # Flush after every line so tail -f logs/app.log updates right away.
    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


def get_logger(name: str = "ai-multi-llm") -> logging.Logger:
    logger = logging.getLogger(name)

    # uvicorn --reload can import this file twice. Skip if already set up.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Real-time in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Same lines also go to logs/app.log
    file_handler = ImmediateFileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
