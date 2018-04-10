from cards import CardStack, NotInStackException

#---------------------------------------------------
# Defining game actions
#---------------------------------------------------
class Player(object):
    """Represents a player object"""
    def __init__(self, name, conn):
        self.name = name
        self.hand = CardStack()
        self.connection = conn

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __repr__(self):
        return self.name

    def getHand(self):
        return str(self.hand.cards)

    def getHandSize(self):
        return len(self.hand.cards)

    def addToHand(self, cards):
        if isinstance(cards, list):
            for card in cards:
                self.hand += card
        else:
            self.hand += cards

    def playFromHand(self, cards, stack):
        if isinstance(cards, list):
            for card in cards:
                if card not in self.hand.cards:
                    raise NotInStackException
            #Will throw NotInStackException if a card in cards is not in self.hand
            for card in cards:
                self.hand -= card
                stack += card
        else:
            self.hand += cards
            stack += cards

    def tell(self, message):
        self.connection.send(bytes(message, "utf8"))
