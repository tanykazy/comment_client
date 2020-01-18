#! /usr/bin/env python
# -*- coding: utf_8 -*-


__all__ = [""]


class getplayerstatus():
    def __init__(self, data=None):
        document = minidom.parseString(data.encode("utf_8"))
#        document = minidom.parseString(data)
        getplayerstatus = document.getElementsByTagName(cls.__GETPLAYERSTATUSTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__MSTAG) == False:
            DebugMng.debugError("<%s> not found", cls.__MSTAG)
            return None
        ms = getplayerstatus.getElementsByTagName(cls.__MSTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__RTMPTAG) == False:
            DebugMng.debugError("<%s> not found", cls.__RTMPTAG)
            return None
        rtmp = getplayerstatus.getElementsByTagName(cls.__RTMPTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__USERTAG) == False:
            DebugMng.debugError("<%s> not found", cls.__USERTAG)
            return None
        user = getplayerstatus.getElementsByTagName(cls.__USERTAG)[0]

        if getplayerstatus.getElementsByTagName(cls.__STREAMTAG) == False:
            DebugMng.debugError("<%s> not found", cls.__STREAMTAG)
            return None
        stream = getplayerstatus.getElementsByTagName(cls.__STREAMTAG)[0]

        addr = ms.getElementsByTagName(cls.__ADDRTAG)[0].firstChild.data.strip(None)
        port = ms.getElementsByTagName(cls.__PORTTAG)[0].firstChild.data.strip(None)
        thread = ms.getElementsByTagName(cls.__THREADTAG)[0].firstChild.data.strip(None)
        ticket = rtmp.getElementsByTagName(cls.__TICKETTAG)[0].firstChild.data.strip(None)
        user_id = user.getElementsByTagName(cls.__USER_IDTAG)[0].firstChild.data.strip(None)
        is_premium = user.getElementsByTagName(cls.__IS_PREMIUMTAG)[0].firstChild.data.strip(None)
        start_time = stream.getElementsByTagName(cls.__START_TIMETAG)[0].firstChild.data.strip(None)





        self.__addr
        self.__port
        self.__thread
        self.__ticket
        self.__user_id
        self.__is_premium
        self.__start_time

