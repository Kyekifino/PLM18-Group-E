from Game import Game
from Cards import Deck, Card, NotInStackException
from testFramework import testFramework

# Implementation of Bartok as a Game

class Stress(Game):

  #---------------------------------------------------
  # Initializing attributes, and adding action methods
  #---------------------------------------------------
  def __init__(self, players):
      super(Stress, self).__init__(players)
      self.playFlag = False
      self.currentPlayer = None
      self.skipNextTurn = False
      # Discard pile used to pick up with cheat moves
      self.played = Deck()
      # Dictionary to define possible actions to take
      self.actions = { "{players}" : self.getPlayers,
                 "{start}" : self.playStress,
                 "{play}" : self.playCards,
                 "{hand}" : self.showHand,
                 "{help}" : self.getHelp }

  #---------------------------------------------------
  # Defining game actions
  #---------------------------------------------------
  def getHelp(self, player, msglist):
    player.tell("To play cards on your turn, write {play} followed by the card you want to drop and the card you want to take. ")
    player.tell("For example, write \"{play} H4 S4\" to drop the 4 of Hearts and pick up the 4 of Spades. ")
    player.tell("In order to play a card, the card must you're picking up must be on the table. ")
    player.tell("The goal of the game is to have " + str(48 / len(self.players)) + " piles of four of a kind. ")
    player.tell("To see your hand, write {hand}. For help, write {help}.")

  def showHand(self, player, msglist):
    player.tell("The cards in your hand:")
    player.tell(player.getHand())

  def playStress(self, player, msglist):
      size = len(self.players)
      if size != 2 and size != 3 and size != 4 and size != 6 and size != 12:
          player.tell("The number of players must divide twelve (2, 3, 4, 6, or 12 people")
      else:
          self.playing = True

  def getPlayers(self, player, msglist):
      player.tell("Current players: ")
      msg = ""
      for p in self.players:
        msg += (p.name + "\n")
      player.tell(msg[:-1])

  def playCards(self, player, msglist):
      cards = msglist[1:]
      playedCards = []
      for card in cards:
          card = Card(str(card[0]),str(card[1:]))
          playedCards.append(card)
      if not self.playing:
          player.tell("Wait for the game to start...")
      elif player != self.currentPlayer:
          player.tell("Wait for your turn...")
      elif (len(msglist) != 3):
          player.tell("You must drop one card and pick up one card.")
      elif (playedCards[1] not in self.played.cards):
        player.tell("You must pick up one of the played cards.")
      elif (playedCards[0] not in player.hand.cards):
        player.tell("You must own the card you want to drop.")
      else:
        player.playFromHand(playedCards[0], self.played)
        player.addToHand(self.played.remove(playedCards[1]))
        self.broadcast(str(self.currentPlayer) + "dropped " + str(playedCards[0]) + " and picked up " + str(playedCards[1]))
        self.showGUIHand(self.currentPlayer)
        self.playFlag = True

  #---------------------------------------------------
  # Defining game rules
  #---------------------------------------------------

  def pregameActions(self):
    # Set to players
    self.nextPlayer = iter(self.nextPlayerIterFunc())

    # Make game announcements
    self.broadcast("The Stress Game is starting!")
    self.broadcast("There are %d players playing!" % len(self.players))
    self.wait(1)
    for p in self.players:
        self.getHelp(p, None)
    self.wait(2)
    self.deck.shuffle()
    self.deck.dealCards(self.players, 48 / len(self.players))
    self.played.addToDeck(self.deck.draw())
    self.played.addToDeck(self.deck.draw())
    self.played.addToDeck(self.deck.draw())
    self.played.addToDeck(self.deck.draw())
    for p in self.players:
        p.tell("//{hand}//" + p.getHand())
    return True

  def preplayGuards(self):
    self.broadcast("It is %s\'s turn!\n" % self.currentPlayer.name)
    self.wait(.25)
    self.broadcast("Current cards are " + str(self.played))
    self.wait(1)
    self.showHand(self.currentPlayer, None)
    return True

  def doPlay(self):
    while not self.playFlag:
        pass
    self.playFlag = False
    return True

  def checkForVictory(self):
    types = []
    suits = {
      "H" : 0,
      "S" : 0,
      "D" : 0,
      "C" : 0
    }
    for card in self.currentPlayer.hand.cards:
      if card.rank not in types:
        types.append(card.rank)
      suits[card.suit] += 1
    return suits == 4 and types == 48 / len(self.players)
      

  def endGame(self):
    self.wait(1)
    self.broadcast(str(self.currentPlayer) + " has " + str(48 / len(self.players)) + " piles of four of a kind and wins!")
    self.broadcast("Thanks for playing!")
