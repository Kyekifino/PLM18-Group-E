#!/usr/bin/env python3

#Boiler plate code taken from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

nameSet = False
top = tkinter.Tk()
top.title("Card Game")
gameName = False

def receive():
    """Handles receiving of messages."""
    global nameSet
    global gameName
    while True:
        try:
            if gameName == False:
                gameName = client_socket.recv(BUFSIZ).decode("utf8")
                top.title(gameName)
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if "Another user has that name. Try again." in msg:
                nameSet = False
                top.title(gameName)
            msg_list.config(state=tkinter.NORMAL)
            msg_list.insert(tkinter.END, msg + "\n")
            msg_list.see(tkinter.END)
            msg_list.config(state=tkinter.DISABLED)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global nameSet
    global gameName
    msg = my_msg.get()
    if not nameSet:
        top.title(gameName + ": " + msg)
        nameSet = True
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Your name here...")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Text(messages_frame, height=20, width=75, yscrollcommand=scrollbar.set, wrap=tkinter.WORD)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
msg_list.config(state=tkinter.DISABLED)
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg, width=50)
entry_field.bind("<Return>", send)
entry_field.bind("<FocusIn>", lambda args: entry_field.delete('0', 'end'))
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = input('Enter host: ')
PORT = 33000#input('Enter port: ')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
