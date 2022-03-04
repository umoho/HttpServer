import logging
import socket
import sys
import datetime
import filetype
import gzip

import const


class Resources:

    def __init__(self, path):
        self.type = None
        self.path = path
        self.text = None
        try:
            f = open(self.path, mode='r', encoding='utf-8')
            self.text = f.read()
            self.type = filetype.guess(self.path)
            logging.debug(f'Resources {self.path} loaded successfully')
            f.close()
        except FileNotFoundError as e:
            logging.error(f'Resource file {self.path} is not found')
            logging.exception(e)
        except PermissionError as e:
            logging.error(f'Cannot read resource file {self.path} because file permission error')
            logging.exception(e)
        except IOError as e:
            logging.error(f'Cannot read resource file {self.path} because IO error')
            logging.exception(e)


class Response:

    def __init__(self, content, content_type, content_encoding=None,
                 protocol='HTTP/2', status='200', reason='OK',
                 server_name=f'{const.NAME}'):
        self.content = content
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.content_length = sys.getsizeof(content)
        date_time = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.objs = {
            'Content-Type': content_type,
            'Content-Length': self.content_length,
            'Content-Encoding': self.content_encoding,
            'Date': date_time,
            'Server': server_name
        }
        self.response_head = ''
        self.objects_head = ''
        if reason is None:
            self.response_head = f'{protocol} {status}'
        else:
            self.response_head = f'{protocol} {status} {reason}'
        for key in self.objs.keys():
            if self.objs[key] is None:
                continue
            self.objects_head += f'{key}: {self.objs[key]}\r\n'
        self.response = f'{self.response_head}\r\n{self.objects_head}\r\n{self.content}'

    def raw(self):
        return self.response.encode('utf-8')

    def encoded(self, encode_method):
        encoded_content = None
        if encode_method == 'gzip':
            encoded_content = gzip.compress(self.content.encode('utf-8'))
        return encoded_content


class HTTPServer:

    def __init__(self, host='localhost', port=80, max_link=5, directory='resources'):
        self.runnable = None
        self.dir = directory
        logging.info('Server init...')
        self.server_socket = ServerSocket(host, port, max_link)

    def run(self):
        self.runnable = True
        res = Resources(r'resources/index.html')
        while self.runnable:
            self.server_socket.link(Response(content=res.text, content_type='text/html').raw())

    def stop(self):
        logging.info('Stopping server...')
        self.runnable = False
        logging.info('Server stopped')
        exit(0)

    def response(self):
        pass


class ServerSocket:

    def __init__(self, host, port, max_link):
        logging.info('Server socket init...')
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.debug('Socket created')
            self.server_socket.bind((host, port))
            logging.debug(f'Socket bind {host}:{port}')
        except socket.error as e:
            logging.error(f'Cannot bind host {host} with port {port} because socket error')
            logging.exception(e)
        self.server_socket.listen(max_link)
        logging.info(f'Listening at http://{host}:{port}/')

    def link(self, data=None):
        client_socket, address = self.server_socket.accept()
        client_socket.recv(1024)
        logging.info(f'Linked from {address[0]}:{address[1]}')
        client_socket.send(data)
        logging.debug('Message sent')
        client_socket.close()
        logging.debug('Link closed')
