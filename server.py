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
        self.is_found = None
        try:
            f = open(self.path, mode='r', encoding='utf-8')
            self.text = f.read()
            self.type = filetype.guess(self.path)
            self.is_found = True
            logging.debug(f'Resources {self.path} loaded successfully')
            f.close()
        except FileNotFoundError as e:
            self.is_found = False
            logging.error(f'Resource file {self.path} is not found')
            logging.exception(e)
        except PermissionError as e:
            logging.error(f'Cannot read resource file {self.path} because file permission error')
            logging.exception(e)
        except IOError as e:
            logging.error(f'Cannot read resource file {self.path} because IO error')
            logging.exception(e)


class Request:

    def __init__(self, recv):
        self.received = recv.decode()
        self.method = self.received.split()[0]
        self.path = self.received.split()[1]
        self.protocol = self.received.split()[2]
        self.header = None
        self.body = None
        # print(f'{self.method} {self.path} {self.protocol}')
        pass


class Response:

    def __init__(self, content, content_type, content_encoding=None,
                 protocol='HTTP/2', status='200', reason=None,
                 server_name=f'{const.NAME} ({const.VERSION})'):
        self.content = content
        self.content_type = content_type
        self.content_encoding = content_encoding
        if self.content_encoding is None:
            # send data without encoding
            self.content_length = sys.getsizeof(self.content)
        elif content_encoding == 'gzip':  # TODO something wrong
            self.encoded_content = gzip.compress(self.content.encode())
            self.content_length = sys.getsizeof(self.encoded_content)
            self.content = str(self.encoded_content)
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
            # no reason
            self.response_head = f'{protocol} {status} {reason}'
        for key in self.objs.keys():
            if self.objs[key] is None:
                # if no value, ignore it
                continue
            # build object info
            self.objects_head += f'{key}: {self.objs[key]}\r\n'
        # finally answer
        self.response = f'{self.response_head}\r\n{self.objects_head}\r\n{self.content}'

    def data(self, encode_method='utf-8'):
        # encode raw data
        return self.response.encode(encode_method)


class HTTPServer:

    def __init__(self, host='localhost', port=80, max_link=5, res_dir='resources', config=None):
        logging.info('Server init...')
        if config is None:
            # one way to config
            self.host = host
            self.port = port
            self.max_link = max_link
            self.res_dir = res_dir
        else:
            # the other way
            serv_conf = config['server']
            res_conf = config['resources']
            self.host = serv_conf['host']
            self.port = serv_conf['port']
            self.max_link = serv_conf['link']['max']
            self.res_dir = res_conf['directory']
            self.index = res_conf['index']
            self.not_found = res_conf['not-found']
        self.runnable = None
        self.server_socket = ServerSocket(host, port, max_link)

    def run(self):
        self.runnable = True
        status = {
            'ok': 200,
            'not-found': 404
        }
        while self.runnable:
            # get request and process
            req = Request(self.server_socket.receive())
            # dir / usually meaning index
            if req.path == r'/':
                res = Resources(f'{self.res_dir}/{self.index}')
                status_code = status['ok']
                if not res.is_found:
                    res = Resources(f'{self.res_dir}/{self.not_found}')
                    status_code = status['ok']
            else:
                res = Resources(req.path)
                status_code = status['not-found']
            self.server_socket.send(Response(content=res.text,
                                             content_type='text/html',
                                             protocol=req.protocol,
                                             status=str(status_code),
                                             reason=None
                                             ).data())

    def stop(self):
        logging.info('Stopping server...')
        self.runnable = False
        logging.info('Server stopped')
        exit(0)


class ServerSocket:

    def __init__(self, host, port, max_link):
        self.client_socket = None
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

    def receive(self, size=1024):
        self.client_socket, address = self.server_socket.accept()
        logging.debug('Link accepted')
        logging.info(f'Linked from {address[0]}:{address[1]}')
        return self.client_socket.recv(size)

    def send(self, data):
        self.client_socket.send(data)
        logging.debug('Message sent')
        self.client_socket.close()
        logging.debug('Link closed')
