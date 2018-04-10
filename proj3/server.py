#!/usr/bin/env python3
#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, timeout
from threading import Thread, Timer
from player import Player

#----------------------------------------
# Import a class of the game
#----------------------------------------
gameName = input("Name of the game? ")
GameClass = ""
attempts = 20

while attempts > 0:
    try:
        _temp = __import__(gameName, globals(), locals(), [gameName])
        GameClass = getattr(_temp, gameName)
        break;
    except:
        print('Use a valid game name without .py')
        gameName = input("Name of the game? ")
        attempts -= 1
        continue

if (attempts == 0 and GameClass == ""):
    print('Try again.')
    quit()
#----------------------------------------
# Server side communication
#----------------------------------------
game = None

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global game, gameName
    while True:
        try:
            client, client_address = SERVER.accept()
            if game is None or game.playing is False:
                print("%s:%s has connected." % client_address)
                client.send(bytes(gameName, "utf8"))
                client.send(bytes("Welcome to the " + gameName + " server! Now type your name and press enter to join!", "utf8"))
                Thread(target=handle_client, args=(client,)).start()
            else:
                client.send(bytes("A game is in session. Please come back later...", "utf8"))
        except timeout:
            pass

def wait_for_game():
    global game
    while game is None or game.playing is False:
        pass
    game.runGame()

def handle_client(client):  # Takes client socket as argument.
    global game
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")

    if game is None:
        p = Player(name, client)
        game = GameClass([p])
    else:
        while name in [p.name for p in game.players]:
            client.send(bytes("Another user has that name. Try again.", "utf8"))
            name = client.recv(BUFSIZ).decode("utf8")
        p = Player(name, client)
        game.players.append(p)
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit. To see all people in the room, type {players}. To start the game, type {start}.' % name
    p.tell(welcome)

    msg = "%s has joined the chat!" % name
    game.broadcast(msg)

    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        if msg != "{quit}":
            game.parseAction(p, msg)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            game.broadcast("%s has left the chat." % name)
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
    game = None
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
