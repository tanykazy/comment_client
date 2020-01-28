# -*- coding: utf_8 -*-


__all__ = [""]


from html.parser import HTMLParser

from define import BaseClass
from define import MultiThreadClass
from define import ElementInterface
from define import KNOWN_TAGS
from define import MessageBox
from define import EventId
from define import UnitId
from define import BaseEnum


class ParseInfo(MultiThreadClass):
    """
    Parser
    """
    def __init__(self, daemon=False):

        matrix = {
            EventId.PARSEREQ: {
                self.__StateId.IDLE: self.__idle_parsereq}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.PARSEINFO,
            matrix=matrix,
            daemon=daemon)

        self.state = self.__StateId.IDLE

        self.__parser = self.__Parser(
            logger=self.log,
            callback=self.__handler)

    def __handler(self, element=None):
        self.log.trace()
        if element.tag == "chat":
            self.send_message(
                UnitId.CONNECTIONMNG,
                EventId.CHATNOTIFY,
                element)
        elif element.tag == "chat_result":
            self.send_message(
                UnitId.CONNECTIONMNG,
                EventId.CHATRESULTNOTIFY,
                element)
        elif element.tag == "thread":
            self.send_message(
                UnitId.CONNECTIONMNG,
                EventId.THREADINFONOTIFY,
                element)
        else:
            self.__logger.error(
                "Inner Error %s",
                element)

    def __idle_parsereq(self, container):
        self.log.trace()
#        safeData = container.message.decode(encoding="utf-8", errors="strict")
#        self.__parser.feed(safeData)
        self.__parser.feed(container.message)
        return True


    # define inner state
    class __StateId(BaseEnum):
        IDLE = 0x00


    class __Parser(BaseClass, HTMLParser):
        """
        inner class of html parser
        """
        def __init__(self, logger=None, callback=None):
            HTMLParser.__init__(self)
            self.__logger = logger
            self.__stack = list()
            self.__data = list()
            self.__callback = callback

        def handle_starttag(self, tag, attrs):
            self.__logger.trace()
            if self.__data:
                self.__logger.error(
                    "missing data %s",
                    self.__data)

            if not tag in KNOWN_TAGS:
                self.__logger.error(
                    "unknown tag detected %s %s",
                    tag,
                    attrs)
            else:
                if self.__stack:
                    self.__logger.error(
                        "missing start tag %s %s",
                        tag,
                        attrs)
                else:
                    element = ElementInterface(tag, attrs=attrs)
                    self.__stack.append(element)
                    self.__data = list()

        def handle_endtag(self, tag):
            self.__logger.trace()
            if not self.__stack:
                self.__logger.error(
                    "missing end tag %s",
                    tag)
            else:
                if self.__stack[-1].tag != tag:
                    self.__logger.error(
                        "mismatch end tag %s",
                        tag)
                else:
                    element = self.__stack.pop()
                    element.text = "".join(self.__data)
                    # execute callback function to notify element
                    self.__callback(element=element)
                    self.__data = list()

        def handle_data(self, data):
            self.__logger.trace()
            self.__data.append(data)


if __name__ == "__main__":
    pass


