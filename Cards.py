# For use in setting up various card games.
from random import shuffle

class Card(object):
    """Represents a card object."""

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __repr__(self):
        return str(self.suit) + str(self.rank)
    def __str__(self):
        return str(self.suit) + str(self.rank)

class cardStack(object):
    """Represents any such stack of cards."""

    def __init__(self):
        self.cards = []
        self.isVisible = True
    def __str__(self):
        str = ""
        for card in self.cards:
            str = str + card + ", "
        return str[0:-2]
    def __repr__(self):
        str = ""
        for card in self.cards:
            str = str + card + ", "
        return str[0:-2]

class Deck(cardStack):
    """Represents a deck of cards."""

    def isEmpty(self):
        return len(self.cards) == 0

    def shuffle(self):
        shuffle(self.cards)

    def changeVisibility(self):
        if self.isVisible:
            self.isVisible = False
        else :
            self.isVisible = True

    def deal(self, size, Player):
        for num in Range(0,size):
            Player.hand[i] = self.cards.pop()

    def draw(self):
        return self.cards.pop()

    def addToDeck(self):
        self.cards.append(card)

    def fillDeck(self):
        if not self.cards:
            for suit in range(4):
                for rank in range(1, 14):
                    if suit == 0:
                        suit = "H"
                    if suit == 1:
                        suit = "D"
                    if suit == 2:
                        suit = "C"
                    if suit == 3:
                        suit = "S"
                    if rank == 1:
                        rank = "A"
                    if rank == 11:
                        rank = "J"
                    if rank == 12:
                        rank = "Q"
                    if rank == 13:
                        rank = "K"
                    card = Card(suit, rank)
                    self.cards.append(card)

    def resetDeck(self):
        self.cards = []
