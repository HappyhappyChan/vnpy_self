"""
Global setting of the trading platform.
"""

from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone_name

from .utility import load_json


SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    # "datafeed.name": "",
    # "datafeed.username": "",
    # "datafeed.password": "",
    "datafeed.name": "tushare",
    "datafeed.username": "token",
    "datafeed.password": "c044c2469407484159d4f7dfa2d438f5ac3e4fc89f540264c95ce268",

    "database.timezone": get_localzone_name(),
    # "database.name": "sqlite",
    # "database.database": "database.db",
    # "database.host": "",
    # "database.port": 0,
    # "database.user": "",
    # "database.password": ""
    "database.name": "mysql",
    "database.database": "vnpy",
    "database.host": "localhost",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "cheng123"
}


# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length: int = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
