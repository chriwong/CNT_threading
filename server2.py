# Project 2 - Server
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
        except Exception as initE:
            print('Server init error:', str(initE), file=sys.stderr)
            sys.exit(-1)

    def startListening(self):
        try:
            self.serverSocket.listen(5)
            print('Server listening on ', self.serverSocket.getsockname()[1])

            while True:
                meisterSocket, addr = self.serverSocket.accept()
                print('Accepted new connection')

                while True:
                    menuOption = meisterSocket.recv(64).decode()
                    print('menuoption:', menuOption)

                    if menuOption[0] == 'p':
                        print('Server received p')
                        pickledQuestion = meisterSocket.recv(1024)
                        unpickledQuestion = pickle.loads(pickledQuestion)
                        if unpickledQuestion.number not in QuestionBank:
                            QuestionBank[unpickledQuestion.number] = unpickledQuestion
                            meisterSocket.send('Success'.encode())
                        else:
                            # The given question number already exists in the question bank
                            # Notify the meister as such
                            meisterSocket.send('Error, that question number already exists'.encode())

                    elif menuOption[0] == 'd':
                        delQuestion = int(menuOption[2:])
                        try:
                            del QuestionBank[delQuestion]
                        except KeyError as keyE:
                            # The given question number was not in the question bank
                            meisterSocket.send('Error, that question number did not exist'.encode())

                    elif menuOption[0] == 'g':
                        print('Server received g')

                    elif menuOption[0] == 'k':
                        print('Server received k')
                        meisterSocket.send('killed'.encode())
                        break

                    elif menuOption[0] == 'q':
                        pass

                    elif menuOption[0] == 'h':
                        # meisterSocket.send('\tCONTEST MEISTER HELP MENU\np <n> - put new question <n> in question bank\nd <n> - deletes question <n>\ng <n> - retrieves question <n>\ns <n> - set new contest <n>\na <cn> <qn> - append question <qn> to contest <cn>\nbegin <n> - begin contest <n>\nl - list contests\nr <n> - review contest <n>\nk - kill server\nq - kill client\nh - print this help text\n'.encode())
                        print('Server received h')
                        pass

                    elif menuOption[0] == 's':
                        print('Server received s')

                    elif menuOption[0] == 'a':
                        print('Server received a')

                    elif menuOption[0] == 'b':
                        print('Server received b')

                    elif menuOption[0] == 'l':
                        print('Server received l')

                    elif menuOption[0] == 'r':
                        print('Server received r')

                    else:
                        print('Server received unexpected input')

                meisterSocket.close()
                print(' ~Closed connection')

        except Exception as listenE:
            print('Server listen error:', str(listenE), file=sys.stderr)
            sys.exit(-1)

    def can_sockets_pickle(self):
        self.serverSocket.listen(5)
        print('Server listening on ', self.serverSocket.getsockname()[1])
        connection, addr = self.serverSocket.accept()
        pickledQ = connection.recv(1024)
        normalQuestion = pickle.loads(pickledQ)
        print(normalQuestion)


class AcceptClientsThread(threading.Thread):
    def __init__(self, contestSocket, listOfClients):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.event.set()
        self.contestSocket = contestSocket
        self.listOfClients = listOfClients

    def run(self):
        self.contestSocket.listen(5)
        while self.event.is_set():
            newClient, newClientAddr = self.contestSocket.accept()
            self.listOfClients.append(newClient)


def main():
    global QuestionBank
    global ContestBank
    contestServer = ContestServer()
    contestServer.startListening()


# RUNTIME STARTS HERE

QuestionBank = {}   # {int questionNumber, Question q}
ContestBank = {}    # {int contestNumber, Contest c}

# Try to load QuestionBank from file
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

# Try to load ContestBank from file
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