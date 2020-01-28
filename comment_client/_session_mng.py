# -*- coding: utf_8 -*-


__all__ = [""]


from collections import deque

from api_info import ApiInfo
from login_info import LoginInfo
from define import MultiThreadClass
from define import MessageBox
from define import EventId
from define import UnitId
from define import BaseEnum
from define import BaseClass
from define import TimerReq
from define import SocketConnectReq
from define import SocketSendReq
from define import Wrapper


class SessionMng(MultiThreadClass):
    def __init__(self, daemon=False):
        # create function table
        matrix = {
            EventId.CONNECTREQ: {
                self.__StateId.INIT: self.__init_connectreq,
                self.__StateId.CONNECTING: self.__connecting_connectreq,
                self.__StateId.IDLE: self.__idle_connectreq,
                self.__StateId.CHATSENDING: self.__chatsending_connectreq},
            EventId.SENDREQ: {
                self.__StateId.INIT: self.__init_sendreq,
                self.__StateId.CONNECTING: self.__connecting_sendreq,
                self.__StateId.IDLE: self.__idle_sendreq,
                self.__StateId.CHATSENDING: self.__chatsending_sendreq},
            EventId.HTTPCOOKIEINITCNF: {
                self.__StateId.INIT: self.__init_httpcookieinitcnf,
                self.__StateId.CONNECTING: self.__connecting_httpcookieinitcnf,
                self.__StateId.IDLE: self.__idle_httpcookieinitcnf,
                self.__StateId.CHATSENDING: self.__chatsending_httpcookieinitcnf},
            EventId.HTTPGETPLAYERSTATUSRES: {
                self.__StateId.INIT: self.__init_httpgetplayerstatusres,
                self.__StateId.CONNECTING: self.__connecting_httpgetplayerstatusres,
                self.__StateId.IDLE: self.__idle_httpgetplayerstatusres,
                self.__StateId.CHATSENDING: self.__chatsending_httpgetplayerstatusres},
            EventId.HTTPGETPOSTKEYRES: {
                self.__StateId.INIT: self.__init_httpgetpostkeyres,
                self.__StateId.CONNECTING: self.__connecting_httpgetpostkeyres,
                self.__StateId.IDLE: self.__idle_httpgetpostkeyres,
                self.__StateId.CHATSENDING: self.__chatsending_httpgetpostkeyres},
            EventId.HTTPHEARTBEATRES: {
                self.__StateId.INIT: self.__init_httpheartbeatres,
                self.__StateId.CONNECTING: self.__connecting_httpheartbeatres,
                self.__StateId.IDLE: self.__idle_httpheartbeatres,
                self.__StateId.CHATSENDING: self.__chatsending_httpheartbeatres},
            EventId.SOCKETCONNECTCNF: {
                self.__StateId.INIT: self.__init_socketconnectcnf,
                self.__StateId.CONNECTING: self.__connecting_socketconnectcnf,
                self.__StateId.IDLE: self.__idle_socketconnectcnf,
                self.__StateId.CHATSENDING: self.__chatsending_socketconnectcnf},
            EventId.SOCKETSENDCNF: {
                self.__StateId.INIT: self.__init_socketsendcnf,
                self.__StateId.CONNECTING: self.__connecting_socketsendcnf,
                self.__StateId.IDLE: self.__idle_socketsendcnf,
                self.__StateId.CHATSENDING: self.__chatsending_socketsendcnf},
            EventId.SOCKETDISCONNECTCNF: {
                self.__StateId.INIT: self.__init_socketdisconnectcnf,
                self.__StateId.CONNECTING: self.__connecting_socketdisconnectcnf,
                self.__StateId.IDLE: self.__idle_socketdisconnectcnf,
                self.__StateId.CHATSENDING: self.__chatsending_socketdisconnectcnf},
            EventId.CHATNOTIFY: {
                self.__StateId.INIT: self.__init_chatnotify,
                self.__StateId.CONNECTING: self.__connecting_chatnotify,
                self.__StateId.IDLE: self.__idle_chatnotify,
                self.__StateId.CHATSENDING: self.__chatsending_chatnotify},
            EventId.CHATRESULTNOTIFY: {
                self.__StateId.INIT: self.__init_chatresultnotify,
                self.__StateId.CONNECTING: self.__connecting_chatresultnotify,
                self.__StateId.IDLE: self.__idle_chatresultnotify,
                self.__StateId.CHATSENDING: self.__chatsending_chatresultnotify},
            EventId.THREADINFONOTIFY: {
                self.__StateId.INIT: self.__init_threadinfonotify,
                self.__StateId.CONNECTING: self.__connecting_threadinfonotify,
                self.__StateId.IDLE: self.__idle_threadinfonotify,
                self.__StateId.CHATSENDING: self.__chatsending_threadinfonotify},
            EventId.DISCONNECTREQ: {
                self.__StateId.INIT: self.__init_disconnectReq,
                self.__StateId.CONNECTING: self.__connecting_disconnectReq,
                self.__StateId.IDLE: self.__idle_disconnectReq,
                self.__StateId.CHATSENDING: self.__chatsending_disconnectReq}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.CONNECTIONMNG,
            matrix=matrix,
            daemon=daemon)

        self.__task = deque()
        self.__live = dict()
        self.__main_socket = None
        self.__socket_info = list()

        # initialize inner state
        self.state = self.__StateId.INIT

        self.__init_live_info()

    def __add_socket_info(self, addr, port, thread, id=None):
        if not self.__socket_info[addr]:
            self.__socket_info[addr] = dict()

        self.__socket_info[addr][port] = id

    def __del_socket_info(self):
        self.__socket_info = dict()

    def __init_live_info(self):
        self.log.trace()
        self.__live = {
            "liveId": None,
            "chatCount": int(0),
            "chat": {
                "no": int(0)},
            "thread": {
                "thread": None,
                "last_res": None,
                "ticket": None,
                "server_time": None},
            "playerstatus": {
                "addr": None,
                "port": None,
                "thread": None,
                "ticket": None,
                "user_id": None,
                "is_premium": None,
                "start_time": None},
            "block_no": int(0),
            "postkey": None,
            "omsg": False,
            "msg": False}
        self.__task.clear()

    def __save_playerstatus(self, data):
        self.log.trace()
        playerstatus = ApiInfo.expandDom(data)
        self.__live["playerstatus"]["addr"] = playerstatus["addr"]
        self.__live["playerstatus"]["port"] = playerstatus["port"]
        self.__live["playerstatus"]["thread"] = playerstatus["thread"]
        self.__live["playerstatus"]["ticket"] = playerstatus["ticket"]
        self.__live["playerstatus"]["user_id"] = playerstatus["user_id"]
        self.__live["playerstatus"]["is_premium"] = playerstatus["is_premium"]
        self.__live["playerstatus"]["start_time"] = playerstatus["start_time"]
        self.log.info(
            "liveInfo(%s)",
            self.__live)

    def __save_thread(self, data):
        self.log.trace()
        self.__live["thread"]["thread"] = data["thread"]
#        self.__live["thread"]["last_res"] = data["last_res"]
        self.__live["thread"]["ticket"] = data["ticket"]
        self.__live["thread"]["server_time"] = data["server_time"]
        self.log.info(
            "liveInfo(%s)",
            self.__live)

    def __create_chat_tag(self, text):
        self.log.trace()
        return ApiInfo.createChatTag(
            thread = self.__live["playerstatus"]["thread"],
#            ticket = self.__live["thread"]["ticket"],
            ticket = self.__live["playerstatus"]["ticket"],
            vpos = ApiInfo.calculateDiffTime(),
            postkey = self.__live["postkey"],
            locale = ApiInfo.LOCALE,
            user_id = self.__live["playerstatus"]["user_id"],
            premium = self.__live["playerstatus"]["is_premium"],
            mail = ApiInfo.MAIL,
            text = text)

    def __decide_whether_need_postkey(self, no=None):
        """ decide whether need postkey. """
        self.log.trace()
        if int(no) == 0:
            self.__live["chatCount"] += 1
        else:
            self.__live["chatCount"] = int(no)
        
        block_no = ApiInfo.calculateBlockNo(no=self.__live["chatCount"])
        if self.__live["block_no"] != block_no:
            self.__live["block_no"] = block_no
            return True
        else:
            return False

    def __send_timerreq_heartbeatreq(self, live_id=None, wait_time=60):
        self.log.trace()
        data = ApiInfo.createHeartbeatUrl(live_id = live_id)
        result = self.send_message(
            UnitId.TIMERMNG,
            EventId.TIMERREQ,
            TimerReq(
                interval = wait_time,
                unit_id = UnitId.HTTPCTRL,
                event_id = EventId.HTTPHEARTBEATREQ,
                data = data))
        return result

    def __storeSendDataStore(self, data):
        self.log.trace()
        self.__task.append(data)

    def __restoreSendDataStore(self):
        self.log.trace()
        if self.__task:
            return self.__task[0]
        else:
            return None

    def __cleanupSendDataStore(self):
        self.log.trace()
        self.__task.popleft()

    def __init_connectreq(self, container):
        self.log.trace()
        live_id = ApiInfo.extractLiveId(container.message)
        if live_id is None:
            result = self.send_message(
                UnitId.UNITCTRL,
                EventId.CONNECTCNF,
                False)
            return False

        self.__live["liveId"] = live_id
        user_session = LoginInfo.get_login_info()

        if user_session is None:
            result = self.send_message(
                UnitId.UNITCTRL,
                EventId.CONNECTCNF,
                False)
            return False

        self.send_message(
            UnitId.HTTPCTRL,
            EventId.HTTPCOOKIEINITREQ,
            {
                "version": ApiInfo.VERSION,
                "name": ApiInfo.NAME,
                "value": user_session,
                "port": ApiInfo.PORT,
                "port_specified": ApiInfo.PORT_SPECIFIED,
                "domain": ApiInfo.DOMAIN,
                "domain_specified": ApiInfo.DOMAIN_SPECIFIED,
                "domain_initial_dot": ApiInfo.DOMAIN_INITIAL_DOT,
                "path": ApiInfo.PATH,
                "path_specified": ApiInfo.PATH_SPECIFIED,
                "secure": ApiInfo.SECURE,
                "expires": ApiInfo.EXPIRES,
                "discard": ApiInfo.DISCARD,
                "comment": ApiInfo.COMMENT,
                "comment_url": ApiInfo.COMMENT_URL,
                "rest": ApiInfo.REST,
                "rfc2109": ApiInfo.RFC2109,
                "user_agent": ApiInfo.USER_AGENT
            })

        self.state = self.__StateId.CONNECTING
        return True

    def __connecting_connectreq(self, container):
        self.log.trace()
        pass

    def __idle_connectreq(self, container):
        self.log.trace()
        pass

    def __chatsending_connectreq(self, container):
        self.log.trace()
        pass

    def __init_sendreq(self, container):
        self.log.trace()
        pass

    def __connecting_sendreq(self, container):
        self.log.trace()
        pass

    def __idle_sendreq(self, container):
        self.log.trace()

        chatTag = self.__create_chat_tag(container.message)
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETSENDREQ,
            SocketSendReq(
                destination = self.__main_socket,
                data = chatTag
            ))

        self.__storeSendDataStore(container.message)

        self.state = self.__StateId.CHATSENDING
        return True

    def __chatsending_sendreq(self, container):
        self.log.trace()

        self.__storeSendDataStore(container.message)

        self.state = self.__StateId.CHATSENDING
        return True

    def __init_httpcookieinitcnf(self, container):
        self.log.trace()
        pass

    def __connecting_httpcookieinitcnf(self, container):
        self.log.trace()

        getplayerstatusUrl = ApiInfo.createGetplayerstatusUrl(self.__live["liveId"])
        result = self.send_message(
            UnitId.HTTPCTRL,
            EventId.HTTPGETPLAYERSTATUSREQ,
            getplayerstatusUrl)

        self.state = self.__StateId.CONNECTING
        return True

    def __idle_httpcookieinitcnf(self, container):
        self.log.trace()
        pass

    def __chatsending_httpcookieinitcnf(self, container):
        self.log.trace()
        pass

    def __init_httpgetplayerstatusres(self, container):
        self.log.trace()
        self.log.warning(
            "Discard message from the http_ctrl %s",
            container.message)
        return True

    def __connecting_httpgetplayerstatusres(self, container):
        self.log.trace()

        self.__save_playerstatus(container.message)
        server_type = ApiInfo.detectServerType(self.__live["playerstatus"]["addr"])
        self.__live[server_type] = True

        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETCONNECTREQ,
            SocketConnectReq(
                addr = self.__live["playerstatus"]["addr"],
                port = self.__live["playerstatus"]["port"]))

        self.__live["block_no"] = ApiInfo.calculateBlockNo(no=self.__live["chat"]["no"])
        data = ApiInfo.createGetpostkeyUrl(
            thread = self.__live["playerstatus"]["thread"],
            block_no = self.__live["block_no"])

        result = self.send_message(
            UnitId.HTTPCTRL,
            EventId.HTTPGETPOSTKEYREQ,
            data)

        self.__send_timerreq_heartbeatreq(live_id = self.__live["liveId"])

        self.state = self.__StateId.CONNECTING
        return True

    def __idle_httpgetplayerstatusres(self, container):
        self.log.trace()

        self.log.warning(
            "Discard message from the http_ctrl %s",
            container.message)

        self.state = self.__StateId.IDLE
        return True

    def __chatsending_httpgetplayerstatusres(self, container):
        self.log.trace()

        self.log.warning(
            "Discard message from the http_ctrl %s",
            container.message)

        data = self.__restoreSendDataStore()
        if data != None:
            chatTag = self.__create_chat_tag(data)
            result = self.send_message(
                UnitId.SOCKETCTRL,
                EventId.SOCKETSENDREQ,
                SocketSendReq(
                    destination = self.__main_socket,
                    data = chatTag))

        self.state = self.__StateId.CHATSENDING
        return True

    def __init_httpgetpostkeyres(self, container):
        self.log.trace()
        self.log.warning(
            "Discard message from the http_ctrl %s",
            container.message)
        return True

    def __connecting_httpgetpostkeyres(self, container):
        self.log.trace()
        pass

    def __idle_httpgetpostkeyres(self, container):
        self.log.trace()

        self.__live["postkey"] = ApiInfo.extractPostkey(postkey=container.message)
        self.log.info(
            "postkey(%s)",
            self.__live["postkey"])

        self.state = self.__StateId.IDLE
        return True

    def __chatsending_httpgetpostkeyres(self, container):
        self.log.trace()

        self.__live["postkey"] = ApiInfo.extractPostkey(postkey=container.message)
        self.log.info(
            "postkey(%s)",
            self.__live["postkey"])

        data = self.__restoreSendDataStore()
        if data != None:
            chatTag = self.__create_chat_tag(data)
            result = self.send_message(
                UnitId.SOCKETCTRL,
                EventId.SOCKETSENDREQ,
                SocketSendReq(
                    destination = self.__main_socket,
                    data = chatTag))

        self.state = self.__StateId.CHATSENDING
        return True

    def __init_httpheartbeatres(self, container):
        self.log.trace()
        self.log.warning(
            "Discard message from the http_ctrl %s",
            container.message)
        return True

    def __connecting_httpheartbeatres(self, container):
        self.log.trace()
        heartbeat = ApiInfo.parseHeartbeat(container.message)
        self.log.info("heartbeat: %s", heartbeat)

        self.__live["chat"]["no"] = heartbeat["comment_count"]
        if self.__decide_whether_need_postkey(no=heartbeat["comment_count"]):
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])

            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

        self.__send_timerreq_heartbeatreq(live_id = self.__live["liveId"], wait_time = heartbeat["wait_time"])

        self.state = self.__StateId.CONNECTING
        return True

    def __idle_httpheartbeatres(self, container):
        self.log.trace()
        heartbeat = ApiInfo.parseHeartbeat(container.message)
        self.log.info("heartbeat: %s", heartbeat)

        self.__live["chat"]["no"] = heartbeat["comment_count"]
        if self.__decide_whether_need_postkey(no=heartbeat["comment_count"]):
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])

            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

        self.__send_timerreq_heartbeatreq(live_id = self.__live["liveId"], wait_time = heartbeat["wait_time"])

        self.state = self.__StateId.IDLE
        return True

    def __chatsending_httpheartbeatres(self, container):
        self.log.trace()
        heartbeat = ApiInfo.parseHeartbeat(container.message)
        self.log.info("heartbeat: %s", heartbeat)

        self.__live["chat"]["no"] = heartbeat["comment_count"]
        if self.__decide_whether_need_postkey(no=heartbeat["comment_count"]):
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])

            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

        self.__send_timerreq_heartbeatreq(live_id = self.__live["liveId"], wait_time = heartbeat["wait_time"])

        self.state = self.__StateId.CHATSENDING
        return True

    def __init_socketconnectcnf(self, container):
        self.log.trace()
        pass

    def __connecting_socketconnectcnf(self, container):
        self.log.trace()

        self.__main_socket = container.message.id
        addr = self.__live["playerstatus"]["addr"]
        port = self.__live["playerstatus"]["port"]
        thread = self.__live["playerstatus"]["thread"]
#        self.__add_socket_info(addr, port, thread, self.__main_socket)

        result = self.send_message(
            UnitId.UNITCTRL,
            EventId.CONNECTCNF,
            True)

        threadTag = ApiInfo.createThreadTag(self.__live["playerstatus"]["thread"])
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETSENDREQ,
            SocketSendReq(
                destination = self.__main_socket,
                data = threadTag))

        if self.__live["msg"]:
            #test
            other_room_info = ApiInfo.calculateOtherRoomInfo(
                addr = self.__live["playerstatus"]["addr"],
                port = self.__live["playerstatus"]["port"],
                thread = self.__live["playerstatus"]["thread"])

            for index in other_room_info:
                result = self.send_message(
                    UnitId.SOCKETCTRL,
                    EventId.SOCKETCONNECTREQ,
                    SocketConnectReq(
                        addr = index["addr"],
                        port = index["port"]))

        self.state = self.__StateId.IDLE
        return True

    def __idle_socketconnectcnf(self, container):
        self.log.trace()
        self.__socket_info.append(container.message.id)
        
        print(container.message.id)
        
        threadTag = ApiInfo.createThreadTag(self.__live["playerstatus"]["thread"])
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETSENDREQ,
            SocketSendReq(
                destination = container.message.id,
                data = threadTag))
        return True

    def __chatsending_socketconnectcnf(self, container):
        self.log.trace()
        pass

    def __init_socketsendcnf(self, container):
        self.log.trace()
        pass

    def __connecting_socketsendcnf(self, container):
        self.log.trace()
        pass

    def __idle_socketsendcnf(self, container):
        self.log.trace()
        # TODO check result of sending
        # add sequence of retry sending
        return True

    def __chatsending_socketsendcnf(self, container):
        self.log.trace()
        # TODO check result of sending
        # add sequence of retry sending
        return True

    def __init_socketdisconnectcnf(self, container):
        self.log.trace()
        pass

    def __connecting_socketdisconnectcnf(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.UNITCTRL,
            EventId.DISCONNECTCNF,
            True)

        self.state = self.__StateId.INIT
        return True

    def __idle_socketdisconnectcnf(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.UNITCTRL,
            EventId.DISCONNECTCNF,
            True)

        self.state = self.__StateId.INIT
        return True

    def __chatsending_socketdisconnectcnf(self, container):
        self.log.trace()
        pass

    def __init_chatnotify(self, container):
        self.log.trace()
        self.log.warning(
            "Discard message from the parse_info %s",
            container.message)
        return True

    def __connecting_chatnotify(self, container):
        self.log.trace()
        pass

    def __idle_chatnotify(self, container):
        self.log.trace()

        result = self.send_message(
            UnitId.UNITCTRL,
            EventId.DATANOTIFY,
            container.message)

        self.__live["chat"]["no"] = container.message.attrs["no"]
        if self.__decide_whether_need_postkey(no=container.message.attrs["no"]):
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])

            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

        return True

    def __chatsending_chatnotify(self, container):
        self.log.trace()

        result = self.send_message(
            UnitId.UNITCTRL,
            EventId.DATANOTIFY,
            container.message)

        self.__live["chat"]["no"] = container.message.attrs["no"]
        if self.__decide_whether_need_postkey(no=container.message.attrs["no"]):
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])

            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

        return True

    def __init_chatresultnotify(self, container):
        self.log.trace()
        self.log.warning(
            "Discard message from the parse_info %s",
            container.message)
        return True

    def __connecting_chatresultnotify(self, container):
        self.log.trace()
        pass

    def __idle_chatresultnotify(self, container):
        self.log.trace()
        pass

    def __chatsending_chatresultnotify(self, container):
        self.log.trace()

        status = int(container.message.attrs["status"])
        if status == 0:
            self.__cleanupSendDataStore()

            result = self.send_message(
                UnitId.UNITCTRL,
                EventId.SENDCNF,
                None)

            data = self.__restoreSendDataStore()
            if data != None:
                chatTag = self.__create_chat_tag(data)

                result = self.send_message(
                    UnitId.SOCKETCTRL,
                    EventId.SOCKETSENDREQ,
                    SocketSendReq(
                        destination = self.__main_socket,
                        data = chatTag))

                self.state = self.__StateId.CHATSENDING
                return True

            else:
                self.state = self.__StateId.IDLE
                return True

        elif status == 1:
            self.log.warning(
                "chat_result fail[failure] (%s)",
                container.message)

            self.__cleanupSendDataStore()

            self.state = self.__StateId.IDLE
            return True

        elif status == 2:
            self.log.warning(
                "chat_result fail[thread id error] (%s)",
                container.message)

            url = ApiInfo.createGetplayerstatusUrl(self.__live["liveId"])
            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPLAYERSTATUSREQ,
                url)

            # TODO 再送処理は未実装
            # 状態をIDLEに戻す
            self.__cleanupSendDataStore()
            self.state = self.__StateId.IDLE
            return True

        elif status == 3:
            self.log.warning(
                "chat_result fail[ticket error] (%s)",
                container.message)

            threadTag = ApiInfo.createThreadTag(self.__live["playerstatus"]["thread"])
            result = self.send_message(
                UnitId.SOCKETCTRL,
                EventId.SOCKETSENDREQ,
                SocketSendReq(
                    destination = self.__main_socket,
                    data = threadTag))

            # TODO 再送処理は未実装
            # 状態をIDLEに戻す
            self.__cleanupSendDataStore()
            self.state = self.__StateId.IDLE
            return True

        elif status == 4:
            self.log.warning(
                "chat_result fail[postkey error] (%s)",
                container.message.attrs)

            self.__live["block_no"] = ApiInfo.calculateBlockNo(no=container.message.attrs["no"])
            url = ApiInfo.createGetpostkeyUrl(
                thread=self.__live["playerstatus"]["thread"],
                block_no=self.__live["block_no"])
            result = self.send_message(
                UnitId.HTTPCTRL,
                EventId.HTTPGETPOSTKEYREQ,
                url)

            self.state = self.__StateId.CHATSENDING
            return True

        elif status == 5:
            self.log.warning(
                "chat_result fail[lock comment] (%s)",
                container.message)

            self.__cleanupSendDataStore()

            self.state = self.__StateId.IDLE
            return True

        elif status == 8:
            self.log.warning(
                "chat_result fail[long comment] (%s)",
                container.message)

            self.__cleanupSendDataStore()

            self.state = self.__StateId.IDLE
            return True

        else:
            self.log.warning(
                "chat_result fail[unknown error] (%s)",
                container.message)

            self.__cleanupSendDataStore()

            self.state = self.__StateId.IDLE
            return True

    def __init_threadinfonotify(self, container):
        self.log.trace()
        pass

    def __connecting_threadinfonotify(self, container):
        self.log.trace()
        pass

    def __idle_threadinfonotify(self, container):
        self.log.trace()

        print(container.message.attrs)

        ApiInfo.recordConnectTime(
            start_time=self.__live["playerstatus"]["start_time"],
            server_time=container.message.attrs["server_time"])

        self.__save_thread(container.message.attrs)

        self.state = self.__StateId.IDLE
        return True

    def __chatsending_threadinfonotify(self, container):
        self.log.trace()

        print(container.message.attrs)

        ApiInfo.recordConnectTime(
            start_time=self.__live["playerstatus"]["start_time"],
            server_time=container.message.attrs["server_time"])

        self.__save_thread(container.message.attrs)

        data = self.__restoreSendDataStore()
        if data != None:
            chatTag = self.__create_chat_tag(data)

            result = self.send_message(
                UnitId.SOCKETCTRL,
                EventId.SOCKETSENDREQ,
                SocketSendReq(
                    destination = self.__main_socket,
                    data = chatTag))

        self.state = self.__StateId.CHATSENDING
        return True

    def __init_disconnectReq(self, container):
        self.log.trace()
        pass

    def __connecting_disconnectReq(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETDISCONNECTREQ,
            None)

        self.__init_live_info()

        self.state = self.__StateId.CONNECTING
        return True

    def __idle_disconnectReq(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETDISCONNECTREQ,
            None)

        self.__init_live_info()

        self.state = self.__StateId.IDLE
        return True

    def __chatsending_disconnectReq(self, container):
        self.log.trace()
        result = self.send_message(
            UnitId.SOCKETCTRL,
            EventId.SOCKETDISCONNECTREQ,
            None)

        self.__init_live_info()

        self.state = self.__StateId.IDLE
        return True


    # define inner state
    class __StateId(BaseEnum):
        INIT = 0x00
        CONNECTING = 0x01
        IDLE = 0x02
        CHATSENDING = 0x03


    class __LiveInfo(BaseClass):
        def __init__(self):
            pass


if __name__ == "__main__":
    pass


