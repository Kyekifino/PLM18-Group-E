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
    broadcast(msg)
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        msglist = msg.split()
        if msglist[0] != "{quit}":
            if msglist[0] not in commands:
                broadcast(msg, name+": ")
            else:
                commands[msglist[0]](client, msglist)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast("%s has left the chat." % name)
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8") + bytes(msg, "utf8"))

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
            broadcast(currentPlayer + " played " + str(len(cardsPlayed)) + " cards.")
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
        cheatFlag = False
        broadcast("%s has called cheat... " % clients[client])
        if cheating:
            broadcast("%s was cheating, and has to pick up the stack! " % currentPlayer)
            players[currentPlayer].takeAll()
        else:
            broadcast("%s wasn't cheating... %s has to pick up the stack..." % (currentPlayer, clients[client]))
            players[clients[client]].takeAll()
    else:
        broadcast("Can't call cheat now.")
    return False


def playCheat(client, args):
    global cheatGame
    if cheatGame is None and len(clients) >= 3:
        broadcast("%s has decided to start a game of cheat!\n" % clients[client])
        broadcast("There are %d players playing!\n" % len(clients))
        time.sleep(.5)
        broadcast("To play cards on your turn, write {play} followed by the cards.\n")
        broadcast("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades.\n")
        broadcast("If you think a player played cards that aren't of the current rank, announce {cheat}\n")
        broadcast("If they were lying, they have to pick up all the played cards... but if the weren't... you do!\n")
        broadcast("To see your hand, write {hand}. For help, write {help}.\n")
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
        cheatGame = make(OuterMachine("Welcome to the game!", len(clients), None), cheatSpec)
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

    def timeToExit(i):
        return victory
    def repeatTurns(i):
        return not victory

    repeat = 0
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

    def onEntry(i):
        global currentPlayer
        p = [clients[k] for k in clients]
        currentPlayer = p[i.currPlayer]
        name = str(currentPlayer + " is up! ")
        broadcast(name)
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
        broadcast("Game over!\nSay {start} to play again!")
        return True

#----------------------------------------
# Cheat turn specifications
#----------------------------------------
def cheatTurnSpec(m, s, t):
    def waitForCards(i):
        global cardsPlayed
        global turnFlag
        m.currRank = m.game
        if m.currRank == 1:
            m.currRank = "A"
        if m.currRank == 11:
            m.currRank = "J"
        if m.currRank == 12:
            m.currRank = "Q"
        if m.currRank == 13:
            m.currRank = "K"
        broadcast("Current rank is %s. " % m.currRank)
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
        global victory
        cheating = False
        m.currRank = m.game
        for c in cardsPlayed:
            if str(c.rank) != str(m.currRank):
                print(c.rank, m.currRank)
                cheating = True
        print(cheating)
        for c in cardsPlayed:
            playedDeck.addToDeck(c)
        if not players[currentPlayer].hand.cards:
            broadcast("%s emptied their hand!" % currentPlayer)
            time.sleep(1)
            if cheating:
                broadcast("%s was cheating with their final play, and must pick up the deck!" % currentPlayer)
                players[currentPlayer].takeAll()
            else:
                broadcast("%s wasn't cheating... and wins!" % currentPlayer)
                victory = True
                return False
        else:
            broadcast("You have five seconds to announce {cheat}.")
            cheatFlag = True
            def timeout():
                cheatFlag = False
            t = Timer(5 , timeout)
            t.start()
            t.join()
            if cheatFlag:
                broadcast("Time's up!")
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

    def onEntry(i):
        print("Entered into check state. Should determine cheating.")

    def quit(i):
        return victory

    def onExit(i):
        return True

class NextTurn(State):
    tag = "="

    def quit(i):
        return True

    def onEntry(i):
        print("Entered into next turn state. Should move to next turn.")

    def onExit(i):
        return False

class GameOver(State):
    tag = "!"

    def quit(i):
        return True

    def onEntry(i):
        print("Entered into game over state. Should end for real.")

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
