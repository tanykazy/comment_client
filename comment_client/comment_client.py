#! /usr/bin/env python
# -*- coding: utf_8 -*-


__version__ = "0.0.1"


from define import BaseClass
from _unit_ctrl import UnitCtrl


class CommentClient(BaseClass):
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


if __name__ == '__main__':
    import argparse
    import sys
    try:
        from threading import Lock
    except ImportError:
        from dummy_threading import Lock
    from cmd import Cmd

    argumentParser = argparse.ArgumentParser(
        description="Client of comment for Niconico Live.",
#        prog="",
        add_help=True,
        argument_default=None,
#        parents=(),
        prefix_chars="-",
#        conflict_handler=None,
        formatter_class=argparse.RawTextHelpFormatter)

    argumentParser.add_argument(
        "url",
        action="store",
#        const=None,
        default=None,
        type=str,
#        choices=None,
#        required=True,
        help="URL or ID of the live",
        metavar="URL")

    argumentParser.add_argument(
        "-f", "--file",
        action="store",
        nargs=1,
#        const=None,
        default=None,
        type=str,
#        choices=None,
#        required=True,
        help="Name of the file to store the received data",
        metavar="FILE",
        dest="file")

    argumentParser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__)

    args = argumentParser.parse_args(
        args=None,
        namespace=None)

    class CommentShell(Cmd):
        def __init__(self, completekey, stdin, stdout):
            Cmd.__init__(self, completekey, stdin, stdout)
            self.intro = 'Welcome to the comment client for Nico Live. Type help or ? to list commands.\n'
            self.prompt = '> '

            #self.__comment_client = comment_client.CommentClient(handle=self.__handler, path=args.file)
            self.__comment_client = CommentClient(handle=self.__handler, path=args.file)
            # connect
            self.__comment_client.connect(args.url)

        def __handler(self, text, **status):
#            print("{no:<3}: {text}".format(no=status["no"], text=text.encode(encoding="shift-jis", errors="replace").decode("shift-jis")))
            if("premium" in status):
                premium = status["premium"]
            else:
                premium = 0
            if("mail" in status):
                mail = status["mail"]
            else:
                mail = 0
            print("{no:>3}:{premium:<1}:{mail:3}:{user_id:6}>{text}".format(
                no=status["no"],
                premium=premium,
                mail=mail,
                user_id=status["user_id"],
                text=text.encode(encoding="shift_jis", errors="ignore").decode(encoding="shift_jis", errors="ignore")))

        def quit(self):
            self.__comment_client.quit()

        def precmd(self, line):
            return line

        def postcmd(self, stop, line):
            return stop

        def preloop(self):
            pass

        def postloop(self):
            self.__comment_client.quit()

        def default(self, line):
            self.__comment_client.send(line)
            return False

        def emptyline(self):
            pass

        def do_hello(self, arg):
            self.__comment_client.connect(arg)
            return False

        def do_bye(self, arg):
            self.__comment_client.disconnect()
            return False

        def do_quit(self, arg):
            self.__comment_client.quit()
            return True

    shell = CommentShell(completekey='tab', stdin=sys.stdin, stdout=sys.stdout)
    try:
        shell.cmdloop()
    except KeyboardInterrupt as error:
        shell.quit()
