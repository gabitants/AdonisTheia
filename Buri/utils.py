"""
Buri Utils
===========

Utility methods for Buri.
"""
import os
from typing import List, Optional, Dict, Any
import logging
from subprocess import getstatusoutput

try:
    from termcolor import cprint
except Exception as e:
    print(e)
    # pylint: disable=unused-argument

    def cprint(msg: str, **kwargs: Any) -> None:  # type: ignore
        """ Print wrap to replace cprint. """
        print(msg)

LOGGERS: Dict[str, logging.Logger] = {}


def create_logger(name: str, base_dir: str = "", level: int = logging.DEBUG) -> logging.Logger:
    """
    Creates a logger, bound to a name. When calling the method again with same log name, ill return the same logger.

    :param name: Name of the logger. (str)
    :param base_dir: Directory where the log file will be created. (str)
    :param level: Level of debugging. (int)
    :return: Logger. (logger)
    """
    if name in LOGGERS:
        return LOGGERS[name]
    log = logging.getLogger(name)
    log.setLevel(level)
    fh = logging.FileHandler(os.path.join(base_dir, f"{name}.log"))
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s -%(levelname)10s : %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
    log.addHandler(fh)
    LOGGERS[name] = log
    return LOGGERS[name]


def show(logger_instance: logging.Logger, msg: str, color: str = "", attrs: Optional[List[str]] = None, tabs: int = 0,
         level: str = "INFO") -> None:
    """
    Prints msg and logs as info.

    :param logger_instance: Object used to log. (logger)
    :param msg: Message to show. (str)
    :param color: Color to print in. (str)
    :param attrs: *cprint* attributes. (list)
    :param tabs: Number of tabs to print before message. (int)
    :param level: Log level. (str)
    :raise NotImplementedError: When given an invalid logger level.
    """
    if level == "INFO":
        logger_instance.info(msg)
    elif level == "WARN":
        logger_instance.warning(msg)
        if not color:
            color = 'yellow'
    elif level == "ERROR":
        logger_instance.error(msg)
        if not color:
            color = 'red'
    else:
        raise NotImplementedError(f"Logger level '{level}' is not implemented for message: {msg}")
    cprint("\t" * tabs + msg, color=color or None, attrs=attrs)


def cmd(logger_instance: logging.Logger, c: str, msg: str, raising: bool = True) -> str:
    """
    Abstraction of `subprocess.getstatusoutput`.

    :param logger_instance: Logger instance. (Logger)
    :param c: Command. (str)
    :param msg: Message that accompanies any Exceptions raised. (str)
    :param raising: If should raise exceptions. (bool)
    :return: Command result. (str)
    :raise Exception: If return status is not 0 and raising is set.
    """
    print(f'Calling: {c}')
    if logger_instance:
        logger_instance.info(f'Calling: {c}')
    sts, out = getstatusoutput(c)
    if sts != 0 and raising:
        raise Exception(f'{msg}: {out}')
    if logger_instance:
        logger_instance.info(f'Output: {out}')
    return out
