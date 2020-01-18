# -*- coding: utf_8 -*-


__all__ = [""]


from http import cookiejar
from urllib import request

from comment_client.define import Wrapper
from comment_client.define import MultiThreadClass
from comment_client.define import MessageBox
from comment_client.define import EventId
from comment_client.define import UnitId
from comment_client.define import BaseEnum


# define inner state
class _StateId(BaseEnum):
    INIT = 0x00
    IDLE = 0x01


class HttpCtrl(MultiThreadClass):
    def __init__(self, daemon=False):
        # create function table
        matrix = {
            EventId.HTTPCOOKIEINITREQ: {
                _StateId.INIT: self.__init_httpcookieinitreq,
                _StateId.IDLE: self.__idle_httpcookieinitreq},
            EventId.HTTPGETPLAYERSTATUSREQ: {
                _StateId.INIT: self.__init_httpgetplayerstatusreq,
                _StateId.IDLE: self.__idle_httpgetplayerstatusreq},
            EventId.HTTPGETPOSTKEYREQ: {
                _StateId.INIT: self.__init_httpgetpostkeyreq,
                _StateId.IDLE: self.__idle_httpgetpostkeyreq},
            EventId.HTTPHEARTBEATREQ: {
                _StateId.INIT: self.__init_httpheartbeatreq,
                _StateId.IDLE: self.__idle_httpheartbeatreq}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.HTTPCTRL,
            matrix=matrix,
            daemon=daemon)

        self.__openerDirector = None
        self.__cookieJar = None
        self.__httpCookieProcessor = None
        self.__defaultCookiePolicy = None

        self.state = _StateId.INIT

    def __create_cookie(self, data):
        self.log.trace()
        return cookiejar.Cookie(
            version = data["version"],
            name = data["name"],
            value = data["value"],
            port = data["port"],
            port_specified = data["port_specified"],
            domain = data["domain"],
            domain_specified = data["domain_specified"],
            domain_initial_dot = data["domain_initial_dot"],
            path = data["path"],
            path_specified = data["path_specified"],
            secure = data["secure"],
            expires = data["expires"],
            discard = data["discard"],
            comment = data["comment"],
            comment_url = data["comment_url"],
            rest = data["rest"],
            rfc2109 = data["rfc2109"])

    def __make_opener(self, cookie, data):
        self.log.trace()
        self.__defaultCookiePolicy = cookiejar.DefaultCookiePolicy()
#        self.__cookieJar = cookiejar.CookieJar(policy = self.__defaultCookiePolicy)
        self.__cookieJar = cookiejar.CookieJar()
        self.__cookieJar.set_cookie(cookie)
        self.__httpCookieProcessor = request.HTTPCookieProcessor(self.__cookieJar)
        self.__openerDirector = request.build_opener(self.__httpCookieProcessor)
        self.__openerDirector.addheaders = [data["user_agent"]]

    def __get_response(self, url):
        self.log.trace()
        self.log.info(
            "open URL %s",
            url)
        response = self.__openerDirector.open(url)
        data = Wrapper.decode(response.read())
        self.log.info(
            "response data %s",
            data)
        response.close()
        return data

    def __init_httpcookieinitreq(self, container):
        self.log.trace()
        cookie = self.__create_cookie(container.message)
        self.__make_opener(cookie, container.message)

        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.HTTPCOOKIEINITCNF,
            None)

        self.state = _StateId.IDLE
        return True

    def __idle_httpcookieinitreq(self, container):
        self.log.trace()
        cookie = self.__create_cookie(container.message)
        self.__make_opener(cookie, container.message)

        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.HTTPCOOKIEINITCNF,
            None)

        self.state = _StateId.IDLE
        return True

    def __init_httpgetplayerstatusreq(self, container):
        self.log.trace()
        pass

    def __idle_httpgetplayerstatusreq(self, container):
        self.log.trace()
        data = self.__get_response(container.message)
        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.HTTPGETPLAYERSTATUSRES,
            data)

        self.state = _StateId.IDLE
        return True

    def __init_httpgetpostkeyreq(self, container):
        self.log.trace()
        pass

    def __idle_httpgetpostkeyreq(self, container):
        self.log.trace()
        data = self.__get_response(container.message)
        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.HTTPGETPOSTKEYRES,
            data)

        self.state = _StateId.IDLE
        return True

    def __init_httpheartbeatreq(self, container):
        self.log.trace()
        pass

    def __idle_httpheartbeatreq(self, container):
        self.log.trace()
        data = self.__get_response(container.message)
        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.HTTPHEARTBEATRES,
            data)

        self.state = _StateId.IDLE
        return True

if __name__ == "__main__":
    pass


