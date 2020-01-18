# -*- coding: utf_8 -*-


__all__ = [""]


import socket

from comment_client.define import Wrapper
from comment_client.define import BaseClass
from comment_client.define import MultiThreadClass
from comment_client.define import Log
from comment_client.define import MessageBox
from comment_client.define import EventId
from comment_client.define import UnitId
from comment_client.define import BaseEnum
from comment_client.define import SocketConnectCnf
from comment_client.define import SocketSendCnf


class SocketCtrl(MultiThreadClass):
    def __init__(self, daemon=False):
        matrix = {
            EventId.SOCKETCONNECTREQ: {
                self.__StateId.IDLE: self.__idle_socketconnectreq,
                self.__StateId.RECEIVING: self.__receiving_socketconnectreq},
            EventId.SOCKETSENDREQ: {
                self.__StateId.IDLE: self.__idle_socketsendreq,
                self.__StateId.RECEIVING: self.__receiving_socketsendreq},
            EventId.SOCKETDISCONNECTREQ: {
                self.__StateId.IDLE: self.__idle_socketdisconnectreq,
                self.__StateId.RECEIVING: self.__receiving_socketdisconnectreq}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.SOCKETCTRL,
            matrix=matrix,
            daemon=daemon)

        self.__socket_info = dict()
        self.__main_socket = None
        self.__socket = None
        self.__bufsize = 2048

        self.__flag_loop = None
        self.__job_loop = None
        self.__lock = Wrapper.Lock()

        self.state = self.__StateId.IDLE

    def __callback(self, data=None, no=None):
        self.__lock.acquire(blocking = True, timeout = -1)
        result = self.send_message(
                    UnitId.PARSEINFO,
                    EventId.PARSEREQ,
                    data)
        self.__lock.release()
        return result

    def __idle_socketconnectreq(self, container):
        self.log.trace()

        socket_info = self.__SocketInfo(
            addr = container.message.addr,
            port = container.message.port,
            bufsize = self.__bufsize,
            callback = self.__callback)

        self.__main_socket = socket_info.getno()

        self.__socket_info[self.__main_socket] = socket_info

        self.__socket_info[self.__main_socket].connect()
        self.__socket_info[self.__main_socket].start()

        result = self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.SOCKETCONNECTCNF,
            SocketConnectCnf(
                id = self.__main_socket))

        self.state = self.__StateId.RECEIVING
        return True

    def __receiving_socketconnectreq(self, container):
        self.log.trace()
        socket_info = self.__SocketInfo(
            addr = container.message.addr,
            port = container.message.port,
            bufsize = self.__bufsize,
            callback = self.__callback)

        socket_no = socket_info.getno()

        self.__socket_info[socket_no] = socket_info

        self.__socket_info[socket_no].connect()
        self.__socket_info[socket_no].start()

        result = self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.SOCKETCONNECTCNF,
            SocketConnectCnf(
                id = socket_no))

        self.state = self.__StateId.RECEIVING
        return True

    def __idle_socketsendreq(self, container):
        self.log.trace()
        pass

    def __receiving_socketsendreq(self, container):
        self.log.trace()
        result = self.__socket_info[self.__main_socket].send(
            container.message.data)

        self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.SOCKETSENDCNF,
            SocketSendCnf(
                destination = container.message.destination,
                result = result))

        self.state = self.__StateId.RECEIVING
        return True

    def __idle_socketdisconnectreq(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.SOCKETDISCONNECTCNF,
            None)

        self.state = self.__StateId.IDLE
        return True

    def __receiving_socketdisconnectreq(self, container):
        self.log.trace()
        for index in self.__socket_info:
            self.__socket_info[index].stop()
            self.__socket_info[index].close()
            del self.__socket_info[index]

        result = self.send_message(
            UnitId.CONNECTIONMNG,
            EventId.SOCKETDISCONNECTCNF,
            True)

        self.state = self.__StateId.IDLE
        return True


    # define inner state
    class __StateId(BaseEnum):
        IDLE = 0x00
        RECEIVING = 0x01


    class __SocketInfo(BaseClass):
    # 未使用 複数のソケットに対して同時に接続するために使うクラス
    # 配列に保持し、管理する
    # 立ち見コメント取得用
        def __init__(self, addr=None, port=None, bufsize=1024, callback=None):
            self.addr = addr
            self.port = port
            self.bufsize = bufsize
            self.__callback = callback
            self.__socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
            self.__flag = None
            self.__job = None
            self.log = Log(__name__)

        def __loop(self, stop_event=None):
            """
            ソケットから0だけが返ってきた場合、相手側からリジェクトされたものとみなしたほうが良いかもしれない。
            そのばあいの再接続シーケンスのためには、リジェクトを通知するイベントが必要。
            （ソケット機能部だけでは、初回のチケット取得が行えないため。）
            イベントはまだ実装していない。
            """
            self.log.trace()
            while stop_event.wait(0):
                data = self.recv()
#               self.log.info("%s", data)
                if data:
                    # parse処理がシーケンシャルになるとエラーが出るかもしれない。
                    # ソケット毎のparse処理ができるように変更する必要がある。
                    result = self.__callback(data=data, no=self.getno())
                else:
                    # case of socket closed
                    self.log.info("Receive end message of XMLSocket")

        def getno(self):
            return self.__socket.fileno()

        def start(self):
            self.log.trace()
            self.__flag = Wrapper.Event()
            self.__job = Wrapper.Thread(
                group=None,
                target=self.__loop,
                name=None,
                kwargs={"stop_event": self.__flag})
            self.__job.daemon = True
            self.__flag.set()
            self.__job.start()

        def stop(self):
            self.log.trace()
            self.__flag.clear()
            self.__job.join()

        def connect(self, addr=None, port=None):
            self.log.trace()
            self.__socket.connect((self.addr, int(self.port)))

        def close(self):
            self.log.trace()
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()

        def send(self, data):
            self.log.trace()
            sendData = Wrapper.encode(data + "\0")
            dataByte = len(sendData)
            sendByte = self.__socket.send(sendData)
            if dataByte == sendByte:
                return True
            else:
                return False

        def recv(self):
            """
            TODO
            受信したデータはstr型
            len()でバイト数が0なら受診なしとみなしてNoneを返すようにする。
                len('\0') = 1 になるため、受信データ = '\0' の場合にNoneを返す。
            呼び出し元はNoneなら受信なしとして、ソケットがクローズされたものとみなす。
            """
            self.log.trace()
            data = self.__socket.recv(self.bufsize)
            unidata = Wrapper.decode(data)
            unidata = unidata.replace("\0", "")
            return unidata


if __name__ == "__main__":
    pass


