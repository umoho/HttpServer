import logging
import os
import socket
import sys
import datetime

import const


def check_resources(path):
    path_dir = os.listdir(path)
    for all_dir in path_dir:
        child = os.path.join('%s%s' % (path, all_dir))
        print(child.encode('gbk'))


def read_resources(path):
    # check_resources(path)
    text = ''
    try:
        f = file = open(path, mode='r', encoding='utf-8')
        text = f.read()
        logging.info('Resources loaded')
        f.close()
    except FileNotFoundError:
        logging.error('Resource files is not found')
    except PermissionError:
        logging.error('Cannot read resources because file permission error')
    except IOError:
        logging.error('Cannot read resources because IO error')
    return text


def response(data,
             server_name=f'{const.NAME} (version {const.VERSION})',
             content_type='text/html',
             protocol='HTTP/1.x',
             state_code='200 OK'):
    date_time = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = sys.getsizeof(data)
    line = f'{protocol} {state_code}\r\n'
    head = f'Server: {server_name}\r\n' \
           f'Date: {date_time}\r\n' \
           f'Content-Length: {content_length}\r\n' \
           f'Content-Type: {content_type}\r\n'
    resp = f'{line}{head}\r\n{data}'
    return resp


class HTTPServer:

    def __init__(self, host='localhost', port=80, max_link=5, directory='resources'):
        self.runnable = None
        self.dir = directory
        logging.info('Server init...')
        self.server_socket = ServerSocket(host, port, max_link)

    def run(self):
        self.runnable = True
        while self.runnable:
            self.server_socket.link(response(data=read_resources(self.dir)))

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
        except socket.error:
            logging.error(f'Cannot bind host {host} with port {port} because socket error')
        self.server_socket.listen(max_link)
        logging.info(f'Listening at http://{host}:{port}/')

    def link(self, message=''):
        client_socket, address = self.server_socket.accept()
        client_socket.recv(1024)
        logging.info(f'Linked from {address[0]}:{address[1]}')
        client_socket.send(message.encode('utf-8'))
        logging.debug('Message sent')
        client_socket.close()
        logging.debug('Link closed')


class RequestParse:

    def __init__(self, request):
        self.content = request
        self.method = request.split()[0]
        self.path = request.split()[1]
        self.body = request.split('\r\n\r\n', 1)[1]

    def body(self):
        return self.body

    def path(self):
        index = self.path.find('?')
        if index == -1:
            return self.path, {}
        else:
            path, query_string = self.path.split('?', 1)
