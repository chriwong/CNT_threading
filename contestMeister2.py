# Project 2 - Contest Meister
import os
import pickle
import socket
import sys
import threading


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

    def tryConnect(self, h, p):
        try:
            self.meisterSocket.connect((h, p))
            print('Successful connection!')
        except ConnectionRefusedError as connRefE:
            print('Error: unable to connect', str(connRefE), file=sys.stderr)
            sys.exit(-1)
        except Exception as connE:
            print('Connection error:', str(connE), file=sys.stderr)

    def handle_input(self, op):
        if op[0] == 'p':
            self.p(op)

        elif op[0] == 's':
            print('Server received s')

        elif op[0] == 'a':
            print('Server received a')

        elif op[0] == 'b':
            print('Server received b')

        elif op[0] == 'l':
            print('Server received l')

        elif op[0] == 'r':
            print('Server received r')

    def p(self, number):
        newQuestion = buildQuestion(number)
        pickledNewQuestion = pickle.dumps(newQuestion)
        self.meisterSocket.send(pickledNewQuestion)
        res = self.meisterSocket.recv(1024).decode()
        print(res)


# Returns only syntactically correct menu options
def get_sanitized_input():
    while True:
        try:
            s = str(input("> "))

            # noarg commands
            if s[0] == 'k' or s[0] == 'q' or s[0] == 'h' or s[0] == 'l':
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
def buildQuestion(number):
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


# Program start

if len(sys.argv) < 3:
    print('Error: missing program arguments', file=sys.stderr)
    sys.exit(-1)

elif len(sys.argv) > 4:
    print('Error: too many program arguments', file=sys.stderr)
    sys.exit(-1)

host = sys.argv[1]
port = sys.argv[2]
contestMeister = ContestMeister()
contestMeister.tryConnect(host, port)

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
        print('Sanitized input:', menuOption)
        contestMeister.handle_input(menuOption)
