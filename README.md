# PLM18-Group-E
Group E for Programming Languages and Modeling

*Note: These instructions are for the version under the proj3 folder.*

Dickerson Thomas

Egorova Anastasia

Cassandra Keesee

# Cheat

Cheat (also known as B.S., bluff, and I-doubt-it) is a card game where the players aim to get rid of all of their cards. It is a game of deception, with cards being played face-down and players being permitted to lie about the cards they have played. A challenge is usually made by players calling out the name of the game, and the loser of a challenge has to pick up every card played so far.

## Getting Started

Use those instructions if you want to run cheat on your local machine. Note that the game will not start unless a minimum of three players are connected to the server.

### Prerequisites

Have Python installed as python3

### Running

On the "host" computer:

Open a command shell. On Windows type ipconfig, on Mac type ifconfig. Find your LAN ip address, and write it down for the players of the game. While you can play an instance of the game on the host computer, it is not recommended you do so, as output on the server may give you an unfair advantage.
```
python3 .\cheatServer.py
```

On other consoles:

```
python3 .\GameClient.py
Enter host: [Enter the LAN ip address of the host computer]
```
# Bartok

Bartok is a card game where the players aim to get rid of all of their cards. To play every player has to either put a card matching the most recent played card by rank/suit or draw another card and skip a turn. If a 2 is played, the next player has to draw two cards and skip a turn. 

## Getting Started

Use those instructions if you want to run cheat on your local machine. Note that the game will not start unless a minimum of four and a maximum of 4 players are connected to the server.

### Prerequisites

Have Python installed as python3

### Running

On the "host" computer:

Open a command shell. On Windows type ipconfig, on Mac type ifconfig. Find your LAN ip address, and write it down for the players of the game. While you can play an instance of the game on the host computer, it is not recommended you do so, as output on the server may give you an unfair advantage.
```
python3 .\bartokServer.py
```

On other consoles:

```
python3 .\GameClient.py
Enter host: [Enter the LAN ip address of the host computer]
```


#### March 18 Branch
https://github.com/Kyekifino/PLM18-Group-E/tree/march18
