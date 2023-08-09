import logging
import sys


def create_log(log_path: str):
    file_handler = logging.FileHandler(filename=log_path)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    frm = logging.Formatter("{asctime} [{levelname:4}] {message}",
                            "%d.%m.%Y %H:%M:%S",
                            "{"
                            )
    file_handler.setFormatter(frm)
    stream_handler.setFormatter(frm)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(level=logging.INFO)
    return logger
