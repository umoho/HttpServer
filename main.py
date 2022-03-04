import logging

import const
import server
import config
from log import log_init

# Log
log_init()

logging.info(const.MOTD)
logging.info(f'Welcome to use {const.NAME} (version {const.VERSION}, created by {const.AUTHOR})')

# Confi

conf = config.Config.read(file_path='./config.yml')

# Http Server
http_server = server.HTTPServer(config=conf)

http_server.run()

# TODO http_server.stop()
