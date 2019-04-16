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


class ContestMeister:
    def __init__(self):
        self.meisterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def try_connect(self, host, port):
        try:
            self.meisterSocket.connect((host, port))
            print('Successful connection!')
        except ConnectionRefusedError as e:
            print('Error: unable to connect', str(e), file=sys.stderr)
            sys.exit(-1)
        except Exception as e:
            print('Connection error:', str(e), file=sys.stderr)

    def can_sockets_pickle(self):
        quest = Question(69)
        quest.tag = 'TAG YOU\'RE IT'
        quest.text = 'The quick brown fox jumped over the lazy ?'
        quest.choices = {'a': '(a) aardvark', 'b': '(b) baboon', 'c': '(c) chimpanzee', 'd': '(d) dog'}
        quest.answer = 'd'
        pickledQuest = pickle.dumps(quest)
        self.meisterSocket.connect(('storm.cise.ufl.edu', 44123))
        self.meisterSocket.send(pickledQuest)

    def p(self, number):
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
            if terminator == '.':
                break
            else:
                newQuestion.choices[choice[1]] = choice
                choice = terminator

        # Answer
        newQuestion.answer = input()

        pickledNewQuestion = pickle.dumps(newQuestion)
        self.meisterSocket.send(pickledNewQuestion)


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
                except IndexError as e:
                    print('Input validation error: missing arguments')
                except ValueError as e:
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


# Program start

# if len(sys.argv) < 3:
#     print('Error: missing program arguments', file=sys.stderr)
#     sys.exit(-1)
#
# elif len(sys.argv) > 4:
#     print('Error: too many program arguments', file=sys.stderr)
#     sys.exit(-1)
#
# else:
#     host = sys.argv[1]
#     port = sys.argv[2]
#     contestMeister = ContestMeister()
#     contestMeister.try_connect(host, port)
#
#     if len(sys.argv) == 4:
#         cmdfilename = sys.argv[3]
#         try:
#             with open(cmdfilename, 'r') as cmdfile:
#                 for line in cmdfile:
#                     # do command
#                     pass
#
#         except OSError as e:
#             print('Error opening command file (OSError):', str(e), file=sys.stderr)
#             sys.exit(-1)
#         except Exception as ee:
#             print('Error opening command file: ', str(ee), file=sys.stderr)
#
#     else:
#         while True:
#             menuOption = get_sani_input()
#             print('Sanitized input:', menuOption)
#             if menuOption == 'q':
#                 sys.exit(1)

contestMeister = ContestMeister()
contestMeister.can_sockets_pickle()