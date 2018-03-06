#!/usr/bin/env python3

#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from stateMachineFramework import *
from player import *
from Cards import *



def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global cheatGame
    cheatGame = None
    while True:
        client, client_address = SERVER.accept()
        if cheatGame is None:
            print("%s:%s has connected." % client_address)
            client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
            addresses[client] = client_address
            Thread(target=handle_client, args=(client,)).start()


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
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            if msg not in commands:
                broadcast(msg, name+": ")
            else:
                commands[msg](client)
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

def showHand(client):
    name = str(clients[client])
    msg = "Hand: " + players[name].getHand()
    client.send(bytes(msg, "utf8"))

def players(client):
    msg = "Current players: "
    """Show names and addresses of all players"""
    for p in clients:
        msg = msg + str(clients[p]) + ", "
    msg = msg[0:-2]
    client.send(bytes(msg, "utf8"))

def playCheat(client):
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
            showHand(p)
        cheatGame = make(OuterMachine("Welcome to the game!", len(clients)), cheatSpec).run()
    elif len(clients) < 3:
        client.send(bytes("Not enough players to start!", "utf8"))
    else:
        client.send(bytes("A game of cheat is currently occurring!", "utf8"))


commands = { bytes("{players}", "utf8") : players,
             bytes("{play}", "utf8") : playCheat }
clients = {}
addresses = {}
players = {}
cheatplayers = {}
cheatGame = None


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
        try:
            return i.repeat == 10
        except AttributeError:
            i.repeat = 0
    def repeatTurns(i):
        try:
            i.repeat += 1
        except AttributeError:
            i.repeat = 1
        return i.repeat < 10
    repeat = 0
    m.leave = timeToExit
    m.repeat = repeatTurns
    player = s("player*")
    exit = s("exit.")
    t("start", m.true, player)
    t(player, m.repeat, player)
    t(player, m.leave, exit)

class Turn(State):
    tag = "*"
    currPlayer = 0

    def onEntry(i):
        p = [clients[k] for k in clients]
        name = str(p[i.currPlayer]) + " is up!\n"
        broadcast(bytes(name, "utf8"))
        #make(InnerMachine(name,i.currPlayer),spec001).run()

    def onExit(i):
        if i.currPlayer < i.model.numPlayers - 1:
            i.currPlayer += 1
        else:
            i.currPlayer = 0

class Exit(State):
    tag = "."

    def quit(i):
        return True

    def onExit(i):
        return i

#----------------------------------------

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
