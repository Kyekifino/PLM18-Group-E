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
        client.send(bytes("Wait for the game to start...", "utf8"))
    else:
        client.send(bytes("You have " + str(players[currentPlayer].handSize) + " cards.", "utf8"))
        for i in players.keys():
            if (i != currentPlayer):
                client.send(bytes(players[i].name + " has " + str(players[currentPlayer].handSize) + " cards.", "utf8"))

def playSomeCards(client, args):
    global bartokGame
    global turnFlag
    if bartokGame is None:
        client.send(bytes("Wait for the game to start...", "utf8"))
    elif clients[client] == currentPlayer:
        if (len(args) != 1):
            client.send(bytes("You must play one card.", "utf8"))
        else:
            myHand = players[currentPlayer].hand.cards
            myCard = Card(args[0][0], args[0][1:])
            if myCard not in myHand:
                client.send(bytes("You don't have this card!", "utf8"))
                return
            if myCard.rank == playedDeck.lastCard().rank or myCard.suit == playedDeck.lastCard().suit:
                
                broadcast(bytes(currentPlayer + " played " + str(myCard), "utf8"))
                
    # global bartokGame
    # global turnFlag
    # if bartokGame is None:
    #     client.send(bytes("Wait for the game to start...", "utf8"))
    # elif clients[client] == currentPlayer:
    #     myHand = players[currentPlayer].hand.cards
    #     for card in args:
    #         myCard = Card(card[0], card[1:])
    #         if myCard in myHand:
    #             cardsPlayed.append(myCard)
    #     if len(cardsPlayed) > 0:
    #         players[currentPlayer].playCards(cardsPlayed)
    #         broadcast(bytes(currentPlayer + " played " + str(len(cardsPlayed)) + " cards.", "utf8"))
    #         turnFlag = True
    #     else:
    #         client.send(bytes("You must play at least one card.", "utf8"))
    # else:
    #     client.send(bytes("Wait for your turn...", "utf8"))

def players(client, args):
    msg = "Current players: "
    """Show names and addresses of all players"""
    for p in clients:
        msg = msg + str(clients[p]) + ", "
    msg = msg[0:-2]
    client.send(bytes(msg, "utf8"))

def playBartok(client, args):
    global bartokGame
    if bartokGame is None and len(clients) >= 4 and len(clients) <= 9:
        broadcast(bytes("%s has decided to start a game of bartok!\n" % clients[client], "utf8"))
        broadcast(bytes("There are %d players playing!\n" % len(clients), "utf8"))
        time.sleep(.5)
        broadcast(bytes("To play cards on your turn, write {play} followed by the card.\n", "utf8"))
        broadcast(bytes("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades.\n", "utf8"))
        broadcast(bytes("If you think a player played cards that aren't of the current rank, announce {cheat}\n", "utf8"))
        broadcast(bytes("If they were lying, they have to pick up all the played cards... but if the weren't... you do!\n", "utf8"))
        broadcast(bytes("To see your hand, write {hand}. For help, write {help}.\n", "utf8"))
        time.sleep(.5)
        unplayedDeck.fillDeck()
        unplayedDeck.shuffle()
        for p in clients: #Init players
            players[clients[p]] = Player(clients[p])
            players[clients[p]].draw(5)
        playedDeck.addToDeck(unplayedDeck.draw())
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
    client.send(bytes("To play cards on your turn, write {play} followed by the cards.\n", "utf8"))
    client.send(bytes("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades.\n", "utf8"))
    client.send(bytes("If you think a player played cards that aren't of the current rank, announce {cheat}\n", "utf8"))
    client.send(bytes("If they were lying, they have to pick up all the played cards... but if the weren't... you do!\n", "utf8"))
    client.send(bytes("To see your hand, write {hand}. For help, write {help}.\n", "utf8"))

#----------------------------------------

commands = { "{users}" : players,
             "{start}" : playBartok,
             "{play}" : playSomeCards,
             "{hand}" : showHand,
             "{status}" : getStatus,
             "{help}" : getHelp }
clients = {}
addresses = {}
players = {}
bartokGame = None
turnFlag = False
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
def bartokSpec(m, s, t):

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
        broadcast(bytes(name, "utf8"))
        victory = make(InnerMachine(name,i.currPlayer,i.currSuit),bartokTurnSpec).run()

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
        global bartokGame
        global turnFlag
        global victory
        global currentPlayer
        global cardsPlayed
        players = {}
        bartokGame = None
        turnFlag = False
        victory = False
        currentPlayer = None
        cardsPlayed = []
        broadcast(bytes("Game over!\nSay {start} to play again!", "utf8"))
        return True

#----------------------------------------
# Cheat turn specifications
#----------------------------------------
def bartokTurnSpec(m, s, t):
    def waitForCards(i):
        global cardsPlayed
        global turnFlag
        m.currCard = playcards.lastCard()
        broadcast(bytes("Current card is %s. " % str(m.currCard), "utf8"))
        p = [k for k in clients]
        showHand(p[m.currPlayer], [])
        cardsPlayed = []
        turnFlag = False
        while not turnFlag:
            pass
        return True

    m.playcards = waitForCards
    play = s("play/")
    nextTurn = s("exit=")
    t("start", m.true, play)
    t(play, m.playcards, nextTurn)

class PlayCards(State):
    tag = "/"

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
