import logging
import sys
import getopt

import const
import server
import config
from log import log_init


def main(argv):
    # Log
    log_init()

    # Welcome
    logging.info(const.MOTD)
    logging.info(f'Welcome to use {const.NAME} (version {const.VERSION}, created by {const.AUTHOR})')

    # Option
    opts = None
    try:
        opts, args = getopt.getopt(argv, 'hc:', ['help', 'config='])
    except getopt.GetoptError as e:
        logging.exception(e)
        exit(2)

    conf = None

    for opt, arg in opts:
        # Config
        if opt in ('-c', '--config'):
            conf = config.Config.read(file_path=arg)
            logging.info('Use user config file')

    if not opts:
        conf = config.Config.read(file_path='./config.yml')
        logging.info('Use default config file')

    # Http Server
    http_server = server.HTTPServer(config=conf)

    http_server.run()

    # TODO http_server.stop()


if __name__ == '__main__':
    main(sys.argv[1:])
