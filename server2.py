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

    def to_string(self):
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
        self.maxCorrect = 0

    def to_string(self):
        s = ''
        s = s + str(self.number) + '\t'
        s = s + str(len(self.questions)) + ' question(s), '
        s = s + 'run, ' if self.executed else s + 'not run'
        if len(self.questions) != 0 and self.executed:
            s = s + 'average correct: ' + str(avg(self.correctness)) + '; '
            s = s + 'maximum correct: ' + str(self.maxCorrect)
        return s


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
                    print('Loaded questions from questionbank.pickle')
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
                    print('Loaded contests from contestbank.pickle')
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
        except Exception:
            print('Server init error:', traceback.format_exc(), file=sys.stderr)
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
                    print('From meister >', menuOption)

                    if menuOption[0] == 'p':
                        print('Waiting for pickled question')
                        pickledQuestion = meisterSocket.recv(1024)
                        unpickledQuestion = pickle.loads(pickledQuestion)
                        print('New question:', unpickledQuestion.to_string())
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
                            meisterSocket.send(retQuestion.to_string().encode())
                            print('Retrieved question:', retQuestion.number, retQuestion.text)
                        except ValueError:
                            meisterSocket.send('Get error: number argument invalid'.encode())
                            print('Get error: number invalid', traceback.format_exc())
                        except KeyError:
                            meisterSocket.send('Get error: question not found'.encode())
                            print('Get: question not found')

                    elif menuOption[0] == 'k':
                        print('Terminating server...')
                        meisterSocket.send('killed'.encode())
                        sys.exit(2)

                    elif menuOption[0] == 'q':
                        print('Closing meister socket')
                        break

                    elif menuOption[0] == 'h':
                        pass

                    elif menuOption[0] == 's':
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
                        try:
                            beginIndex = int(menuOption[2:])
                            beginContest = self.ContestBank[beginIndex]
                            if len(beginContest.questions) != 0:
                                contestThread = threading.Thread(target=start_contest, args=(beginContest,))
                                contestThread.start()
                                print('Started contest thread')
                            else:
                                meisterSocket.send('Begin error: contest has no questions'.encode())
                                print('Begin error: contest has no questions')
                        except KeyError:
                            meisterSocket.send('Begin error: no such contest'.encode())
                            print('Begin error: no such contest')

                    elif menuOption[0] == 'l':
                        if len(self.ContestBank) == 0:
                            meisterSocket.send('No contests set yet'.encode())
                            print('No contests set yet')
                        else:
                            print('Listing contests:')
                            ls = ''
                            for contest in self.ContestBank.values():
                                ls = ls + contest.to_string() + '\n'
                                print(contest.to_string(), sep='\n')
                            meisterSocket.send(ls.encode())

                    elif menuOption[0] == 'r':
                        try:
                            reviewIndex = int(menuOption[2:])
                            reviewContest = self.ContestBank[reviewIndex]
                            rs = reviewContest.to_string()
                            print(reviewContest.to_string())
                            for q in zip(reviewContest.questions, reviewContest.correctness):
                                rs = rs + '\t' + q[0].number + '\t' + str(float(q[1])*100) + ' % correct\n'
                                print('\t', q[0].number, '\t', str(float(q[1])*100), '% correct', sep='', end='\n')
                            meisterSocket.send(rs.encode())

                        except KeyError:
                            meisterSocket.send('Begin error: no such contest'.encode())
                            print('Begin error: no such contest')

                    elif menuOption[0] == 'z':
                        print('~Debugger: list questions')
                        for q, v in self.QuestionBank.items():
                            print(q, v.text)

                    elif menuOption[0] == 'y':
                        print('~Debugger: list contests')
                        for c, v in self.ContestBank.items():
                            print('Contest', c)
                            for q in self.ContestBank[c].questions:
                                print(q.number, q.text)

                    else:
                        print('Server received unexpected input')

                    try:
                        with open('questionbank.pickle', 'wb+') as file:
                            pickle.dump(self.QuestionBank, file)
                            file.close()
                    except pickle.PickleError:
                        print('Pickling error', traceback.format_exc())

                    try:
                        with open('contestbank.pickle', 'wb+') as file:
                            pickle.dump(self.ContestBank, file)
                            file.close()
                    except pickle.PickleError:
                        print('Pickling error', traceback.format_exc())

                meisterSocket.close()
                print(' ~Closed connection')

        except Exception:
            print('Server listen error:', traceback.format_exc(), file=sys.stderr)
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


def start_contest(contest):
    listOfClients = []
    contestSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    contestSocket.listen(5)
    print('ContestSocket listening on', contestSocket.getsockname()[1])
    # acceptClientsThread = AcceptClientsThread(self.contestSocket, listOfClients)
    # acceptClientsThread.start()
    # time.sleep(20)
    # acceptClientsThread.event.clear()
    # acceptClientsThread.join()
    # print('JOINED')
    timeRemaining = 20
    while timeRemaining > 0:
        try:
            print('timeRemaining:', timeRemaining)
            begin = time.time()
            contestSocket.settimeout(timeRemaining)
            contestantSocket, contestantSocketAddr = contestSocket.accept()
            print('NEW CONNECTION')
            listOfClients.append(contestantSocket)
            elapsed = time.time() - begin
            timeRemaining -= elapsed
        except socket.timeout:
            print('Time\'s up! Let\'s begin!')
            break
    print('Here are our contestants:')
    for x in listOfClients:
        print(x)


def avg(arr):
    total = 0
    for a in arr:
        total += a
    return total/len(arr)


# RUNTIME STARTS HERE

contestServer = ContestServer()
contestServer.start_listening()
