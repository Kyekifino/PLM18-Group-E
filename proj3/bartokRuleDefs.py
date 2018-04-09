from rule import *
from Cards import Deck, Card

class Bartok(Rule):
    def winCondition(self, decks, hands):
        if len(hands[0]) == 0:
            return True
        return False

    def turnIf(self, decks, hands, chosenCard):
        conflictCard = decks[0].lastCard()
        if (conflictCard.suit == chosenCard.suit or conflictCard.rank == chosenCard.rank):
            return True
        else:
            return "You cannot play this card! Play a card from the same suit or rank or draw one card."

    def turnThen(self, decks, hands, chosenCard):
        decks[0].addToDeck(chosenCard)

    def turnElse(self, decks, hands, chosenCard):
        hands[0].addToDeck(decks[1].draw())
