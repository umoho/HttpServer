import sys
import datetime

import const


class Request:

    def __init__(self, recv):
        self.received = recv.decode()
        self.method = self.received.split()[0]
        self.path = self.received.split()[1]
        self.protocol = self.received.split()[2]
        self.header = None
        self.body = None
        # print(f'{self.method} {self.path} {self.protocol}')
        pass  # TODO


class Response:

    def __init__(self, resource,
                 protocol='HTTP/2', status='200', reason=None,
                 server_name=f'{const.NAME} ({const.VERSION})'):
        self.content = resource.content
        self.content_type = resource.type
        if resource.ENCODE_ABLE is True:
            if resource.encoding is not None:
                self.content_encoding = resource.encoding
            else:
                self.content_encoding = None
        else:
            self.content_encoding = None
        self.content_length = sys.getsizeof(self.content)
        date_time = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.objs = {
            'Content-Type': self.content_type,
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

    def data(self, encoding='utf-8'):
        # encode raw data
        return self.response.encode(encoding)
