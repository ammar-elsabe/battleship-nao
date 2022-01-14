from __future__ import print_function
from array import *
import time
import random
import math
from naoqi import ALProxy
from naoqi import *

def letterToNum(letter):
    i = 1
    for x in "abcdefghijklmnopqrstuvwxyz":
        if(x == letter):
            break
        i += 1
    return i

def numToLetter(num):
    i = ord('a')
    for x in [1,2,3,4,5,6,7,8,9,10]:
        if(x == num):
            break
        i += 1
    return chr(i)

class naoAudio():
    def __init__(self):
        self.__sr = ALProxy("ALSpeechRecognition", os.environ.get('IP'), 9559)
        self.__tts = ALProxy("ALTextToSpeech", os.environ.get('IP'), 9559)
        self.__mem = ALProxy("ALMemory", os.environ.get('IP'), 9559)
        self.__sruser = "sruser"


    def listen(self, wordList, recTime = 5.0):
        self.__sr.setLanguage("English")
        self.__sr.setVocabulary(wordList, False)
        self.__sr.subscribe(self.__sruser)
        print('Speech recognition engine started')
        self.__sr.pause(False)
        time.sleep(recTime)
        self.__sr.pause(True)
        self.__sr.unsubscribe(self.__sruser)
        self.__mem.subscribeToEvent('WordRecognized',self.__sruser,'wordRecognized')
        text = self.__mem.getData("WordRecognized")
        if text[1] > 0.3:
            print(text[0])
            return str(text[0])
        else:
            self.say("I didn't quite get that, can you repeat?")
        try:
            self.__mem.unsubscribeToEvent('WordRecognized', "wordRecognized")
        except:
            pass
        self.__sruser += "x"
    
    def say(self, message):
        self.__tts.say(message)

naoIO = naoAudio()

class battleships:
    def __init__(self):
        self.__grid = [[0]*10 for _ in range(10)]
        self.__ships = 'CBSDP'
        self.__shipsSunk = 0
        self.__naoShipsSunk = 0
        self.__previouslyAttacked = [[0]*10 for _ in range(10)]
        self.__hitByEnemy = 0
        self.__airCarrier = 0
        self.__battleship = 0
        self.__submarine = 0
        self.__destroyer = 0
        self.__patrolBoat= 0
        for x in self.__ships:
            if(x=='C'):
                size = 5
            elif(x=='B'):
                size = 4
            elif(x=='S' or x=='D'):
                size = 3
            elif(x=='P'):
                size = 2
            horizontal = bool(random.getrandbits(1))
            if(horizontal):
                rowNum = random.randint(0,9)
                colNum = random.randint(0,9-size)
                while True:
                    for i in range(colNum, colNum+size):
                        clash = self.__grid[rowNum][i] != 0
                        if(clash):
                            rowNum = random.randint(0,9)
                            colNum = random.randint(0,9-size)
                            break
                    if(not clash):
                        break
                for i in range(colNum, colNum+size):
                    self.__grid[rowNum][i]= x
            else:
                colNum = random.randint(0,9)
                rowNum = random.randint(0,9-size)
                while True:
                    for i in range(rowNum, rowNum+size):
                        clash=self.__grid[i][colNum] != 0
                        if(clash):
                            colNum = random.randint(0,9)
                            rowNum = random.randint(0,9-size)
                            break
                    if(not clash):
                        break
                for i in range(rowNum, rowNum+size):
                    self.__grid[i][colNum] = x
    def attack(self):
        row = random.randint(0,9)
        row = row if row%2==0 else (row+1)%10
        col = random.randint(0,9)
        col = col if row%2==0 else (col+1)%10
        if self.__previouslyAttacked[row][col] != 0:
            for i in range(10):
                for j in range(10):
                    if self.__previouslyAttacked[i][j] == 0:
                        row = i
                        col = j
        naoIO.say("I attack ")
        naoIO.say(numToLetter(row + 1))
        naoIO.say(str(col + 1))
        naoIO.say("Was that a hit, a miss, or did it sink a ship?")
        while True:
            result = naoIO.listen(["hit", "miss", "sink", "can you repeat"])
            if result == "hit" or result == "sink":
                self.__previouslyAttacked[row][col] = "X"
                if result == "sink":
                    self.__shipsSunk+=1
                break
            elif result == "miss":
                self.__previouslyAttacked[row][col] = "O"
                break
            elif result == "can you repeat":
                naoIO.say("Sure")
                naoIO.say("I attack ")
                naoIO.say(numToLetter(row + 1))
                naoIO.say(str(col + 1))
            else:
                naoIO.say("I didn't quite get that, may you repeat?")
        print("Nao's blank grid:")
        self.printGrid(self.__previouslyAttacked)
                
    def didIWin(self):
        return self.__shipsSunk == 5
    
    def didILose(self):
        return self.__naoShipsSunk == 5

    def underAttack(self):
        wordlist = []
        x = ord('a')
        i=1
        for _ in range(100):
            wordlist.append(chr(x) + ' ' + str(i))
            i+=1
            if(i>10):
                i = 1
                x += 1
        col = None
        row = None
        naoIO.say("Which co ordinate do you wish to attack?")
        while True:
            retrievedInput = naoIO.listen(wordlist)
            row = letterToNum(retrievedInput[0]) - 1
            try:
                col = int(retrievedInput[2] + retrievedInput[3]) - 1
            except:
                try:
                    col = int(retrievedInput[2]) - 1
                except:
                    naoIO.say("I didn't quite get that, please repeat")
                    continue
            naoIO.say("Did you say")
            naoIO.say(numToLetter(row+1))
            naoIO.say(str(col+1))
            yn = naoIO.listen(["yes", "no"])
            if(yn == "yes"):
                break
            elif(yn == "no"):
                naoIO.say("OK, can you repeat?")
                wordlist.remove(numToLetter(row+1) + " " + str(col+1))
            else:
                while True:
                    naoIO.say("Was that a yes? Or a no?")
                    yn = naoIO.listen(["yes", "no"])
                    if(yn == "yes"):
                        break
                    elif yn == "no":
                        naoIO.say("OK, can you repeat?")
                        wordlist.remove(numToLetter(row+1) + " " + str(col+1))
                        break
                if(yn == "yes"):
                    break
        print("row to be attacked", row)
        print("col to be attacked", col)
        while self.__grid[row][col]=='X' or self.__grid[row][col]=='O':
            print("You cannot shoot at a previously shot at coordinate")
            naoIO.say("You cannot shoot at a previously shot at coordinate")
            naoIO.say("Which co ordinate do you wish to attack?")
            while True:
                retrievedInput = naoIO.listen(wordlist)
                row = letterToNum(retrievedInput[0]) - 1
                try:
                    col = int(retrievedInput[2] + retrievedInput[3]) - 1
                except:
                    try:
                        col = int(retrievedInput[2]) - 1
                    except:
                        naoIO.say("I didn't quite get that, please repeat")
                        continue
                naoIO.say("Did you say")
                naoIO.say(numToLetter(row+1))
                naoIO.say(str(col+1))
                yn = naoIO.listen(["yes", "no"])
                if(yn == "yes"):
                    break
                elif(yn == "no"):
                    naoIO.say("OK, can you repeat?")
                    wordlist.remove(numToLetter(row+1) + " " + str(col+1))
                else:
                    while True:
                        naoIO.say("Was that a yes? Or a no?")
                        yn = naoIO.listen(["yes", "no"])
                        if(yn == "yes"):
                            break
                        elif yn == "no":
                            naoIO.say("OK, can you repeat?")
                            wordlist.remove(numToLetter(row+1) + " " + str(col+1))
                            break
                    if(yn == "yes"):
                        break
                        
            print("row to be attacked", row)
            print("col to be attacked", col)
        if(self.__grid[row][col]!=0):
            self.__hitByEnemy+=1
            naoIO.say("hit")
            if(self.__grid[row][col]  == 'C'):
                self.__airCarrier+=1
                if self.__airCarrier==5:
                    print('\033[1m' + "The air carrier has sunk" + '\033[0m')
                    self.__naoShipsSunk += 1
                    print(self.__naoShipsSunk, "have sunk")
                    naoIO.say("sink")
            elif(self.__grid[row][col]  == 'B'):
                self.__battleship+=1
                if self.__battleship==4:
                    print('\033[1m' + "The battleship has sunk" + '\033[0m')
                    self.__naoShipsSunk += 1
                    print(self.__naoShipsSunk, "have sunk")
                    naoIO.say("sink")
            elif(self.__grid[row][col]  == 'S'):
                self.__submarine+=1
                if self.__submarine==3:
                    print('\033[1m' + "The submarine has sunk" + '\033[0m')
                    self.__naoShipsSunk += 1
                    print(self.__naoShipsSunk, "have sunk")
                    naoIO.say("sink")
            elif(self.__grid[row][col]  == 'D'):
                self.__destroyer+=1
                if self.__destroyer==3:
                    print('\033[1m' + "The destroyer has sunk" + '\033[0m')
                    self.__naoShipsSunk += 1
                    print(self.__naoShipsSunk, "have sunk")
                    naoIO.say("sink")
            elif(self.__grid[row][col]  == 'P'):
                self.__patrolBoat+=1
                if self.__patrolBoat==2:
                    print('\033[1m' + "The patrol boat has sunk" + '\033[0m')
                    self.__naoShipsSunk += 1
                    print(self.__naoShipsSunk, "have sunk")
                    naoIO.say("sink")
            self.__grid[row][col]='X'        
        else:
            print("The attack has missed")
            naoIO.say("miss")
            self.__grid[row][col]='O'
        print("Nao's grid:")
        self.printGrid(self.__grid)
    def printGrid(self, gridArg):
        i = ord('A')
        for x in (" ", 1,2,3,4,5,6,7,8,9,10):
            print('\033[1m' + '{:>2}'.format(x) + '\033[0m',end = " ")
        print('\n')
        for r in gridArg:
            print('\033[1m' + '{:>2}'.format(chr(i)) + '\033[0m',end = " ")
            i+=1
            for c in r:
                if(c=='X'):
                    print('\033[91m' + '{:>2}'.format(c) + '\033[0m',end = " ")
                elif(c=='O'):
                    print('\033[94m' + '{:>2}'.format(c) + '\033[0m',end = " ")
                elif(c!=0):
                    print('\033[93m' + '{:>2}'.format(c) + '\033[0m',end = " ")
                else:
                    print('{:>2}'.format(c),end = " ")
            print('\n')

trials = 0
naoAI = battleships()
naoIO.say("Let's play pen and paper battleship!")
ready = False
while not ready:
    naoIO.say("Please tell me when you have your grids ready")
    ready = naoIO.listen(["ready"]) == "ready"
naoIO.say("Alright, I will attack first")
while True:
    naoAI.attack()
    if naoAI.didIWin():
        naoIO.say("I win! Better luck next time!")
        print('\033[91m' + "Game Over" + '\033[0m')
        print("You lost after ",trials , "tries, better luck next time!")
        break
    naoIO.say("Now your turn")
    naoAI.underAttack()
    trials+=1
    if naoAI.didILose():
        naoIO.say("Good Game! Hopefully my master makes my algorithm better so that I can defeat you next time!")
        print('\033[92m' + "You Win!" + '\033[0m')
        print("You won after ",trials ,"tries, congratulations!")
        break
