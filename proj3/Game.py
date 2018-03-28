from Cards import *
from stateMachineFramework import *
from testFramework import testFramework


# Inheritance-based implementation based on Group F (https://github.com/ejgillia/plm18_f)

class Game(object):

  def __init__(self, server, players):
    #---------------------------------------------------
    # Server is the server on which the game is played
    # Players is the list of players in the game
    #---------------------------------------------------

    self.deck = Deck()
    self.deck.fillDeck();

    self.numPlayers = len(players)
    self.players = players
    self.nextPlayer = iter(self.nextPlayerIterFunc())

  #----------------------------------------
  # Iterator to return next player
  #----------------------------------------
  def nextPlayerIterFunc(self):
      currPlayer = 0;
      while True:
        yield self.players[currPlayer]
        if (currPlayer < (self.numPlayers - 1)):
          currPlayer = currPlayer + 1
        else:
          currPlayer = 0


  #----------------------------------------
  # Phases of a turn
  #----------------------------------------
  class StartPhase(State): #Begin the turn
    tag = "!"
  class PreplayPhase(State): #Things that can occur before a play
    tag = "@"
  class PlayPhase(State): #Things that occur to constitute a play
    tag = "#"
  class PostplayPhase(State): #Things that can occur after a play
    tag = "$"
  class EndPhase(State): #End the turn
    tag = "%"
    def quit(i):
        return True
    def onExit(i):
        print("Turn over")
        return i.model.game.checkForVictory(i)

  #--------------------------------------------
  # State machine to abstractly define a turn.
  # m is the machine
  # s is the list of states
  # t is the list of transitions
  #--------------------------------------------
  def turnSpec(self, m, s, t):
      start = s("!")
      preplay = s("@")
      play = s("#")
      postplay = s("$")
      end = s("%")
      t("start", m.true, start)
      t(start, self.startGuards, preplay)
      t(preplay, self.preplayGuards, play)
      t(play, self.doPlay, postplay)
      t(postplay, self.postplayGuards, end)

  #-------------------------------------------
  # Methods to be extended by implementation.
  # Use to define rules of the game.
  #-------------------------------------------
  def startGuards(self, i):
    return True

  def preplayGuards(self, i):
    return True

  def doPlay(self, i):
    return True

  def postplayGuards(self, i):
    return True

  def checkForVictory(self, i):
    return True


  #----------------------------------------
  # Phases of the game
  #----------------------------------------
  class GameStart(State):
    tag = "^"
  class Turn(State):
    tag = "&"
  class GameOver(State):
    tag = "*"
    def quit(i):
        return True
    def onExit(i):
        i.model.game.endGame(i)

  #--------------------------------------------
  # State machine to abstractly define the game.
  # m is the machine
  # s is the list of states
  # t is the list of transitions
  #--------------------------------------------
  def gameSpec(self, m, s, t):
    start = s("^")
    turn = s("&")
    end = s("*")
    t("start", m.true, start)
    t(start, self.pregameActions, turn)
    t(turn, self.runTurn, end)
    t(turn, m.true, turn)
    # TODO Make this work

  #-------------------------------------------
  # Methods to be extended by implementation.
  # Use to define flow of the game.
  #-------------------------------------------
  def pregameActions(self, i):
    print("Game started")
    return True

  def runTurn(self, i):
    p = self.nextPlayer.next()
    return make(InnerMachine(p + "\'s turn.",p,self),self.turnSpec).run()

  def runGame(self):
    make(OuterMachine("Welcome to the game!", self.numPlayers, self),self.gameSpec).run()

  def endGame(self, i):
    print("Game completed")


#----------------------------------------
# Tests
#----------------------------------------
@testFramework
def tryIterator():
    game = Game(None, [1,2,3,4])
    print(game.nextPlayer.next())
    print(game.nextPlayer.next())
    print(game.nextPlayer.next())
    print(game.nextPlayer.next())
    print(game.nextPlayer.next())
    print(game.nextPlayer.next())

@testFramework
def tryGame():
    game = Game(None, ["Tom", "Dick", "Harry"])
    game.runGame()



# ---------------------------------------
if __name__ == "__main__":
    rseed()
    testFramework()
