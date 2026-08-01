import sys
import logging
from datetime import datetime, UTC


class DefaultFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) \n%(message)s\n",
            datefmt="%Y-%m-%d %H:%M:%S"  # default looks like this -> 2026-03-29 00:52:35,846,
        )


class AnsiColorFormatter(DefaultFormatter):
    # Ref on coloured logs and available colours:
    # https://medium.com/@kamilmatejuk/inside-python-colorful-logging-ad3a74442cc6
    no_style = "\033[0m"
    bold = "\033[91m"
    grey = "\033[90m"
    green = "\033[32m"
    yellow = "\033[93m"
    red = "\033[31m"
    red_light = "\033[91m"
    cyan = "\033[36m"
    cyan_bg = "\033[46m"
    cyan_light = "\033[96m"
    cyan_light_bg = "\033[106m"
    blue = "\033[34m"
    blue_light = "\033[94m"
    blue_light_bg = "\033[104m"
    purple = "\033[35m"
    purple_bg = "\033[45m"
    white = "\033[37m"
    white_bg = "\033[47m"
    black = "\033[30m"
    black_bg = "\033[40m"

    def format(self, record: logging.LogRecord):
        start_style = {
            "DEBUG": AnsiColorFormatter.grey,
            "INFO": AnsiColorFormatter.green,
            "WARNING": AnsiColorFormatter.yellow,
            "ERROR": AnsiColorFormatter.red,
            "CRITICAL": AnsiColorFormatter.red_light + AnsiColorFormatter.bold,
        }.get(record.levelname, AnsiColorFormatter.no_style)

        end_style = AnsiColorFormatter.no_style

        return f"{start_style}{super().format(record)}{end_style}"


class Logger:
    # File logger setting
    FILE_LOGGER_ENABLED: bool = True  # useful when long logs
    FILE_LOGGER_NEW_RUN_FILE: bool = False  # useful when comparing log files
    FILE_LOGGER_MODE: str = "w"  # a=append, w=write

    # logging.basicConfig(
    #     format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
    #     # level=logging.INFO,
    #     # filename="logs/local.log",
    #     # filemode="a"  # defaults to `a`
    # )
    logger = logging.getLogger("CashFlowTrackerLogger")

    # Once a message passes the logger, each handler then applies its own
    # filter. So logger needs to have the most relaxed level.
    logger.setLevel(logging.DEBUG)

    # Console handler with color formatter
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)  # TODO: change to ERROR
    console_handler.setFormatter(AnsiColorFormatter())
    logger.addHandler(console_handler)

    # File handler
    if FILE_LOGGER_ENABLED:
        log_level = logging.DEBUG
        log_level_name = logging.getLevelName(log_level)

        file_handler = logging.FileHandler(
            filename=f"logs/{log_level_name}-{datetime.now(tz=UTC)}.log"
            if FILE_LOGGER_NEW_RUN_FILE
            else f"logs/{log_level_name}.log",
            mode=FILE_LOGGER_MODE
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(DefaultFormatter())
        logger.addHandler(file_handler)


logger = Logger.logger


def debug_log(*args):
    allow_debug_log = True  # manual toggle for now

    if allow_debug_log:
        print(f"\n>>> {AnsiColorFormatter.blue_light_bg}{AnsiColorFormatter.black}\
              {'\n'.join([str(arg) for arg in args])}{AnsiColorFormatter.no_style}")


if __name__ == "__main__":
    logger.debug("Testing Debug Message")
    logger.info("Testing Info Message")
    logger.warning("Testing Warning Message")
    logger.error("Testing Error Message")

    debug_log("testing", "debug_log()")
