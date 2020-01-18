#! /usr/bin/env python
# -*- coding: utf_8 -*-


__version__ = "0.3.6"


if __name__ == '__main__':
    import argparse
    import sys
    try:
        from threading import Lock
    except ImportError:
        from dummy_threading import Lock
    from cmd import Cmd
    from comment_client import client

    argumentParser = argparse.ArgumentParser(
        description="Client of comment for Niconico Live.",
        epilog="Report bugs to http://c1083.hatenablog.com/",
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

            self.__client = client.Client(handle=self.__handler, path=args.file)
            # connect
            self.__client.connect(args.url)

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
            self.__client.quit()

        def precmd(self, line):
            return line

        def postcmd(self, stop, line):
            return stop

        def preloop(self):
            pass

        def postloop(self):
            self.__client.quit()

        def default(self, line):
            self.__client.send(line)
            return False

        def emptyline(self):
            pass

        def do_hello(self, arg):
            self.__client.connect(arg)
            return False

        def do_bye(self, arg):
            self.__client.disconnect()
            return False

        def do_quit(self, arg):
            self.__client.quit()
            return True

    shell = CommentShell(completekey='tab', stdin=sys.stdin, stdout=sys.stdout)
    try:
        shell.cmdloop()
    except KeyboardInterrupt as error:
        shell.quit()
