from random import shuffle

class NotInStackException(Exception):
    pass

#----------------------------------------
# Get suits
#----------------------------------------
def suits():
    return "H D C S".split(" ")

#----------------------------------------
# Get ranks
#----------------------------------------
def ranks():
    return "A 2 3 4 5 6 7 8 9 10 J Q K".split(" ")

#----------------------------------------
# Card class for a single card
#----------------------------------------
class Card(object):
    """Represents a card object."""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __repr__(self):
        return str(self.suit) + str(self.rank)
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

#----------------------------------------
# Stack class for hands
#----------------------------------------
class CardStack(object):
    """Represents any such stack of cards."""
    def __init__(self):
        self.cards = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        for card in self.cards:
            s = s + str(card) + ", "
        return s[0:-2]

    def __iadd__(self,other):
        self.cards.append(other)
        return self

    def __isub__(self,other):
        try:
            self.cards.remove(other)
            return self
        except ValueError:
            raise NotInStackException

    def size(self):
        return len(self.cards)

    def isEmpty(self):
        return len(self.cards) == 0

    def empty(self):
        self.cards = []

#----------------------------------------
# Deck for full deck of cards
#----------------------------------------
class Deck(CardStack):
    """Represents a deck of cards."""

    def shuffle(self):
        shuffle(self.cards)

    def lastCard(self):
        return self.cards[len(self.cards) - 1]

    def draw(self):
        return self.cards.pop()

    def addToDeck(self, c):
        self.cards.append(c)

    def fillDeck(self):
        if not self.cards:
            for suit in suits():
                for rank in ranks():
                    card = Card(suit, rank)
                    self.cards.append(card)

    def dealDeck(self, players):
      currPlayer = 0
      while not self.isEmpty:
          players[currPlayer].addToHand(self.draw())
          if currPlayer < (len(players) - 1):
              currPlayer += 1
          else:
              currPlayer = 0

    def dealCards(self, players, numCards):
      currPlayer = 0
      cardsDealt = 0
      while cardsDealt < (numCards*len(players)) and len(self.cards) > 0:
          players[currPlayer].addToHand(self.draw())
          if currPlayer < (len(players) - 1):
              currPlayer += 1
          else:
              currPlayer = 0
          cardsDealt += 1
