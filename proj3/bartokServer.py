#!/usr/bin/env python3

#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, timeout
from threading import Thread, Timer
from Bartok import *
from player import *

bartokGame = None

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global bartokGame
    while True:
        try:
            client, client_address = SERVER.accept()
            if bartokGame is None or bartokGame.playing is False:
                print("%s:%s has connected." % client_address)
                client.send(bytes("Welcome to the Bartok server! Now type your name and press enter to join!", "utf8"))
                Thread(target=handle_client, args=(client,)).start()
            else:
                client.send(bytes("A game is in session. Please come back later...", "utf8"))
        except timeout:
            pass

def wait_for_game():
    global bartokGame
    while bartokGame is None or bartokGame.playing is False:
        pass
    bartokGame.runGame()

def handle_client(client):  # Takes client socket as argument.
    global bartokGame
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")

    if bartokGame is None:
        p = Player(name, client)
        bartokGame = Bartok([p])
    else:
        while name in [p.name for p in bartokGame.players]:
            client.send(bytes("Another user has that name. Try again.", "utf8"))
            name = client.recv(BUFSIZ).decode("utf8")
        p = Player(name, client)
        bartokGame.players.append(p)
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit. To see all people in the room, type {players}. To start the game, type {start}.' % name
    p.tell(welcome)

    msg = "%s has joined the chat!" % name
    bartokGame.broadcast(msg)

    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        if msg != "{quit}":
            bartokGame.parseAction(p, msg)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            bartokGame.broadcast("%s has left the chat." % name)
            break

#----------------------------------------
HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

#----------------------------------------

if __name__ == "__main__":
    bartokGame = None
    SERVER.settimeout(0.2)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    GAME_THREAD = Thread(target=wait_for_game)
    GAME_THREAD.start()
    GAME_THREAD.join()
    ACCEPT_THREAD.join()
    SERVER.close()
