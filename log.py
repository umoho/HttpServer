import logging


def log_init():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s',
                        level=logging.INFO)

