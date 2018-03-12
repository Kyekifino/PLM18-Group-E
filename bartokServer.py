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
    global bartokGame
    bartokGame = None
    while bartokGame is None:
        try:
            client, client_address = SERVER.accept()
        except timeout:
            pass
        else:
            if bartokGame is None:
                print("%s:%s has connected." % client_address)
                client.send(bytes("Welcome to the Bartok server! Now type your name and press enter to join!", "utf8"))
                addresses[client] = client_address
                Thread(target=handle_client, args=(client,)).start()
    bartokGame.run()


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

def broadcastToOthers(msg, currentPlayer, youMessage):
    for sock in clients:
        if (clients[sock] == currentPlayer):
            sock.send(youMessage)
        else:
            sock.send(msg)

#----------------------------------------
# Usable commands
#----------------------------------------

def showHand(client, args):
    name = str(clients[client])
    msg = "Hand: " + players[name].getHand()
    client.send(bytes(msg, "utf8"))

def getStatus(client, args):
    global bartokGame
    if bartokGame is None:
        client.send(bytes("!Wait for the game to start...", "utf8"))
    else:
        client.send(bytes("You have " + str(len(players[currentPlayer].hand.cards)) + " cards.", "utf8"))
        for i in players.keys():
            if (i != currentPlayer):
                client.send(bytes(players[i].name + " has " + str(len(players[currentPlayer].hand.cards)) + " cards.", "utf8"))

def playSomeCards(client, args):
    global bartokGame
    global turnFlag
    global victory
    if bartokGame is None:
        client.send(bytes("!Wait for the game to start...", "utf8"))
    elif clients[client] == currentPlayer:

        if (len(args) != 2):
            client.send(bytes("!You must play one card.", "utf8"))
        else:
            myHand = players[currentPlayer].hand.cards
            myCard = Card(args[1][0], args[1][1:])
            if myCard not in myHand:
                client.send(bytes("!You don't have this card! ", "utf8"))
                return
            if myCard.rank == playedDeck.lastCard().rank or myCard.suit == playedDeck.lastCard().suit:
                playedDeck.addToDeck(myCard)
                players[currentPlayer].playCards([] + [myCard])
                broadcast(bytes(currentPlayer + " played " + str(myCard), "utf8"))
                if myCard.rank == '2':
                    players[nextPlayer].draw(2)
                    broadcast(bytes(nextPlayer + " drew two cards! ", "utf8"))
                turnFlag = True
            else:
                client.send(bytes("!You cannot play this card! Play a card from the same suit or rank. ", "utf8"))
                return
    else:
        client.send(bytes("!Wait for your turn...", "utf8"))

def drawCard(client, args):
    global bartokGame
    global turnFlag
    if bartokGame is None:
        client.send(bytes("Wait for the game to start...", "utf8"))
    elif clients[client] == currentPlayer:
        if (len(args) != 1):
            client.send(bytes("Draw uses no arguments! Type {draw}.", "utf8"))
        else:
            if unplayedDeck.isEmpty() and playedDeck.isEmpty():
                client.send(bytes("Both played and unplayed decks are empty, skip the turn.", "utf8"))
            else:
                players[currentPlayer].draw()
                broadcast(bytes(currentPlayer + " drew one card!", "utf8"))
                showHand(client, args)
            turnFlag = True
    else:
        client.send(bytes("Wait for your turn...", "utf8"))

def players(client, args):
    msg = "Current players: "
    """Show names and addresses of all players"""
    for p in clients:
        msg = msg + str(clients[p]) + ", "
    msg = msg[0:-2]
    client.send(bytes(msg, "utf8"))

def playBartok(client, args):
    global bartokGame
    #  
    if bartokGame is None and len(clients) >= 4 and len(clients) <= 9:
        broadcast(bytes("%s has decided to start a game of Bartok!\n" % clients[client], "utf8"))
        broadcast(bytes("There are %d players playing!\n" % len(clients), "utf8"))
        time.sleep(.5)
        broadcast(bytes("To play cards on your turn, write {play} followed by the card.\n", "utf8"))
        broadcast(bytes("For example, write \"{play} H4\" to play the 4 of Hearts.\n", "utf8"))
        broadcast(bytes("In order to play a card, the card must match either the rank or the suite of the displayed card.\n", "utf8"))
        broadcast(bytes("If you cannot play a card, you must draw. To draw the card, write {draw}\n", "utf8"))
        broadcast(bytes("To see your hand, write {hand}. To see the number of cards in each players hand, write {status}. For help, write {help}.\n", "utf8"))
        time.sleep(.5)
        unplayedDeck.fillDeck()
        unplayedDeck.shuffle()
        for p in clients: #Init players
            players[clients[p]] = Player(clients[p])
            players[clients[p]].draw(5)
            # players[clients[p]].hand.cards.append(Card("S", "5"))
        playedDeck.addToDeck(unplayedDeck.draw())
        # playedDeck.addToDeck(Card("S", "7"))
        for p in clients:
            showHand(p, [])
        bartokGame = make(OuterMachine("Welcome to the game!", len(clients)), bartokSpec)
    elif len(clients) < 4:
        client.send(bytes("Not enough players to start!", "utf8"))
    elif len(clients > 9):
        client.send(bytes("Too many players to start!", "utf8"))
    else:
        client.send(bytes("A game of bartok is currently occurring!", "utf8"))

def getHelp(client, args):
    client.send(bytes("To play cards on your turn, write {play} followed by the card.\n", "utf8"))
    client.send(bytes("For example, write \"{play} H4\" to play the 4 of Hearts.\n", "utf8"))
    client.send(bytes("In order to play a card, the card must match either the rank or the suite of the displayed card.\n", "utf8"))
    client.send(bytes("If you cannot play a card, you must draw. To draw the card, write {draw}\n", "utf8"))
    client.send(bytes("To see your hand, write {hand}. To see the number of cards in each players hand, write {status}. For help, write {help}.\n", "utf8"))

#----------------------------------------

commands = { "{users}" : players,
             "{start}" : playBartok,
             "{play}" : playSomeCards,
             "{hand}" : showHand,
             "{status}" : getStatus,
             "{draw}": drawCard,
             "{help}" : getHelp }
clients = {}
addresses = {}
players = {}
bartokGame = None
turnFlag = False
victory = False
currentPlayer = None
nextPlayer = None


HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

#----------------------------------------
# Bartok game specifications
#----------------------------------------
def bartokSpec(m, s, t):

    def timeToExit(i):
        return victory
    def repeatTurns(i):
        return not victory

    m.leave = timeToExit
    m.repeat = repeatTurns
    player = s("player*")
    exitGame = s("exit.")
    t("start", m.true, player)
    t(player, m.repeat, player)
    t(player, m.leave, exitGame)

class Turn(State):
    global victory
    victory = False

    tag = "*"
    currPlayer = 0
    currSuit = 1

    def onEntry(self):
        global currentPlayer
        global nextPlayer
        p = [clients[k] for k in clients]
        currentPlayer = p[self.currPlayer]
        nextPlayer = p[self.currPlayer + 1 if self.currPlayer < self.model.numPlayers - 1 else 0]
        name = str(currentPlayer + " is up! ")
        broadcastToOthers(bytes(name, "utf8"), currentPlayer, bytes("It's your turn!", "utf8"))
        make(InnerMachine(name,self.currPlayer,self.currSuit),bartokTurnSpec).run()

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
        global bartokGame
        global turnFlag
        global victory
        global currentPlayer
        global nextPlayer
        players = {}
        bartokGame = None
        turnFlag = False
        victory = False
        currentPlayer = None
        nextPlayer = None
        playedDeck.resetDeck()
        unplayedDeck.resetDeck()
        broadcast(bytes("Game over!\n", "utf8"))
        return False

#----------------------------------------
# Bartok turn specifications
#----------------------------------------
def bartokTurnSpec(m, s, t):
    def waitForCards(i):
        global turnFlag
        global victory
        m.currCard = playedDeck.lastCard()
        broadcast(bytes("Current card is %s.\n" % str(m.currCard), "utf8"))
        p = [k for k in clients]
        showHand(p[m.currPlayer], [])
        turnFlag = False
        while not turnFlag:
            pass
        if not players[currentPlayer].hand.cards:
            broadcast(bytes("%s emptied their hand! They Win the Game." % currentPlayer, "utf8"))
            victory = True
            return False
        return True
    
    m.playcards = waitForCards
    play = s("play/")
    nextTurn = s("exit=")
    t("start", m.true, play)
    t(play, m.playcards, nextTurn)

class PlayCards(State):
    tag = "/"

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
