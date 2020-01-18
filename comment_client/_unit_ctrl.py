# -*- coding: utf_8 -*-


__all__ = [""]


from comment_client._session_mng import SessionMng
from comment_client._socket_ctrl import SocketCtrl
from comment_client._http_ctrl import HttpCtrl
from comment_client._parse_info import ParseInfo
from comment_client._timer_mng import TimerMng
from comment_client.define import Wrapper
from comment_client.define import MultiThreadClass
from comment_client.define import MessageBox
from comment_client.define import EventId
from comment_client.define import UnitId
from comment_client.define import BaseEnum


class UnitCtrl(MultiThreadClass):
    def __init__(self, handle=None):
        matrix = {
            EventId.CONNECTREQ: {
                self.__StateId.INIT: self.__init_connectreq,
                self.__StateId.CONNECTED: self.__connected_connectreq},
            EventId.CONNECTCNF: {
                self.__StateId.INIT: self.__init_connectcnf,
                self.__StateId.CONNECTED: self.__connected_connectcnf},
            EventId.SENDCNF: {
                self.__StateId.INIT: self.__init_sendcnf,
                self.__StateId.CONNECTED: self.__connected_sendcnf},
            EventId.DATANOTIFY: {
                self.__StateId.INIT: self.__init_datanotify,
                self.__StateId.CONNECTED: self.__connected_datanotify},
            EventId.DISCONNECTREQ: {
                self.__StateId.INIT: self.__init_disconnectreq,
                self.__StateId.CONNECTED: self.__connected_disconnectreq},
            EventId.DISCONNECTCNF: {
                self.__StateId.INIT: self.__init_disconnectcnf,
                self.__StateId.CONNECTED: self.__connected_disconnectcnf}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.UNITCTRL,
            matrix=matrix,
            daemon=False)

        self.__handle = handle

        self.__sync = {
            "lock": Wrapper.Lock(),
            "event": {
                "connect": Wrapper.Event(),
                "disconnect": Wrapper.Event()}}

        common_daemon_flug = False
        self.__session_mng = SessionMng(daemon=common_daemon_flug)
        self.__socket_ctrl = SocketCtrl(daemon=common_daemon_flug)
        self.__http_ctrl = HttpCtrl(daemon=common_daemon_flug)
        self.__parse_info = ParseInfo(daemon=common_daemon_flug)
        self.__timer_mng = TimerMng(daemon=common_daemon_flug)

        self.state = self.__StateId.INIT

    def start(self):
        self.log.trace()
        self.__session_mng.run()
        self.__socket_ctrl.run()
        self.__http_ctrl.run()
        self.__parse_info.run()
        self.__timer_mng.run()
        self.run()

    def stop(self):
        self.log.trace()
        self.__session_mng.kill()
        self.__socket_ctrl.kill()
        self.__http_ctrl.kill()
        self.__parse_info.kill()
        self.__timer_mng.kill()
#        if self.state == self.__StateId.CONNECTED:
#            self.disconnectReq()
        self.kill()
#        self.__handle_comment = None

    def connect(self, url):
        self.log.trace()
        self.__sync["lock"].acquire(True)
        self.__sync["event"]["connect"].clear()
#        unidata = Wrapper.decode(url)
        unidata = url
        self.send_message(
            UnitId.UNITCTRL,
            EventId.CONNECTREQ,
            unidata)
        self.__sync["event"]["connect"].wait()
        self.__sync["lock"].release()

    def disconnect(self):
        self.log.trace()
        self.__sync["lock"].acquire(True)
        self.__sync["event"]["disconnect"].clear()
        self.send_message(
            UnitId.UNITCTRL,
            EventId.DISCONNECTREQ,
            None)
        self.__sync["event"]["disconnect"].wait()
        self.__sync["lock"].release()

    def send(self, data=None, sync=False):
        self.log.trace()
#        unidata = Wrapper.decode(data)
        unidata = data
        if len(unidata) != 0:
            self.send_message(
                UnitId.CONNECTIONMNG,
                EventId.SENDREQ,
                unidata)

    def __init_connectreq(self, container):
        self.log.trace()
        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.CONNECTREQ,
            container.message)

        self.state = self.__StateId.INIT
        return True

    def __connected_connectreq(self, container):
        self.log.trace()
        pass

    def __init_connectcnf(self, container):
        self.log.trace()
        self.log.info("unit_ctrl: receive event of <connect_cnf>")
        if container.message:
            self.state = self.__StateId.CONNECTED
        else:
            # TODO failure connect request
            pass

        self.__sync["event"]["connect"].set()
        return True

    def __connected_connectcnf(self, container):
        self.log.trace()
        pass

    def __init_sendcnf(self, container):
        self.log.trace()
        pass

    def __connected_sendcnf(self, container):
        self.log.trace()

        self.state = self.__StateId.CONNECTED
        return True

    def __init_datanotify(self, container):
        self.log.trace()
        pass

    def __connected_datanotify(self, container):
        self.log.trace()

        self.__handle(
            container.message.text,
            tag = container.message.tag,
            **container.message.attrs)

        self.state = self.__StateId.CONNECTED
        return True

    def __init_disconnectreq(self, container):
        self.log.trace()
        pass

    def __connected_disconnectreq(self, container):
        self.log.trace()

        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.DISCONNECTREQ,
            container.message)

        self.state = self.__StateId.CONNECTED
        return True

    def __init_disconnectcnf(self, container):
        self.log.trace()
        pass

    def __connected_disconnectcnf(self, container):
        self.log.trace()
        self.log.info("unit_ctrl: receive event of <disconnect_cnf>")
        if container.message:
            self.state = self.__StateId.INIT
        else:
            # TODO failure disconnect request
            pass

        self.__sync["event"]["disconnect"].set()
        return True


    # define inner state
    class __StateId(BaseEnum):
        INIT = 0x00
        CONNECTED = 0x01


if __name__ == "__main__":
    pass


