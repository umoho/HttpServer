import logging
import os.path

from const import EncodingMethod


class Resources:

    def __init__(self):
        self.type = None
        self.ENCODE_ABLE = None


class FileResources(Resources):

    data = None

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.data = None
        self.type = None
        self.is_found = None
        self.ENCODE_ABLE = None
        try:
            f = open(self.path, mode='r', encoding='utf-8')
            self.data = f.read()
            self.is_found = True
            FileResources.data = self.data
            logging.debug(f'Resources {self.path} loaded successfully')
            f.close()
        except FileNotFoundError:
            self.is_found = False
            logging.warning(f'Resource file {self.path} is not found')
            raise ResourceNotFoundError
        except PermissionError as e:
            logging.error(f'Cannot read resource file {self.path} because file permission error')
            logging.exception(e)
        except IOError as e:
            logging.error(f'Cannot read resource file {self.path} because IO error')
            logging.exception(e)


class EmptyResource(Resources):

    def __init__(self):
        super().__init__()
        self.content = None


class GeneralResource(FileResources):

    def __init__(self, path, mime=None):
        super().__init__(path)
        self.type = mime
        self.content = super().data

    def filetype(self):
        file_name, file_extension = os.path.splitext(self.path)
        return file_extension[1:]


class HTMLResource(FileResources):

    def __init__(self, path, encoding=None):
        super().__init__(path)
        self.ENCODE_ABLE = True
        self.encoding = encoding
        self.type = 'text/html'
        if self.encoding is None:
            self.content = super().data
        if self.encoding is EncodingMethod.GZIP:
            # TODO encode process
            pass


class CSSResource(FileResources):

    def __init__(self, path):
        super().__init__(path)
        self.ENCODE_ABLE = False
        self.type = 'text/css'
        self.content = super().data


class JavaScriptResource(FileResources):

    def __init__(self, path):
        super().__init__(path)
        self.type = 'application/javascript'
        self.content = super().data


class ResourceNotFoundError(Exception):
    # TODO error process
    pass


class PageNotFoundError(ResourceNotFoundError):

    pass


class IndexPageNotFoundError(PageNotFoundError):

    pass


class NotFoundPageNotFoundError(PageNotFoundError):

    pass

