# Project 2 - Contestant
import socket
import sys
import traceback


class Contestant:
    def __init__(self):
        self.contestantSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def try_connect(self, addr):
        try:
            self.contestantSocket.connect(addr)
            print('Successful connection!')
        except ConnectionRefusedError as connRefE:
            print('Error: unable to connect', str(connRefE), file=sys.stderr)
            print(traceback.format_exc())
            sys.exit(-1)
        except Exception as connE:
            print('Connection error:', str(connE), file=sys.stderr)
            print(traceback.format_exc())
            sys.exit(-1)

    def play_contest(self):
        pass


if len(sys.argv) != 3:
    print('Program error: wrong number of arguments', file=sys.stderr)
    sys.exit(-1)

host = sys.argv[1]
port = 0
try:
    port = int(sys.argv[2])
except TypeError as nan:
    print('Program error: port number is invalid', str(nan), file=sys.stderr)
    sys.exit(-1)

contestant = Contestant()
contestant.try_connect((host, port))
contestant.play_contest()

