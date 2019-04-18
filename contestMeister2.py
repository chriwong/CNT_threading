# Project 2 - Contest Meister
import os
import pickle
import socket
import sys
import threading
import traceback


class Question:
    def __init__(self, number):
        self.number = number
        self.tag = ''
        self.text = ''
        self.choices = {}
        self.answer = ''

    def toString(self):
        s = ''
        s += self.tag
        s += '\n'
        s += self.text
        s += '\n.\n'
        for v in self.choices.values():
            s = s + v + '\n.\n'
        s += '.\n'
        s += self.answer
        return s


class ContestMeister:
    def __init__(self):
        self.meisterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def try_connect(self, h, p):
        try:
            self.meisterSocket.connect((h, p))
            print('Successful connection!')
        except ConnectionRefusedError as connRefE:
            print('Error: unable to connect', str(connRefE), file=sys.stderr)
            print(traceback.format_exc())
            sys.exit(-1)
        except Exception as connE:
            print('Connection error:', str(connE), file=sys.stderr)
            print(traceback.format_exc())

    def handle_input(self, menuOpt):
        if menuOpt[0] == 'p':
            try:
                newQuestion = build_Question(int(menuOpt[2:]))
                print(newQuestion.toString())
                pickledNewQuestion = pickle.dumps(newQuestion)
                self.meisterSocket.send(pickledNewQuestion)
                res = self.meisterSocket.recv(1024).decode()
                print(res)
            except ValueError:
                print('p command error: number invalid\n', traceback.format_exc())
                self.meisterSocket.recv(1024)

        elif menuOpt[0] == 'd':
            res = self.meisterSocket.recv(64).decode()
            print(res)

        elif menuOpt[0] == 'g':
            res = self.meisterSocket.recv(64).decode()
            print(res)

        elif menuOpt[0] == 'k':
            self.meisterSocket.send('k'.encode())
            kill_confirm = self.meisterSocket.recv(8).decode()
            if kill_confirm == 'killed':
                print('Server successfully killed')
                sys.exit(1)
            else:
                print('Server unsuccessfully killed')

        elif menuOpt[0] == 'q':
            pass

        elif menuOpt[0] == 'h':
            pass

        elif menuOpt[0] == 's':
            pass

        elif menuOpt[0] == 'a':
            pass

        elif menuOpt[0] == 'b':
            pass

        elif menuOpt[0] == 'l':
            pass

        elif menuOpt[0] == 'r':
            pass


# Returns only syntactically correct menu options
def get_sanitized_input():
    while True:
        try:
            s = str(input("> "))

            # noarg commands
            if s[0] == 'k' or s[0] == 'q' or s[0] == 'h' or s[0] == 'l' or s[0] == 'z':
                return s

            # single arg commands
            elif s[0] == 'p' or s[0] == 'd' or s[0] == 'g' or s[0] == 's' or s[:5] == 'begin' or s[0] == 'r':
                try:
                    if isinstance(int(s[2:]), int):
                        return s
                    else:
                        print('Input validation error: second argument is wonky')
                except IndexError as indexE:
                    print('Input validation error: missing arguments')
                except ValueError as valE:
                    print('Input validation error: numeric arguments expected')

            # two arg command
            elif s[0] == 'a':
                if s.count(' ') < 2:
                    print('Input validation error: did not find enough space delimiters')
                else:
                    try:
                        sp = s.find(' ', 2)
                        if isinstance(int(s[2:sp]), int) and isinstance(int(s[sp:]), int):
                            return s
                        else:
                            print('Input validation error: third argument is wonky')
                    except IndexError as e:
                        print('Input validation error: missing arguments')
                    except ValueError as e:
                        print('Input validation error: numeric arguments expected')
            else:
                print('Input validation error: unrecognized menu option. Enter q,d,g,k,q,h,s,a,begin,l,r')

        except Exception as e:
            print('Input validation error:', str(e))


# Creates a Question object
def build_Question(number):
    newQuestion = Question(number)

    # Tag
    newQuestion.tag = input()

    # Text
    buf = input()
    while buf != '.':
        newQuestion.text += buf
        buf = input()

    # Choices
    choice = input()
    while True:
        buf = input()
        while buf != '.':
            choice += '\n'  # Keep multi-line choices multi-line
            choice += buf
            buf = input()
        terminator = input()
        newQuestion.choices[choice[1]] = choice
        choice = terminator
        if terminator == '.':
            break

    # Answer
    newQuestion.answer = input()

    return newQuestion


# RUNTIME STARTS HERE

if len(sys.argv) < 3:
    print('Error: missing program arguments', file=sys.stderr)
    sys.exit(-1)

elif len(sys.argv) > 4:
    print('Error: too many program arguments', file=sys.stderr)
    sys.exit(-1)

host = sys.argv[1]
port = 0
try:
    port = int(sys.argv[2])
except ValueError as nan:
    print('Program start error: port is not valid:', str(nan), file=sys.stderr)
    sys.exit(-1)
contestMeister = ContestMeister()
contestMeister.try_connect(host, port)

if len(sys.argv) == 4:
    cmdfilename = sys.argv[3]
    try:
        with open(cmdfilename, 'r') as cmdfile:
            for line in cmdfile:
                # do command
                pass

    except OSError as e:
        print('Error opening command file (OSError):', str(e), file=sys.stderr)
        sys.exit(-1)
    except Exception as ee:
        print('Error opening command file: ', str(ee), file=sys.stderr)

else:
    while True:
        menuOption = get_sanitized_input()
        contestMeister.meisterSocket.send(menuOption.encode())
        print('Sanitized input:', menuOption)
        contestMeister.handle_input(menuOption)
