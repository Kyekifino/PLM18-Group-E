#!/usr/bin/env python3

#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, timeout
from threading import Thread, Timer
from stateMachineFramework import *
from player import *
from Cards import *



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
                client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
                addresses[client] = client_address
                Thread(target=handle_client, args=(client,)).start()
    cheatGame.run()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    while name in clients.values():
        client.send(bytes("Another user has that name. Try again.", "utf8"))
        name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
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
    print(cheating)
    if len(players[currentPlayer].hand.cards) == 0 and not cheating:
        broadcast(bytes("%s has emptied their hand, and didn't cheat. They win!"))
        return True
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
        broadcast(bytes("%s has decided to start a game of cheat! " % clients[client], "utf8"))
        broadcast(bytes("There are %d players playing! " % len(clients), "utf8"))
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

#----------------------------------------

commands = { "{players}" : players,
             "{start}" : playCheat,
             "{play}" : playSomeCards,
             "{hand}" : showHand,
             "{cheat}" : callCheat }
clients = {}
addresses = {}
players = {}
cheatGame = None
cheating = False
turnFlag = False
cheatFlag = False
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

    def timeToExit(i):
        return player.victory
    def repeatTurns(i):
        return not player.victory

    repeat = 0
    m.leave = timeToExit
    m.repeat = repeatTurns
    player = s("player*")
    exit = s("exit.")
    t("start", m.true, player)
    t(player, m.repeat, player)
    t(player, m.leave, exit)

class Turn(State):
    victory = False

    tag = "*"
    currPlayer = 0
    currSuit = 1

    def onEntry(i):
        global currentPlayer
        p = [clients[k] for k in clients]
        currentPlayer = p[i.currPlayer]
        name = str(currentPlayer + " is up! ")
        broadcast(bytes(name, "utf8"))
        victory = make(InnerMachine(name,i.currPlayer,i.currSuit),cheatTurnSpec).run()

    def onExit(i):
        if i.currPlayer < i.model.numPlayers - 1:
            i.currPlayer += 1
        else:
            i.currPlayer = 0
        if i.currSuit < 13:
            i.currSuit += 1
        else:
            i.currSuit = 1

class GameOver(State):
    tag = "."

    def quit(i):
        return True

    def onExit(i):
        return True

#----------------------------------------
# Cheat turn specifications
#----------------------------------------
def cheatTurnSpec(m, s, t):
    def waitForCards(i):
        global cardsPlayed
        global turnFlag
        cs = m.currRank
        if cs == 1:
            cs = "A"
        if cs == 11:
            cs = "J"
        if cs == 12:
            cs = "Q"
        if cs == 13:
            cs = "K"
        broadcast(bytes("Current rank is %s. " % cs, "utf8"))
        p = [k for k in clients]
        showHand(p[m.currPlayer], [])
        cardsPlayed = []
        turnFlag = False
        while not turnFlag:
            pass
        return True

    def waitForCheat(i):
        global cheatFlag
        global cheating
        cheating = False
        for c in cardsPlayed:
            if c.rank != m.currRank:
                cheating = True
        for c in cardsPlayed:
            playedDeck.addToDeck(c)
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
    finalexit = s("leave!")
    t("start", m.true, play)
    t(play, m.playcards, check)
    t(check, m.cheat, finalexit)
    t(check, m.true, nextTurn)

class PlayCards(State):
    tag = "/"

class Check(State):
    tag = "+"
    currPlayer = 0

class NextTurn(State):
    tag = "="

    def quit(i):
        return True

    def onExit(i):
        return False

class GameOver(State):
    tag = "!"

    def quit(i):
        return True

    def onExit(i):
        return True

#----------------------------------------

if __name__ == "__main__":
    SERVER.settimeout(0.2)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
