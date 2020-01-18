#! /usr/bin/env python
# -*- coding: utf_8 -*-


__all__ = ["Client"]


from comment_client.define import BaseClass
from comment_client._unit_ctrl import UnitCtrl


class Client(BaseClass):
    """
    フレームワークとして機能するクラス
    現在コメント受信時に呼び出されるハンドラの登録だけが実装されている。
    """
    def __init__(self, handle=None, path=None):
        self.__handle = handle
        self.__path = path

        self.__unit_ctrl = UnitCtrl(handle=self.__handle)

        self.__unit_ctrl.start()

    def handler(self, *args, **kwargs):
        if self.__handle is not None:
            self.__handle(*args, **kwargs)

    def connect(self, url):
        return self.__unit_ctrl.connect(url)

    def disconnect(self):
        return self.__unit_ctrl.disconnect()

    def send(self, text):
        return self.__unit_ctrl.send(text)

    def quit(self):
        """
        プロセスを終了(kill)するためのメソッド
        """
        return self.__unit_ctrl.stop()


if __name__ == "__main__":
    pass
