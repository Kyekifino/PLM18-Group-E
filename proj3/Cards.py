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
        return self.__repr__()
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    def isFace(self):
        return rank in ["A", "J", "Q", "K"]

class cardStack(object):
    """Represents any such stack of cards."""

    def __init__(self):
        self.cards = []
        self.isVisible = True
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        s = ""
        for card in self.cards:
            s = s + str(card) + ", "
        return s[0:-2]
    def size(self):
        return len(self.cards)

class Deck(cardStack):
    """Represents a deck of cards."""

    def isEmpty(self):
        return len(self.cards) == 0

    def shuffle(self):
        shuffle(self.cards)

    def lastCard(self):
        return self.cards[len(self.cards) - 1]

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

    def addToDeck(self, c):
        self.cards.append(c)

    def fillDeck(self):
        suits = "H D C S".split(" ")
        ranks = "A 2 3 4 5 6 7 8 9 10 J Q K".split(" ")
        if not self.cards:
            for suit in suits:
                for rank in ranks:
                    card = Card(suit, rank)
                    self.cards.append(card)

    def resetDeck(self):
        self.cards = []
