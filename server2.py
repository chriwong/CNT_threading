# Project 2 - Server
import os
import pickle
import random
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


class Contest:
    def __init__(self, number):
        self.number = number
        self.questions = []
        self.correctness = []
        self.executed = False


class ContestServer:
    def __init__(self):
        self.host = ''
        self.port = 0
        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.bind((self.host, self.port))
        except Exception as e:
            print('Server init error:', str(e), file=sys.stderr)
            sys.exit(-1)

    def begin_listening(self):
        try:
            self.serverSocket.listen(5)
            print('Server listening on ', self.serverSocket.getsockname()[1])

            while True:
                meisterSocket, addr = self.serverSocket.accept()
                print('Accepted new connection')

                while True:
                    menuOption = meisterSocket.recv(64).decode()
                    if menuOption[0] == 'p':
                        pass
                    elif menuOption[0] == 'd':
                        pass
                    elif menuOption[0] == 'g':
                        pass
                    elif menuOption[0] == 'k':
                        meisterSocket.send('Terminating'.encode())
                        break
                    elif menuOption[0] == 'h':
                        # meisterSocket.send('\tCONTEST MEISTER HELP MENU\np <n> - put new question <n> in question bank\nd <n> - deletes question <n>\ng <n> - retrieves question <n>\ns <n> - set new contest <n>\na <cn> <qn> - append question <qn> to contest <cn>\nbegin <n> - begin contest <n>\nl - list contests\nr <n> - review contest <n>\nk - kill server\nq - kill client\nh - print this help text\n'.encode())
                        pass
                    elif menuOption[0] == 's':
                        pass
                    elif menuOption[0] == 'a':
                        pass
                    elif menuOption[0] == 'b':
                        pass
                    elif menuOption[0] == 'l':
                        pass
                    elif menuOption[0] == 'r':
                        pass

                meisterSocket.close()
                print(' ~Closed connection')

        except Exception as e:
            print('Server listen error:', str(e), file=sys.stderr)
            sys.exit(-1)

    def can_sockets_pickle(self):
        self.serverSocket.listen(1)
        print('Server listening on ', self.serverSocket.getsockname()[1])
        connection, addr = self.serverSocket.accept()
        pickledQ = connection.recv(1024)
        normalQuestion = pickle.loads(pickledQ)
        print(normalQuestion)


def main():
    global QuestionBank
    global ContestBank
    contestServer = ContestServer()
    contestServer.can_sockets_pickle()


# Runtime starts here

QuestionBank = {}   # {int questionNumber, Question q}
ContestBank = {}    # {int contestNumber, Contest c}
try:
    if os.stat('questionbank.pickle').st_size != 0:
        with open('questionbank.pickle', 'rb') as file:
            print('Loaded QuestionBank from pickle')
            QuestionBank = pickle.load(file)
            file.close()
except FileNotFoundError as e:
    print('No questionbank.pickle found, creating one now...')
    a = open('questionbank.pickle', 'wb+')
    a.close()

try:
    if os.stat('contestbank.pickle').st_size != 0:
        with open('contestbank.pickle', 'rb') as file:
            print('Loaded ContestBank from pickle')
            ContestBank = pickle.load(file)
            file.close()
except FileNotFoundError as e:
    print('No contestbank.pickle found, creating one now...')
    a = open('contestbank.pickle', 'wb+')
    a.close()

if __name__ == '__main__':
    main()