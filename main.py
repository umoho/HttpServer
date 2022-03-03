import logging

import const
import server
import config
from log import log_init

# Log
log_init()

logging.info(const.MOTD)
logging.info(f'Welcome to use {const.NAME} (version {const.VERSION}, created by {const.AUTHOR})')

# Config
conf = config.read(r'./config.yml')
serv_conf = conf['server']

# Http Server
http_server = server.HTTPServer(host=serv_conf['host'],
                                port=serv_conf['port'],
                                max_link=serv_conf['link']['max'],
                                directory=serv_conf['resources']['directory'] + serv_conf['resources']['index'])

http_server.run()

http_server.stop()
