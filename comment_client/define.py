# -*- coding: utf_8 -*-

"""
Common definition file
"""


__all__ = [""]


import logging
import inspect
import heapq
import itertools
from os import path
from time import time
from random import random
from queue import Queue
from enum import Enum
from enum import unique
try:
    import threading as threading
except ImportError:
    import dummy_threading as threading


UTF_8 = "utf_8" # encoding to use in this module

# known tags
KNOWN_TAGS = (
    "chat",
    "chat_result",
    "thread")

# localize log level
# TODO move to Log class as property
TRACE = 1 # level for trace of function call
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# TODO create common initialize function
# TODO move to common initialize function
DIRNAME = path.dirname(path.abspath(__file__))
LOGFILE = path.join(DIRNAME, "comment_client.log") # file name for log message output
LOGLEVEL = DEBUG # current log level

# configuration of root logger
# TODO move to common initialize function
# TODO add setting function used logging.configuration file
logging.basicConfig(
    filename=LOGFILE,
    filemode="w",
    format="%(asctime)s,%(msecs)d %(levelname)s %(name)s %(message)s",
    datefmt="%H:%M:%S",
    level=LOGLEVEL) # TODO ルートロガーへの設定は各ロガーへの設定に変更


class InnerException(Exception):
    """ Base exception in this module """
    pass


class InnerError(InnerException):
    """ Inner error exception """
    pass


class MatrixError(InnerException):
    """ Matrix error exception """
    pass


class BaseClass(object):
    """ Base class in this module """
    pass


@unique
class BaseEnum(Enum):
    """ Base class for each parallel process state """
    pass


class Wrapper(BaseClass):
    """ Wrapper of standard modules """
    @staticmethod
    def Thread(*args, **kwds):
        return threading.Thread(*args, **kwds)

    @staticmethod
    def Lock(*args, **kwds):
        return threading.Lock(*args, **kwds)

    @staticmethod
    def Event(*args, **kwds):
        return threading.Event(*args, **kwds)

    @staticmethod
    def Timer(*args, **kwds):
        return threading.Timer(*args, **kwds)

    @staticmethod
    def encode(text=None, errors='ignore'):
        """
        wrapper function of str.encode()
        convert to str from unicode
            encoding: encoding to use
            errors:
                'strict' (default)
                'ignore'
                'replace'
                'xmlcharrefreplace'
                'backslashreplace'
        """
        return text.encode(encoding=UTF_8, errors=errors)

    @staticmethod
    def decode(text=None, errors='ignore'):
        """
        wrapper function of str.decode()
        convert to unicode from str
            encoding: encoding to use
            errors:
                'strict' (default)
                'ignore'
                'replace'
        """
        return text.decode(encoding=UTF_8, errors=errors)
#        return text
#        return str(object=text, encoding=UTF_8, errors=errors)


# define interface class
class ElementInterface(BaseClass):
    def __init__(self, tag=None, attrs=None, text=None):
        self.__tag = tag
        self.__attrs = dict(attrs)
        self.__text = text

        self.__attrs.setdefault("no", "0")

    def __getattr__(self, name):
        if name in self.__attrs:
            return self.__attrs[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__, name))

    def __str__(self):
#        return Wrapper.encode("%(no)s:%(text)s" % {"no": self.no, "text": self.text})
        return self.text

    @property
    def tag(self):
        return self.__tag

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        self.__text = value

    @property
    def attrs(self):
        return self.__attrs


@unique
class UnitId(BaseEnum):
    """
    definition of unit ID
    used as id of message box for message destination
    """
    UNITCTRL = 0x0001
    CONNECTIONMNG = 0x0002
    SOCKETCTRL = 0x0003
    HTTPCTRL = 0x0004
    PARSEINFO = 0x0005
    TIMERMNG = 0x0009


@unique
class EventId(BaseEnum):
    """
    definition of event ID
    used in MessageContainer.event
    """
    CONNECTREQ = 0x0101
    CONNECTCNF = 0x0102
    SENDREQ = 0x0103
    SENDCNF = 0x0104
    DATANOTIFY = 0x0105
    DISCONNECTREQ = 0x0106
    DISCONNECTCNF = 0x0107
    SOCKETCONNECTREQ = 0x0201
    SOCKETCONNECTCNF = 0x0202
    SOCKETSENDREQ = 0x0203
    SOCKETSENDCNF = 0x0204
    SOCKETDISCONNECTREQ = 0x0207
    SOCKETDISCONNECTCNF = 0x0208
    SOCKETCLOSEDNOTIFY = 0x0209 # TODO case of receive '\0' data
    HTTPCOOKIEINITREQ = 0x0301
    HTTPCOOKIEINITCNF = 0x0302
    HTTPGETPLAYERSTATUSREQ = 0x0303
    HTTPGETPLAYERSTATUSRES = 0x0304
    HTTPGETPOSTKEYREQ = 0x0305
    HTTPGETPOSTKEYRES = 0x0306
    HTTPHEARTBEATREQ = 0x0307
    HTTPHEARTBEATRES = 0x0308
    PARSEREQ = 0x0401
    PARSERES = 0x0402
    CHATNOTIFY = 0x0501
    CHATRESULTNOTIFY = 0x0502
    THREADINFONOTIFY = 0x0503
    TIMERREQ = 0x0901


class MessageContainer(BaseClass):
    """ structure of message """
    def __init__(self, event=None, message=None, poison=False):
        self.__event = event
        self.__message = message
        self.__poison = poison

    @property
    def event(self):
        """ EventId is set """
        return self.__event

    @property
    def message(self):
        """ content of message """
        return self.__message

    @property
    def poison(self):
        """
        True set in the case of poison message
            True / False
        """
        return self.__poison


class TimerReq(BaseClass):
    """ structure of timer request """
    def __init__(self, interval, unit_id=None, event_id=None, data=None):
        self.__interval = interval
        self.__unit_id = unit_id
        self.__event_id = event_id
        self.__data = data

    @property
    def interval(self):
        return self.__interval

    @property
    def unit_id(self):
        return self.__unit_id

    @property
    def event_id(self):
        return self.__event_id

    @property
    def data(self):
        return self.__data


class SocketConnectReq(BaseClass):
    """ structure of socket connect confirm """
    def __init__(self, addr=None, port=None):
        self.__addr = addr
        self.__port = port

    @property
    def addr(self):
        return self.__addr

    @property
    def port(self):
        return self.__port


class SocketConnectCnf(BaseClass):
    """ structure of socket connect confirm """
    def __init__(self, id=None):
        self.__id = id

    @property
    def id(self):
        return self.__id


class SocketSendReq(BaseClass):
    """ structure of socket send request """
    def __init__(self, destination=None, data=None):
        self.__destination = destination
        self.__data = data

    @property
    def destination(self):
        return self.__destination

    @property
    def data(self):
        return self.__data


class SocketSendCnf(BaseClass):
    """ structure of socket send confirm """
    def __init__(self, destination=None, result=None):
        self.__destination = destination
        self.__result = result

    @property
    def destination(self):
        return self.__destination

    @property
    def result(self):
        return self.__result


class MessageBox(BaseClass):
    """
    Message Box used for parallel processing
    Used from each unit
    """
    # shared resource to use as message box
    # create for each unit
    share_resource = dict({
        UnitId.UNITCTRL: Queue(),
        UnitId.CONNECTIONMNG: Queue(),
        UnitId.SOCKETCTRL: Queue(),
        UnitId.HTTPCTRL: Queue(),
        UnitId.PARSEINFO: Queue(),
        UnitId.TIMERMNG: Queue()})

    @classmethod
    def send(cls, unit=None, container=None):
        cls.share_resource[unit].put(container, block=True, timeout=None)

    @classmethod
    def recv(cls, unit=None):
        return cls.share_resource[unit].get(block=True, timeout=None)

    @classmethod
    def poison(cls, unit=None):
        message = cls.createMessageContainer(event=None, message=None, poison=True)
        cls.send(unit=unit, container=message)

    @classmethod
    def createMessageContainer(cls, event=None, message=None, poison=False):
        return MessageContainer(event=event, message=message, poison=poison)


class MultiThreadClass(BaseClass):
    """ Base class for parallel processing in this module """
    def __init__(self, name=None, uniid=None, matrix=None, daemon=False):
        BaseClass.__init__(self)
        self.__log = Log(name=name, level=0)
        self.__name = name
        self.__uniid = uniid
        self.__job = Wrapper.Thread(
            group=None,
            target=self.main,
            name=name,
            kwargs={"matrix": matrix})
        self.__job.daemon = daemon
        self.__state = None

    @property
    def log(self):
        return self.__log

    @property
    def name(self):
        return self.__name

    @property
    def uniid(self):
        return self.__uniid

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    def main(self, matrix=None):
        """ main loop for parallel processing """
        self.log.trace()
        while True:
            message = self.recv_message()
            if message.poison:
                self.log.info("exit for poison message")
                break
            self.log.debug(
                "recv message. event:%s state:%s",
                message.event,
                self.state)
            result = matrix[message.event][self.state](message)
            if not result:
                self.log.error(
                    "matrix error. event:%s state:%s",
                    message.event,
                    self.state)

    def run(self):
        self.log.trace()
        if not self.__job.is_alive():
            self.__job.start()

    def kill(self):
        self.log.trace()
        MessageBox.poison(unit=self.uniid)
        self.__job.join()

    def recv_message(self):
        self.log.trace()
        message = MessageBox.recv(unit=self.uniid)
        return message

    def send_message(self, unit=None, event=None, message=None):
        self.log.trace()
        container = MessageBox.createMessageContainer(event, message)
        result = MessageBox.send(unit, container)
        return result


class Unique(BaseClass):
    """ class for unique string """
    __last = 0

    @classmethod
    def unique(cls):
        uni = "".join(["".join(str(time()).split(".")), "".join(str(random()).split("."))])
        if cls.__last != uni:
            cls.__last = uni
            return uni
        else:
            return cls.unique(cls)

class Log(BaseClass):
    """ custom Logger class for each modules """
    def __init__(self, name=None, level=INFO):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)
        file_handler = logging.FileHandler(
            path.join(DIRNAME, ".".join([name.split(".")[-1], "log"])),
            mode="w",
            encoding=None,
            delay=False)
        file_handler.setLevel(level)
        self.__logger.addHandler(file_handler)
        self.__level = level

    def trace(self):
        """ function for trace of function call """
        if self.__logger.isEnabledFor(self.__level):
            try:
                frame = inspect.currentframe()
                if frame is not None:
                    if frame.f_back is not None:
                        self.__logger.log(
                            TRACE,
                            "%s:%d %s",
                            frame.f_back.f_code.co_filename,
                            frame.f_back.f_lineno,
                            frame.f_back.f_code.co_name)
            finally:
                del frame

    def debug(self, msg, *args, **kwargs):
        """ wrapper function of logger.debug() """
        self.__logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """ wrapper function of logger.info() """
        self.__logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """ wrapper function of logger.warning() """
        self.__logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """ wrapper function of logger.error() """
        self.__logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """ wrapper function of logger.critical() """
        self.__logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """ wrapper function of logger.exception() """
        self.__logger.exception(msg, *args, **kwargs)


if __name__ == "__main__":
    pass


