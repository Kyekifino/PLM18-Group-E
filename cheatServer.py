#!/usr/bin/env python3

#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Server for multithreaded (asynchronous) chat application."""
import time
from socket import AF_INET, socket, SOCK_STREAM, timeout
from threading import Thread, Timer
from stateMachineFramework import State, OuterMachine, InnerMachine, make
from player import playedDeck, unplayedDeck, Player
from cards import Card



def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global cheatGame
    cheatGame = None
    while cheatGame is None:
        try:
            client, client_address = SERVER.accept()
        except timeout:
            pass
        else:
            if cheatGame is None:
                print("%s:%s has connected." % client_address)
                client.send(bytes("Welcome to the Cheat server! Now type your name and press enter to join!", "utf8"))
                addresses[client] = client_address
                Thread(target=handle_client, args=(client,)).start()
    cheatGame.run()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    while name in clients.values():
        client.send(bytes("Another user has that name. Try again.", "utf8"))
        name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit. To see all users in the room, type {users}. To start the game, type {start}.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        msglist = msg.split()
        if msglist[0] != "{quit}":
            if msglist[0] not in commands:
                broadcast(bytes(msg, "utf8"), name+": ")
            else:
                commands[msglist[0]](client, msglist)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

#----------------------------------------
# Usable commands
#----------------------------------------

def showHand(client, args):
    name = str(clients[client])
    msg = "Hand: " + players[name].getHand()
    client.send(bytes(msg, "utf8"))

def playSomeCards(client, args):
    global cheatGame
    global turnFlag
    if cheatGame is None:
        client.send(bytes("Wait for the game to start...", "utf8"))
    elif clients[client] == currentPlayer:
        myHand = players[currentPlayer].hand.cards
        for card in args:
            myCard = Card(card[0], card[1:])
            if myCard in myHand:
                cardsPlayed.append(myCard)
        if len(cardsPlayed) > 0:
            players[currentPlayer].playCards(cardsPlayed)
            broadcast(bytes(currentPlayer + " played " + str(len(cardsPlayed)) + " cards.", "utf8"))
            turnFlag = True
        else:
            client.send(bytes("You must play at least one card.", "utf8"))
    else:
        client.send(bytes("Wait for your turn...", "utf8"))

def players(client, args):
    msg = "Current players: "
    """Show names and addresses of all players"""
    for p in clients:
        msg = msg + str(clients[p]) + ", "
    msg = msg[0:-2]
    client.send(bytes(msg, "utf8"))

def callCheat(client, args):
    global cheatFlag
    global cheating
    if cheatFlag:
        broadcast(bytes("%s has called cheat... " % clients[client], "utf8"))
        if cheating:
            broadcast(bytes("%s was cheating, and has to pick up the stack! " % currentPlayer, "utf8"))
            players[currentPlayer].takeAll()
        else:
            broadcast(bytes("%s wasn't cheating... %s has to pick up the stack..." % (currentPlayer, clients[client]), "utf8"))
            players[clients[client]].takeAll()
    else:
        broadcast(bytes("Can't call cheat now.", "utf8"))
    return False


def playCheat(client, args):
    global cheatGame
    if cheatGame is None and len(clients) >= 3:
        broadcast(bytes("%s has decided to start a game of cheat!\n" % clients[client], "utf8"))
        broadcast(bytes("There are %d players playing!\n" % len(clients), "utf8"))
        time.sleep(.5)
        broadcast(bytes("To play cards on your turn, write {play} followed by the cards.\n", "utf8"))
        broadcast(bytes("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades.\n", "utf8"))
        broadcast(bytes("If you think a player played cards that aren't of the current rank, announce {cheat}\n", "utf8"))
        broadcast(bytes("If they were lying, they have to pick up all the played cards... but if the weren't... you do!\n", "utf8"))
        broadcast(bytes("To see your hand, write {hand}. For help, write {help}.\n", "utf8"))
        time.sleep(.5)
        unplayedDeck.fillDeck()
        unplayedDeck.shuffle()
        for p in clients: #Init players
            players[clients[p]] = Player(clients[p])
        while not unplayedDeck.isEmpty():
            for p in players:
                if not unplayedDeck.isEmpty():
                    players[p].draw()
        for p in clients:
            showHand(p, [])
        cheatGame = make(OuterMachine("Welcome to the game!", len(clients)), cheatSpec)
    elif len(clients) < 3:
        client.send(bytes("Not enough players to start!", "utf8"))
    else:
        client.send(bytes("A game of cheat is currently occurring!", "utf8"))

def getHelp(client, args):
    client.send(bytes("To play cards on your turn, write {play} followed by the cards.\n", "utf8"))
    client.send(bytes("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades.\n", "utf8"))
    client.send(bytes("If you think a player played cards that aren't of the current rank, announce {cheat}\n", "utf8"))
    client.send(bytes("If they were lying, they have to pick up all the played cards... but if the weren't... you do!\n", "utf8"))
    client.send(bytes("To see your hand, write {hand}. For help, write {help}.\n", "utf8"))

#----------------------------------------

commands = { "{users}" : players,
             "{start}" : playCheat,
             "{play}" : playSomeCards,
             "{hand}" : showHand,
             "{cheat}" : callCheat,
             "{help}" : getHelp }
clients = {}
addresses = {}
players = {}
cheatGame = None
cheating = False
turnFlag = False
cheatFlag = False
victory = False
currentPlayer = None
cardsPlayed = []


HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

#----------------------------------------
# Cheat game specifications
#----------------------------------------
def cheatSpec(m, s, t):

    def timeToExit(self):
        return victory
    def repeatTurns(self):
        return not victory

    m.leave = timeToExit
    m.repeat = repeatTurns
    player = s("player*")
    exit = s("exit.")
    t("start", m.true, player)
    t(player, m.repeat, player)
    t(player, m.leave, exit)

class Turn(State):
    global victory
    victory = False

    tag = "*"
    currPlayer = 0
    currSuit = 1

    def onEntry(self):
        global currentPlayer
        p = [clients[k] for k in clients]
        currentPlayer = p[self.currPlayer]
        name = str(currentPlayer + " is up! ")
        broadcast(bytes(name, "utf8"))
        victory = make(InnerMachine(name,self.currPlayer,self.currSuit),cheatTurnSpec).run()

    def onExit(self):
        if self.currPlayer < self.model.numPlayers - 1:
            self.currPlayer += 1
        else:
            self.currPlayer = 0
        if self.currSuit < 13:
            self.currSuit += 1
        else:
            self.currSuit = 1

class GameOver(State):
    tag = "."

    def quit(self):
        return True

    def onExit(self):
        global players
        global cheatGame
        global cheating
        global turnFlag
        global cheatFlag
        global victory
        global currentPlayer
        global cardsPlayed
        players = {}
        cheatGame = None
        cheating = False
        turnFlag = False
        cheatFlag = False
        victory = False
        currentPlayer = None
        cardsPlayed = []
        broadcast(bytes("Game over!\nSay {start} to play again!", "utf8"))
        return True

#----------------------------------------
# Cheat turn specifications
#----------------------------------------
def cheatTurnSpec(m, s, t):
    def waitForCards(self):
        global cardsPlayed
        global turnFlag
        if m.currRank == 1:
            m.currRank = "A"
        if m.currRank == 11:
            m.currRank = "J"
        if m.currRank == 12:
            m.currRank = "Q"
        if m.currRank == 13:
            m.currRank = "K"
        broadcast(bytes("Current rank is %s. " % m.currRank, "utf8"))
        p = [k for k in clients]
        showHand(p[m.currPlayer], [])
        cardsPlayed = []
        turnFlag = False
        while not turnFlag:
            pass
        return True

    def waitForCheat(self):
        global cheatFlag
        global cheating
        global victory
        cheating = False
        for c in cardsPlayed:
            if str(c.rank) != str(m.currRank):
                print(c.rank, m.currRank)
                cheating = True
        print(cheating)
        for c in cardsPlayed:
            playedDeck.addToDeck(c)
        if not players[currentPlayer].hand.cards:
            broadcast(bytes("%s emptied their hand!" % currentPlayer, "utf8"))
            time.sleep(1)
            if cheating:
                broadcast(bytes("%s was cheating with their final play, and must pick up the deck!" % currentPlayer, "utf8"))
                players[currentPlayer].takeAll()
            else:
                broadcast(bytes("%s wasn't cheating... and wins!" % currentPlayer, "utf8"))
                victory = True
                return False
        else:
            broadcast(bytes("You have five seconds to announce {cheat}.", "utf8"))
            cheatFlag = True
            def timeout():
                cheatFlag = False
            t = Timer(5 , timeout)
            t.start()
            t.join()
            broadcast(bytes("Time's up!", "utf8"))
        time.sleep(1)
        return True

    m.playcards = waitForCards
    m.cheat = waitForCheat
    play = s("play/")
    check = s("check+")
    nextTurn = s("exit=")
    t("start", m.true, play)
    t(play, m.playcards, check)
    t(check, m.cheat, nextTurn)

class PlayCards(State):
    tag = "/"

class Check(State):
    tag = "+"

    def onEntry(self):
        print("Entered into check state. Should determine cheating.")

    def quit(self):
        return victory

    def onExit(self):
        return True

class NextTurn(State):
    tag = "="

    def quit(self):
        return True

    def onEntry(self):
        print("Entered into next turn state. Should move to next turn.")

    def onExit(self):
        return False

#----------------------------------------

if __name__ == "__main__":
    SERVER.settimeout(0.2)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
