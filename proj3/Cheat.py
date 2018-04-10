from Game import *
from Cards import *
from testFramework import testFramework
from player import *

# Implementation of Cheat as a Game

class Cheat(Game):

  def __init__(self, players):
      super(Cheat, self).__init__(players)
      self.playFlag = False
      self.cheatcaller = None
      self.nextRank = iter(self.nextRankIterFunc())
      self.currentPlayer = None
      self.currentRank = None
      # Discard pile used to pick up with cheat moves
      self.discard = Deck()
      # Buffer deck to hold cards while cheaters may cheat
      self.bufferDeck = cardStack()
      # Dictionary to define possible actions to take
      self.actions = { "{players}" : self.getPlayers,
                 "{start}" : self.playCheat,
                 "{play}" : self.playCards,
                 "{hand}" : self.showHand,
                 "{cheat}" : self.callCheat,
                 "{help}" : self.getHelp }

  #---------------------------------------------------
  # Current rank iterator
  #---------------------------------------------------
  def nextRankIterFunc(self):
    currRank = 0;
    while True:
      yield ranks()[currRank]
      if (currRank < (len(ranks()) - 1)):
        currRank += 1
      else:
        currRank = 0

  #---------------------------------------------------
  # Defining game actions
  #---------------------------------------------------
  def getHelp(self, player, msglist):
    player.tell("To play cards on your turn, write {play} followed by the cards. ")
    player.tell("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades. ")
    player.tell("If you think a player played cards that aren't of the current rank, announce {cheat}. ")
    player.tell("If they were lying, they have to pick up all the played cards... but if the weren't... you do! ")
    player.tell("To see your hand, write {hand}. For help, write {help}.")

  def showHand(self, player, msglist):
    player.tell("//{hand}//" + player.getHand())

  def playCheat(self, player, msglist):
      if len(self.players) < 3:
          player.tell("Not enough players to start the game...")
      else:
          self.playing = True

  def getPlayers(self, player, msglist):
      player.tell("Current players: ")
      msg = ""
      for p in self.players:
        msg += (p.name + " --- hand size: " + str(p.getHandSize()) + "\n")
      player.tell(msg[:-1])

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
              player.playFromHand(playedCards, self.bufferDeck)
              self.broadcast(player.name + " has played " + str(self.bufferDeck.size()) + " card(s).")
              self.broadcast("They currently hold " + str(player.hand.size()) + " cards.")
              self.playFlag = True
          except NotInStackException:
              player.tell("You can only play cards that are in your hand.")


  def callCheat(self, player, msglist):
      if not self.playing:
          player.tell("Wait for the game to start...")
      elif player == self.currentPlayer:
          player.tell("You can\'t call Cheat on yourself...")
      else:
          self.cheatCaller = player

  #---------------------------------------------------
  # Defining game rules
  #---------------------------------------------------

  def pregameActions(self):
    # Set to players
    self.nextPlayer = iter(self.nextPlayerIterFunc())
    # Make game announcements
    self.broadcast("The Cheat Game is starting!")
    self.broadcast("There are %d players playing!" % len(self.players))
    self.wait(1)
    for p in self.players:
        self.getHelp(p, None)
    self.wait(2)
    self.deck.shuffle()
    while not self.deck.isEmpty():
        self.currentPlayer = next(self.nextPlayer)
        self.currentPlayer.addToHand(self.deck.draw())
    return True

  def preplayGuards(self):
    self.currentRank = next(self.nextRank)
    self.broadcast("It is %s\'s turn!" % self.currentPlayer.name)
    self.wait(.25)
    self.broadcast("The rank this turn is " + self.currentRank + ".")
    self.wait(1)
    self.showHand(self.currentPlayer, None)
    return True

  def doPlay(self):
    while not self.playFlag:
        pass
    self.playFlag = False
    return True

  def postplayGuards(self):
    cheating = False
    for c in self.bufferDeck.cards:
      self.discard += c
      if c.rank != self.currentRank:
        cheating = True
    self.bufferDeck.empty()
    self.wait(1)
    self.broadcast("You have 10 seconds to announce {cheat}.")
    self.cheatCaller = None
    t_end = time() + 10
    while self.cheatCaller is None and time() < t_end:
        pass
    if self.cheatCaller is not None:
        self.broadcast(self.cheatCaller.name + " has called Cheat!")
        self.wait(2)
        if cheating:
            self.broadcast("%s was cheating, and has to pick up the stack! " % self.currentPlayer.name)
            while not self.discard.isEmpty():
                self.currentPlayer.addToHand(self.discard.draw())
        else:
            self.broadcast("%s wasn't cheating... %s has to pick up the stack..." % (self.currentPlayer.name, self.cheatCaller.name))
            while not self.discard.isEmpty():
                self.cheatCaller.addToHand(self.discard.draw())
    else:
        self.broadcast("Time's up!")
    if not self.discard.isEmpty():
        self.wait(.5)
        self.broadcast("The discard pile has %d cards in it." % self.discard.size())
    return True

  def checkForVictory(self):
    return self.currentPlayer.hand.isEmpty()

  def endGame(self):
    self.wait(1)
    self.broadcast(self.currentPlayer.name + " has emptied their hand, and wins!")
    self.broadcast("Thanks for playing!")
