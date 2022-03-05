import logging
import socket
from enum import Enum, unique

import filetype

import resources
from http import Request
from http import Response


@unique
class HTTPStatusCode(Enum):

    OK = 200
    NOT_FOUND = 404


class HTTPServer:

    def __init__(self, config):
        self.res = None
        logging.info('Server init...')
        if config is None:
            # server cannot start without config
            logging.error('Server cannot start without config')
            return
        else:
            # config the server
            serv_conf = config['server']
            res_conf = config['resources']
            self.host = serv_conf['host']
            self.port = serv_conf['port']
            self.max_link = serv_conf['link']['max']
            self.res_dir = res_conf['directory']
            self.index = res_conf['index']
            self.not_found = res_conf['not-found']
        self.runnable = None
        self.server_socket = ServerSocket(self.host, self.port, self.max_link)

    def run(self):
        self.runnable = True
        while self.runnable:
            # get request and process
            req = Request(self.server_socket.receive())
            # root / will with request
            res_path = f'{self.res_dir}{req.path}'
            not_found_page_path = f'{self.res_dir}/{self.not_found}'
            try:
                resource = resources.GeneralResource(res_path)
                if filetype.guess(res_path) is not None:
                    mime = filetype.guess(res_path).mime
                    res = resources.GeneralResource(res_path, mime)
                    print(mime)
                else:
                    # print(resource.filetype())
                    # TODO more file type support
                    if resource.filetype().lower() == 'js':
                        res = resources.JavaScriptResource(res_path)
                    elif resource.filetype().lower() == 'css':
                        res = resources.CSSResource(res_path)
                    elif resource.filetype().lower() == 'html':
                        try:
                            res = resources.HTMLResource(res_path)
                        except resources.ResourceNotFoundError:
                            res = resources.HTMLResource(not_found_page_path)
                            # TODO no good
                    else:
                        res = resources.HTMLResource(not_found_page_path)
                response = Response(res, status=HTTPStatusCode.OK)
            except resources.ResourceNotFoundError:
                response = Response(resources.EmptyResource(), status=HTTPStatusCode.NOT_FOUND)
                logging.warning(f'Resource at {res_path} is not found')
            self.server_socket.send(response.data())

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
