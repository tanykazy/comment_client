# -*- coding: UTF-8 -*-

"""
使用中のブラウザのクッキーからセッションIDを抽出するクラス
現在、firefoxのみ対応

ブラウザを選択する機能実装後、再考する。
"""


__all__ = [""]


import os
import platform
from configparser import RawConfigParser
import sqlite3

from define import BaseClass
from define import Log


log = Log(name=__name__)


class LoginInfo(BaseClass):

    @classmethod
    def get_login_info(cls):
        log.trace()

        user_session_id = cls.__get_session_firefox()

        log.info("user session %s", user_session_id)

        return user_session_id

    @classmethod
    def __get_session_firefox(cls):
        log.trace()

        if platform.uname().system == "Windows":
            homePath = os.getenv("APPDATA", None)
        else:
            homePath = os.getenv("HOME", None)

        if homePath == None:
            log.error("Home dir path not found")
            return None

        log.info("home dir path %s", homePath)

        if platform.uname().system == "Windows":
            firefoxPath = os.path.join(homePath, "Mozilla", "Firefox")
        else:
            firefoxPath = os.path.join(homePath, ".mozilla", "firefox")

        profilesPath = os.path.join(firefoxPath, "profiles.ini")

        if os.path.exists(profilesPath) == False:
            log.error("%s not found", profilesPath)
            return None

        log.info("profiles file path %s", profilesPath)

        # Use last Profile
        configparser = RawConfigParser()
        configparser.read(profilesPath)

#        lastProfile = configparser.get("General", "StartWithLastProfile")
        lastProfile = "0"
        profileName = configparser.get("Profile" + lastProfile, "Path")

        cookieDir = os.path.join(firefoxPath, profileName)
        cookieFile = os.path.join(cookieDir, "cookies.sqlite")

        if os.path.exists(cookieFile) == False:
            log.error("%s not found", cookieFile)
            return None

        log.info("cookie file path %s", cookieFile)

        connection = sqlite3.connect(cookieFile)
        cursor = connection.cursor()
        cursor.execute("SELECT value FROM moz_cookies WHERE baseDomain=\"nicovideo.jp\" AND name=\"user_session\" AND host=\".nicovideo.jp\"")
        session = cursor.fetchone()[0]

        return session


if __name__ == "__main__":
    pass


