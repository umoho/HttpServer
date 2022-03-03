import logging
import yaml


def read(file_path):
    data = ''
    try:
        file = open(file_path, mode='r', encoding='utf-8')
        data = yaml.load(file, Loader=yaml.FullLoader)
        logging.info('Config loaded')
        file.close()
    except FileNotFoundError:
        logging.error('Config file is not found')
    except PermissionError:
        logging.error('Cannot read config because file permission error')
    return data


def write(file_path, data):
    try:
        file = open(file_path, mode='w', encoding='utf-8')
        file.write(data)
        file.close()
    except FileNotFoundError:
        logging.error('Config file is not found')
    except PermissionError:
        logging.error('Cannot read config because file permission error')
