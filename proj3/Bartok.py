from Game import *
from Cards import *
from testFramework import testFramework
from player import *

# Implementation of Bartok as a Game

class Bartok(Game):

  def __init__(self, players):
      super(Bartok, self).__init__(players)
      self.playFlag = False
      self.currentPlayer = None
      self.skipNextTurn = False
      # Discard pile used to pick up with cheat moves
      self.played = Deck()
      # Dictionary to define possible actions to take
      self.actions = { "{players}" : self.getPlayers,
                 "{start}" : self.playBartok,
                 "{play}" : self.playCards,
                 "{hand}" : self.showHand,
                 "{draw}": self.drawCard,
                 "{help}" : self.getHelp }

  #---------------------------------------------------
  # Defining game actions
  #---------------------------------------------------
  def getHelp(self, player, msglist):
    player.tell("To play cards on your turn, write {play} followed by the cards. ")
    player.tell("For example, write \"{play} H4 S4\" to play the 4 of Hearts and the 4 of Spades. ")
    player.tell("In order to play a card, the card must match either the rank or the suite of the displayed card. ")
    player.tell("If you cannot play a card, you must draw. To draw the card, write {draw}. ")
    player.tell("To see your hand, write {hand}. For help, write {help}.")

  def showHand(self, player, msglist):
    player.tell("Your hand is...")
    player.tell(player.getHand())

  def playBartok(self, player, msglist):
      if len(self.players) < 4 or len(self.players) >= 9:
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
      elif (len(msglist) != 2):
          player.tell("You must play one card.")
      else:
          cards = msglist[1:]
          playedCards = []
          for card in cards:
              card = Card(str(card[0]),str(card[1:]))
              playedCards.append(card)
          try:
              if playedCards[0].rank == self.played.lastCard().rank or playedCards.suit == self.played.lastCard().suit:
                  player.playFromHand(playedCards, self.played)
                  self.broadcast(self.currentPlayer + " played " + str(playedCards[0]))
                  if playedCards[0].rank == '2':
                      self.nextPlayer.draw(2)
                      skipNextTurn = True
                  self.playFlag = True
              else:
                  player.tell("You cannot play this card! Play a card from the same suit or rank.")
                  return
              player.playFromHand(playedCards, self.bufferDeck)
              self.broadcast("They currently hold " + str(player.hand.size()) + " cards.")

          except NotInStackException:
              player.tell("You can only play cards that are in your hand.")

  def drawCard(self, player, msglist):
      if not self.playing:
          player.tell("Wait for the game to start...")
      elif player != self.currentPlayer:
          player.tell("Wait for your turn...")
      else:
          if (len(msglist) != 1):
              player.tell("Draw uses no arguments! Type {draw}")
          else:
              if self.deck.isEmpty() and self.played.isEmpty():
                  player.tell("Both played and unplayed decks are empty, skip the turn.")
              else:
                  self.players[self.currentPlayer].draw()
                  self.broadcast(self.currentPlayer + " drew one card!")

  #---------------------------------------------------
  # Defining game rules
  #---------------------------------------------------

  def pregameActions(self, i):
    # Set to players
    self.nextPlayer = iter(self.nextPlayerIterFunc())
    # Make game announcements
    self.broadcast("The Bartok Game is starting!")
    self.broadcast("There are %d players playing!" % len(self.players))
    self.wait(1)
    for p in self.players:
        self.getHelp(p, None)
    self.wait(2)
    self.deck.shuffle()
    while not self.deck.isEmpty():
        for p in self.players:
            for i in range(5):
                p.addToHand(self.deck.draw())
    return True

  def preplayGuards(self, i):
    self.currentRank = next(self.nextRank)
    self.broadcast("It is %s\'s turn!" % self.currentPlayer.name)
    self.wait(.25)
    self.broadcast("The rank this turn is " + self.currentRank + ".")
    self.broadcast("Current card is " + str(self.played.lastCard()))
    self.wait(1)
    self.showHand(self.currentPlayer, None)
    return True

  def doPlay(self, i):
    while not self.playFlag:
        pass
    self.playFlag = False
    return True

  def postplayGuards(self, i):
    if self.played.lastCard().rank == 2:
        self.currentPlayer = self.nextPlayer
    return True


  def checkForVictory(self, i):
    return self.currentPlayer.hand.isEmpty()

  def endGame(self, i):
    self.wait(1)
    self.broadcast(self.currentPlayer.name + " has emptied their hand, and wins!")
    self.broadcast("Thanks for playing!")
