# For use in setting up various card games.
from random import shuffle

class Card(object):
    """Represents a card object."""

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

class cardStack(object):
    """Represents any such stack of cards."""

    def __init__(self):
        self.cards = []
        self.isVisible = True

class Deck(cardStack):
    """Represents a deck of cards."""

    def shuffle(self):
        random.shuffle(self.cards)

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
        if not cards:
            for suit in range(4):
                for rank in range(1, 14):
                    card = Card(suit, rank)
                    self.cards.append(card)

    def resetDeck(self):
        self.cards = []

