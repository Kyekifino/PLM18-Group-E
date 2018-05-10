from Game import Game
from time import time
from Cards import Deck, Card, CardStack, NotInStackException, ranks
from testFramework import testFramework
from player import Player

# Implementation of  BigTwo as a Game

class BigTwo(Game):

  def __init__(self, players):
      super(BigTwo, self).__init__(players)
      self.playFlag = False
      self.cheatcaller = None
      self.currentNumCards = 0
      self.nextRank = 0
      self.currentPlayer = None
      self.currentRank = None
      self.endTrick = True
      self.passCount = 0
      # Discard pile used to pick up with cheat moves
      self.discard = Deck()
      # Buffer deck to hold cards while cheaters may cheat
      self.bufferDeck = CardStack()
      # Dictionary to define possible actions to take
      self.actions = { "{players}" : self.getPlayers,
                 "{start}" : self.playBigTwo,
                 "{play}" : self.playCards,
                 "{hand}" : self.showHand,
                 "{pass}" : self.callPass,
                 "{help}" : self.getHelp }

  #---------------------------------------------------
  # Defining game actions
  #---------------------------------------------------
  def getHelp(self, player, msglist):
    player.tell("To play cards on your turn, write {play} followed by the cards. ")
    player.tell("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades. ")
    player.tell("If you cannot play any card, type {pass} ")
    player.tell("The first player to play decides the number of cards played that round.")
    player.tell("The next player must play the same number of cards of a higher rank !")
    player.tell("To see your hand, write {hand}. For help, write {help}.")

  def showHand(self, player, msglist):
    player.tell("The cards in your hand:")
    player.tell(player.getHand())

  def playBigTwo(self, player, msglist):
      if len(self.players) < 3 or len(self.players) >= 5:
          player.tell("Need four players to start the game..")
      else:
          self.playing = True

  def getPlayers(self, player, msglist):
      player.tell("Current players: ")
      msg = ""
      for p in self.players:
        msg += (p.name + " --- hand size: " + str(p.getHandSize()) + "\n")
      player.tell(msg[:-1])

  def isValidPlay(self, playedCards, list):
      cardRank = playedCards[1].rank
      for card in playedCards:
          if  card.rank != cardRank:
              raise ValueError
      if self.currentNumCards == 0:
          self.currentNumCards = len(playedCards)
      elif len(playedCards) == self.currentNumCards:
          if cardRank <= self.currentRank:
              raise ValueError
          self.currentRank = cardRank
          return
      else:
          raise ValueError

  def playCards(self, player, msglist):
      if not self.playing:
          player.tell("Wait for the game to start...")
      elif player != self.currentPlayer:
          player.tell("Wait for your turn...")
      elif len(msglist) == 1:
          player.tell("You have to play a card.")
      else:
          cards = msglist[1:]
          playedCards = []
          for card in cards:
              card = Card(str(card[0]),str(card[1:]))
              playedCards.append(card)
          try:
              self.isValidPlay(self, playedCards, self.bufferDeck)
              try:
                  player.playFromHand(playedCards, self.bufferDeck)
                  self.showGUIHand(self.currentPlayer)
                  self.broadcast(player.name + " has played " + str(self.bufferDeck.size()) + " card(s).")
                  self.broadcast("They currently hold " + str(player.hand.size()) + " cards.")
                  self.playFlag = True
              except NotInStackException:
                  player.tell("You can only play cards that are in your hand.")
          except ValueError:
              player.tell("You can only play cards that are in your hand.")



  def callPass(self, player, msglist):
      if not self.playing:
          player.tell("Wait for the game to start...")
      else:
          if self.passCount == 3:
              self.endTrick = True
          else:
              self.passCount += 1
          self.playFlag = True

  #---------------------------------------------------
  # Defining game rules
  #---------------------------------------------------

  def pregameActions(self):
    # Set to players
    self.nextPlayer = iter(self.nextPlayerIterFunc())
    # Make game announcements
    self.broadcast("The Big Two Game is starting!")
    self.broadcast("There are %d players playing!" % len(self.players))
    self.wait(1)
    for p in self.players:
        self.getHelp(p, None)
    self.wait(2)
    self.deck.shuffle()
    while not self.deck.isEmpty():
        self.currentPlayer = next(self.nextPlayer)
        self.currentPlayer.addToHand(self.deck.draw())
    for p in self.players:
        self.showGUIHand(p)
    return True

  def preplayGuards(self):
    self.broadcast("It is %s\'s turn!" % self.currentPlayer.name)
    self.wait(.25)
    self.broadcast("The rank this turn is " + self.currentRank + ".")
    self.wait(1)
    self.showHand(self.currentPlayer, None)
    if self.endTrick == True:
        self.currentNumCards = 0
        self.currentRank = 0
        self.endTrick = False
    return True

  def doPlay(self):
    while not self.playFlag:
        pass
    self.playFlag = False
    return True

  def checkForVictory(self):
    return self.currentPlayer.hand.isEmpty()

  def endGame(self):
    self.wait(1)
    self.broadcast(self.currentPlayer.name + " has emptied their hand, and wins!")
    self.broadcast("Thanks for playing!")
