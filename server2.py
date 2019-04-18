# Project 2 - Server
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
        self.QuestionBank = {}
        self.ContestBank = {}

        # Try to load QuestionBank
        try:
            if os.stat('questionbank.pickle').st_size != 0:
                with open('questionbank.pickle', 'rb') as file:
                    print('Loaded QuestionBank from pickle')
                    self.QuestionBank = pickle.load(file)
                    file.close()
            else:
                print('Empty questionbank.pickle found')
        except FileNotFoundError:
            print('No questionbank.pickle found, creating one now...')
            a = open('questionbank.pickle', 'wb+')
            a.close()
        except pickle.PickleError:
            print('Pickling error', traceback.format_exc())

        # Try to load ContestBank
        try:
            if os.stat('contestbank.pickle').st_size != 0:
                with open('contestbank.pickle', 'rb') as file:
                    print('Loaded ContestBank from pickle')
                    self.ContestBank = pickle.load(file)
                    file.close()
            else:
                print('Empty contestbank.pickle found')
        except FileNotFoundError:
            print('No contestbank.pickle found, creating one now...')
            a = open('contestbank.pickle', 'wb+')
            a.close()
        except pickle.PickleError:
            print('Pickling error', traceback.format_exc())

        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.bind((self.host, self.port))
        except Exception as initE:
            print('Server init error:', str(initE), file=sys.stderr)
            print(traceback.format_exc())
            sys.exit(-1)

    def start_listening(self):
        try:
            self.serverSocket.listen(5)
            print('Server listening on ', self.serverSocket.getsockname()[1])

            while True:
                meisterSocket, meisterSocketAddr = self.serverSocket.accept()
                print('Accepted new connection')

                while True:
                    menuOption = meisterSocket.recv(64).decode()
                    print('menuoption:', menuOption)

                    if menuOption[0] == 'p':
                        print('Waiting for pickled question')
                        pickledQuestion = meisterSocket.recv(1024)
                        unpickledQuestion = pickle.loads(pickledQuestion)
                        print('New question:', unpickledQuestion.toString())
                        if unpickledQuestion.number not in self.QuestionBank:
                            self.QuestionBank[unpickledQuestion.number] = unpickledQuestion
                            meisterSocket.send('Success: question added'.encode())
                            print('Success: question added')
                        else:
                            # The given question number already exists in the question bank
                            # Notify the meister as such
                            meisterSocket.send('Error: question number already exists'.encode())
                            print('Error: question number already exists')

                    elif menuOption[0] == 'd':
                        try:
                            delIndex = int(menuOption[2:])
                            del self.QuestionBank[delIndex]
                            meisterSocket.send('Success: question deleted'.encode())
                            print('Success: question deleted')
                        except ValueError:
                            meisterSocket.send('Error, number argument invalid'.encode())
                            print('Deletion error: number invalid', traceback.format_exc())
                        except KeyError:
                            # The given question number was not in the question bank
                            meisterSocket.send('Error: question not found'.encode())
                            print('Error: question not found')

                    elif menuOption[0] == 'g':
                        try:
                            retIndex = int(menuOption[2:])
                            retQuestion = self.QuestionBank[retIndex]
                            meisterSocket.send(retQuestion.toString().encode())
                            print('Retrieved question:', retQuestion.number, retQuestion.text)
                        except ValueError:
                            meisterSocket.send('Error: number argument invalid'.encode())
                            print('Retrieval error: number invalid', traceback.format_exc())
                        except KeyError:
                            meisterSocket.send('Error: question not found'.encode())
                            print('Error: question not found')

                    elif menuOption[0] == 'k':
                        print('Server received k. Terminating server...')
                        meisterSocket.send('killed'.encode())
                        sys.exit(2)

                    elif menuOption[0] == 'q':
                        print('Server received q. Closing meister socket')
                        meisterSocket.close()

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

                    elif menuOption[0] == 'z':
                        for q in self.QuestionBank:
                            print(q)

                    else:
                        print('Server received unexpected input')

                    try:
                        with open('questionbank.pickle', 'wb+') as file:
                            pickle.dump(self.QuestionBank, file)
                            file.close()
                    except pickle.PickleError:
                        print('Pickling error', traceback.format_exc())

                meisterSocket.close()
                print(' ~Closed connection')

        except Exception as listenE:
            print('Server listen error:', str(listenE), file=sys.stderr)
            print(traceback.format_exc())
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


# RUNTIME STARTS HERE

contestServer = ContestServer()
contestServer.start_listening()
