# Const
from enum import unique, Enum

NAME = 'Pico Pages'  # 'A Simple HTTP Server'
VERSION = '0.1 alpha'
AUTHOR = 'umoho'
MOTD = 'Nice Day!'


@unique
class EncodingMethod(Enum):

    GZIP = 1

