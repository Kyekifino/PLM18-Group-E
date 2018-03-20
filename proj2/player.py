from Cards import CardStack, Deck

unplayedDeck = Deck()
playedDeck = Deck()
playedDeck.changeVisibility()

# stuff outside this class should be in machine, just used it for testing
class Player(object):
    """Represents a player object"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.hand = CardStack()
        self.handSize = 0

    def getHand(self):
        return str(self.hand.cards)

    def draw(self, num = 1):
        if unplayedDeck.isEmpty():
            saveCard = playedDeck.draw()
            while not playedDeck.isEmpty():
                unplayedDeck.addToDeck(playedDeck.draw())
            unplayedDeck.shuffle()
            playedDeck.addToDeck(saveCard)
        for i in range(num):
            self.hand.cards.append(unplayedDeck.draw())
            self.handSize += 1

    def takeAll(self):
        self.handSize += len(playedDeck.cards)
        self.hand.cards += playedDeck.cards
        playedDeck.cards[:] = []

    def playCards(self, cards):
        # cards is an array because there is a possiblity of multiple cards on one play
        # they are sent to buffer because some games have a possiblity of not accepting the cards (Cheat)
        self.handSize -= len(cards)
        self.hand.cards = [x for x in self.hand.cards if x not in cards]
