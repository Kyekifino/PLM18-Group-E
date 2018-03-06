from Cards import *

unplayedDeck = Deck()
bufferDeck = Deck()
bufferDeck.changeVisibility()
playedDeck = Deck()
playedDeck.changeVisibility()
numberOfPlayers = 8

# stuff outside this class should be in machine, just used it for testing
class Player(object):
    """Represents a player object"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.hand = cardStack()
        self.handSize = 0

    def getHand(self):
        return str(self.hand.cards)

    def draw(self):
        self.hand.cards.append(unplayedDeck.draw())
        self.handSize += 1

    def takeAll(self):
        self.handSize += len(playedDeck.cards)
        self.hand.cards += playedDeck.cards
        playedDeck.cards[:] = []

    def say(self, saying, currPlayer):
        print("Player " + self.name + " says " + saying)
        currPlayer.proof()

    def playCards(self, cards):
        # cards is an array because there is a possiblity of multiple cards on one play
        # they are sent to buffer because some games have a possiblity of not accepting the cards (Cheat)
        bufferDeck.cards += cards
        self.handSize -= len(cards)
        for i in cards:
            self.hand.cards.remove(i)

    def proof(self, rule):
        #check if the cards are of whatever rule
        #idk how rules look like yet.
        if (True) :
            playedDeck.cards += bufferDeck.cards
            bufferDeck.cards[:] = []
            return True;
        else :
            self.hand.cards += bufferDeck.cards
            self.handSize += len(bufferDeck)
            bufferDeck.cards[:] = []
            return False;

    def seeHand(self):
        print(self.hand.cards)

#players = [Player(i) for i in range(numberOfPlayers)]
