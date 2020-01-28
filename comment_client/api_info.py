# -*- coding: utf_8 -*-


__all__ = [""]


import re
from urllib.parse import urlparse
from xml.dom import minidom
import time

from define import BaseClass
from define import Log


log = Log(__name__)


class ApiInfo(BaseClass):
    GETPLAYERSTATUSURL = 'http://watch.live.nicovideo.jp/api/getplayerstatus?v=%s'
    GETPOSTKEYURL = 'http://watch.live.nicovideo.jp/api/getpostkey?thread=%s&block_no=%s'
    LEAVEURL = 'http://watch.live.nicovideo.jp/api/leave?v=%s'
    GETSERVERTIMEURL = 'http://watch.live.nicovideo.jp/api/getservertime?t=%s'
    THREADTAG = '<thread thread="%s" version="20061206" res_from="-1" />'
#    CHATTAG = '<chat thread="%s" ticket="%s" vpos="%s" postkey="%s" locale="%s" user_id="%s" premium="%s" mail="%s">%s</chat>'
    CHATTAG = '<chat thread="%s" ticket="%s" vpos="%s" postkey="%s" user_id="%s" premium="%s" mail="%s">%s</chat>'
    HEARTBEATURL = 'http://live.nicovideo.jp/api/heartbeat?v={live_id}'

    MAIL = "184"
    LOCALE = "ja-jp"

    USER_AGENT = ("User-agent", "CommentManager")

    VERSION = 0
    NAME = "user_session"
    VALUE = None # to set user_session
    PORT = None
    PORT_SPECIFIED = False
    DOMAIN = ".live.nicovideo.jp"
    DOMAIN_SPECIFIED = False
    DOMAIN_INITIAL_DOT = True
    PATH = "/"
    PATH_SPECIFIED = True
    SECURE = False
    EXPIRES = None
    DISCARD = False
    COMMENT = None
    COMMENT_URL = None
    REST = {"HttpOnly": None}
    RFC2109 = False

    __START_TIME = None
    __SERVER_TIME = None
    __CONNECT_TIME = None
    __DIFFTIME_CONNECTED = None

    __GETPLAYERSTATUSTAG = "getplayerstatus"
    __MSTAG = "ms"
    __ADDRTAG = "addr"
    __PORTTAG = "port"
    __THREADTAG = "thread"
    __RTMPTAG = "rtmp"
    __TICKETTAG = "ticket"
    __USERTAG = "user"
    __USER_IDTAG = "user_id"
    __IS_PREMIUMTAG = "is_premium"
    __STREAMTAG = "stream"
    __START_TIMETAG = "start_time"
    __HEARTBEATTAG = "heartbeat"
    __COMMENTCOUNTTAG = "commentCount"
    __WAITTIMETAG = "waitTime"

    __RELIVEID = re.compile(r"^lv|co[0-9]+$")
    __REPOSTKEY = re.compile(r"^postkey", re.IGNORECASE)
    __RESERVERTIME = re.compile(r"^servertime", re.IGNORECASE)
    __READDRNUM = re.compile(r"[0-9]{3}")
    __RESERVERTYPEOMSG = re.compile(r"^omsg", re.IGNORECASE)
    __RESERVERTYPEMSG = re.compile(r"^msg", re.IGNORECASE)

    __TRUE = "true"
    __FALSE = "false"

    @classmethod
    def createGetplayerstatusUrl(cls, liveId = None):
        log.trace()
        return cls.GETPLAYERSTATUSURL % liveId

    @classmethod
    def createLeaveUrl(cls, liveId = None):
        log.trace()
        return cls.LEAVEURL % liveId

    @classmethod
    def createGetservertimeUrl(cls, time = None):
        log.trace()
        return cls.GETSERVERTIMEURL % ""

    @classmethod
    def createThreadTag(cls, thread = None):
        log.trace()
        return cls.THREADTAG % thread

    @classmethod
    def createGetpostkeyUrl(cls, thread = None, block_no = None):
        log.trace()
        return cls.GETPOSTKEYURL % (thread, block_no)

    @classmethod
    def createHeartbeatUrl(cls, live_id=None):
        log.trace()
        return cls.HEARTBEATURL.format(live_id = live_id)

    @classmethod
    def createChatTag(cls, thread = None, ticket = None, vpos = None, postkey = None, locale = None, user_id = None, premium = None, mail = None, text = None):
        log.trace()
#        return cls.CHATTAG % (thread, ticket, vpos, postkey, locale, user_id, premium, mail, text)
        return cls.CHATTAG % (thread, ticket, vpos, postkey, user_id, premium, mail, text)

    @classmethod
    def expandDom(cls, data = None):
        log.trace()
#        document = minidom.parseString(data.encode("utf_8"))
        document = minidom.parseString(data)
        getplayerstatus = document.getElementsByTagName(cls.__GETPLAYERSTATUSTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__MSTAG) == False:
            log.error("<%s> not found", cls.__MSTAG)
            return None
        ms = getplayerstatus.getElementsByTagName(cls.__MSTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__RTMPTAG) == False:
            log.error("<%s> not found", cls.__RTMPTAG)
            return None
        rtmp = getplayerstatus.getElementsByTagName(cls.__RTMPTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__USERTAG) == False:
            log.error("<%s> not found", cls.__USERTAG)
            return None
        user = getplayerstatus.getElementsByTagName(cls.__USERTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__STREAMTAG) == False:
            log.error("<%s> not found", cls.__STREAMTAG)
            return None
        stream = getplayerstatus.getElementsByTagName(cls.__STREAMTAG)[0]

        addr = ms.getElementsByTagName(cls.__ADDRTAG)[0].firstChild.data.strip(None)
        port = ms.getElementsByTagName(cls.__PORTTAG)[0].firstChild.data.strip(None)
        thread = ms.getElementsByTagName(cls.__THREADTAG)[0].firstChild.data.strip(None)
        ticket = rtmp.getElementsByTagName(cls.__TICKETTAG)[0].firstChild.data.strip(None)
        user_id = user.getElementsByTagName(cls.__USER_IDTAG)[0].firstChild.data.strip(None)
        is_premium = user.getElementsByTagName(cls.__IS_PREMIUMTAG)[0].firstChild.data.strip(None)
        start_time = stream.getElementsByTagName(cls.__START_TIMETAG)[0].firstChild.data.strip(None)

        return {
            "addr": addr,
            "port": port,
            "thread": thread,
            "ticket": ticket,
            "user_id": user_id,
            "is_premium": is_premium,
            "start_time": start_time}

    @classmethod
    def parseAddrNum(cls, addr=None):
        log.trace()
        match = cls.__READDRNUM.search(addr)
        if match:
            result = match.group()
            log.error("Message addr number: %s", result)
        else:
            result = None
            log.error("Message addr number not found in: %s", addr)
        return result

    @classmethod
    def parseHeartbeat(cls, data=None):
        log.trace()
        document = minidom.parseString(data)
        heartbeat = document.getElementsByTagName(cls.__HEARTBEATTAG)[0]

        if heartbeat.getElementsByTagName(cls.__COMMENTCOUNTTAG) == False:
            log.error("<%s> not found", cls.__COMMENTCOUNTTAG)
            return None
        comment_count = heartbeat.getElementsByTagName(cls.__COMMENTCOUNTTAG)[0].firstChild.data.strip(None)

        if heartbeat.getElementsByTagName(cls.__WAITTIMETAG) == False:
            log.error("<%s> not found", cls.__WAITTIMETAG)
            return None
        wait_time = heartbeat.getElementsByTagName(cls.__WAITTIMETAG)[0].firstChild.data.strip(None)

        return {
            "comment_count": int(comment_count),
            "wait_time": int(wait_time)}

    @classmethod
    def recordConnectTime(cls, start_time = None, server_time = None):
        log.trace()
        cls.__CONNECT_TIME = time.time()
        cls.__START_TIME = float(start_time)
        cls.__SERVER_TIME = float(server_time)
        cls.__DIFFTIME_CONNECTED = float(cls.__SERVER_TIME - cls.__START_TIME)

    @classmethod
    def calculateDiffTime(cls):
        log.trace()
        intraDiffTime = float(time.time() - cls.__CONNECT_TIME)
        return int((intraDiffTime + cls.__DIFFTIME_CONNECTED) * 100)

    @classmethod
    def calculateBlockNo(cls, no = None):
        log.trace()
        return (int(no) + 1) // 100

    @classmethod
    def calculateOtherRoomInfo(cls, addr=None, port=None, thread=None):
        addr_num = int(cls.parseAddrNum(addr))
        addr_list = addr.split(str(addr_num))
        addr_num_tmp = addr_num
        port_tmp = int(port)
        result = list()
        
        count = 0
        
        while True:
            if(addr_num_tmp == 104):
                addr_num_tmp = 101
            else:
                addr_num_tmp += 1
            port_tmp += 1
            result.append({
                "addr": addr_list[0] + str(addr_num_tmp) + addr_list[1],
                "port": port_tmp
            })
            count += 1
            if count > 5:
                break
        return result

    @classmethod
    def extractLiveId(cls, url = None):
        log.trace()
        parseResult = urlparse(url)
        liveId = parseResult.path.split("/")[-1]
        if cls.__RELIVEID.search(liveId) != None:
            return liveId
        else:
            log.error("live id not found in [%s]", url)
            return None

    @classmethod
    def extractPostkey(cls, postkey = None):
        log.trace()
#        key = postkey.decode(encoding="utf-8", errors="strict").split("=")[-1]
        key = postkey.split("=")[-1]

        if key == None:
            log.error("postkey not found in [%s]", postkey)
        return key

    @classmethod
    def extractServertime(cls, servertime = None):
        log.trace()
        time = servertime.split("=")[-1]
        if time == None:
            log.error("servertime not found in [%s]", servertime)
        return time

    @classmethod
    def extractLeave(cls, leave = None):
        log.trace()
        if leave == cls.__TRUE:
            return True
        else:
            return False

    @classmethod
    def detectServerType(cls, addr=None):
        if cls.__RESERVERTYPEOMSG.search(addr):
            return "omsg"
        if cls.__RESERVERTYPEMSG.search(addr):
            return "msg"
        return None

class Getplayerstatus(object):
    def __init__(self, data):
        log.trace()
        self.__data = data


if __name__ == "__main__":
    pass


