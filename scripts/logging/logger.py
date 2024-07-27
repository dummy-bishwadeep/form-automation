import logging
import pathlib
from logging import StreamHandler
from logging.handlers import RotatingFileHandler, SocketHandler
from scripts.config import Services, PathConf


def read_configuration():
    return {
        "name": Services.PROJECT_NAME,
        "handlers": [
            {"type": "RotatingFileHandler", "max_bytes": Services.MAX_BYTES, "back_up_count": Services.BACKUP_COUNT},
            {"type": "StreamHandler", "name": Services.PROJECT_NAME},
        ],
    }


def init_logger():
    logging_config = read_configuration()

    """
    Creates a rotating log
    """
    __logger__ = logging.getLogger(Services.PROJECT_NAME)
    __logger__.setLevel(Services.LOG_LEVEL)

    log_formatter = "%(asctime)s - %(levelname)-6s - [%(funcName)5s(): %(lineno)s] - %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_formatter, time_format)
    for each_handler in logging_config["handlers"]:
        if (
                each_handler["type"] in ["RotatingFileHandler"]
                and Services.ENABLE_FILE_LOGGING
        ):
            pathlib.Path(PathConf.LOG_PATH).mkdir(parents=True, exist_ok=True)
            log_file = pathlib.Path(PathConf.LOG_PATH, f"{Services.PROJECT_NAME}.log")
            temp_handler = RotatingFileHandler(
                log_file,
                maxBytes=each_handler["max_bytes"],
                backupCount=each_handler["back_up_count"],
            )
            temp_handler.setFormatter(formatter)
        elif each_handler["type"] in ["SocketHandler"]:
            temp_handler = SocketHandler(each_handler["host"], each_handler["port"])
        elif each_handler["type"] in ["StreamHandler"]:
            temp_handler = StreamHandler()
            temp_handler.setFormatter(formatter)

        else:
            temp_handler = None
        __logger__.addHandler(temp_handler)

    return __logger__


logger = init_logger()
