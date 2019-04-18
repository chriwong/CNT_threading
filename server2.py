# Project 2 - Server
import os
import pickle
import socket
import sys
import threading
import time
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
            print('Server listening on', self.serverSocket.getsockname()[1])

            while True:
                meisterSocket, meisterSocketAddr = self.serverSocket.accept()
                print('Accepted new connection')

                while True:
                    menuOption = meisterSocket.recv(64).decode()
                    print('>', menuOption)

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
                            meisterSocket.send('Put error: question number already exists'.encode())
                            print('Put error: question number already exists')

                    elif menuOption[0] == 'd':
                        try:
                            delIndex = int(menuOption[2:])
                            del self.QuestionBank[delIndex]
                            meisterSocket.send('Success: question deleted'.encode())
                            print('Success: question deleted')
                        except ValueError:
                            meisterSocket.send('Delete error, number argument invalid'.encode())
                            print('Delete error: number invalid', traceback.format_exc())
                        except KeyError:
                            # The given question number was not in the question bank
                            meisterSocket.send('Delete error: question not found'.encode())
                            print('Delete error: question not found')

                    elif menuOption[0] == 'g':
                        try:
                            retIndex = int(menuOption[2:])
                            retQuestion = self.QuestionBank[retIndex]
                            meisterSocket.send(retQuestion.toString().encode())
                            print('Retrieved question:', retQuestion.number, retQuestion.text)
                        except ValueError:
                            meisterSocket.send('Get error: number argument invalid'.encode())
                            print('Get error: number invalid', traceback.format_exc())
                        except KeyError:
                            meisterSocket.send('Get error: question not found'.encode())
                            print('Get: question not found')

                    elif menuOption[0] == 'k':
                        print('Server received k. Terminating server...')
                        meisterSocket.send('killed'.encode())
                        sys.exit(2)

                    elif menuOption[0] == 'q':
                        print('Server received q. Closing meister socket')
                        break

                    elif menuOption[0] == 'h':
                        print('Server received h')
                        pass

                    elif menuOption[0] == 's':
                        print('Server received s')
                        try:
                            setIndex = int(menuOption[2:])
                            if setIndex not in self.ContestBank:
                                self.ContestBank[setIndex] = Contest(setIndex)
                                meisterSocket.send('Success: contest set'.encode())
                                print('Success: contest set')
                            else:
                                meisterSocket.send('Set error: contest number already exists'.encode())
                                print('Set error: contest number already exists')
                        except ValueError:
                            meisterSocket.send('Set error: numeric arg invalid'.encode())
                            print('Set error: numeric arg invalid')

                    elif menuOption[0] == 'a':
                        print('Server received a')
                        sp = menuOption.find(' ', 3)
                        if sp == -1:
                            meisterSocket.send('Add error: args invalid'.encode())
                            print('Add error: args invalid')
                        else:
                            try:
                                addContestIndex = int(menuOption[2:sp])
                                addQuestionIndex = int(menuOption[sp:])
                                addContest = self.ContestBank[addContestIndex]
                                addQuestion = self.QuestionBank[addQuestionIndex]
                                addContest.questions.append(addQuestion)
                                meisterSocket.send('Success: question added to contest'.encode())
                            except ValueError:
                                meisterSocket.send('Add error: invalid arguments'.encode())
                                print('Add error: invalid arguments')
                            except KeyError:
                                meisterSocket.send('Add error: no such contest/question'.encode())
                                print('Add error: no such contest/question')

                    elif menuOption[0] == 'b':
                        print('Server received b')
                        contestSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        contestSocket.listen(5)
                        print('ContestSocket listening on', self.contestSocket.getsockname()[1])
                        listOfClients = []
                        # acceptClientsThread = AcceptClientsThread(self.contestSocket, listOfClients)
                        # acceptClientsThread.start()
                        # time.sleep(20)
                        # acceptClientsThread.event.clear()
                        # acceptClientsThread.join()
                        # print('JOINED')
                        timeRemaining = 60
                        while timeRemaining > 0:
                            begin = time.time()
                            contestSocket.settimeout(timeRemaining)
                            contestantSocket, contestantSocketAddr = contestSocket.accept()
                            print('NEW CONNECTION')
                            listOfClients.append(contestantSocket)
                            elapsed = time.time() - begin
                            timeRemaining -= elapsed

                    elif menuOption[0] == 'l':
                        print('Server received l')

                    elif menuOption[0] == 'r':
                        print('Server received r')

                    elif menuOption[0] == 'z':
                        for q, v in self.QuestionBank.items():
                            print(q, v.text)

                    elif menuOption[0] == 'y':
                        for c, v in self.ContestBank.items():
                            print('Contest', c)
                            for qs, v in self.ContestBank[c].questions:
                                print(qs, v.text)

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


class AcceptClientsThread(threading.Thread):
    def __init__(self, contestSocket, listOfClients):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.event.set()
        self.contestSocket = contestSocket
        self.listOfClients = listOfClients

    def run(self):
        self.contestSocket.listen(5)
        remaining = 60
        while self.event.is_set():
            newClient, newClientAddr = self.contestSocket.accept()
            print('NEW CONNECTION')
            self.listOfClients.append(newClient)
        print('Should join now...')


# RUNTIME STARTS HERE

contestServer = ContestServer()
contestServer.start_listening()
