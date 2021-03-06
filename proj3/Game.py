from Cards import Deck
from stateMachineFramework import State, InnerMachine, OuterMachine, make
from testFramework import testFramework
from time import sleep

# Inheritance-based implementation based on Group F (https://github.com/ejgillia/plm18_f)
class Game(object):

  #----------------------------------------
  # Constructs a Game object
  #----------------------------------------
  def __init__(self, players):
    self.deck = Deck()
    self.deck.fillDeck()
    self.playing = False
    self.actions = {}
    self.players = players
    self.nextPlayer = iter(self.nextPlayerIterFunc())
    self.currentPlayer = next(self.nextPlayer)

  #----------------------------------------
  # Parses whether a player input is an action.
  #----------------------------------------
  def parseAction(self, player, msg):
    msglist = msg.split()
    if msglist[0] in self.actions:
      self.actions[msglist[0]](player, msglist)
    else:
      self.broadcast(msg, player.name+": ")

  #----------------------------------------
  # Broadcast a message to all the clients
  #----------------------------------------
  def broadcast(self, msg, prefix=""):
    for p in self.players:
        p.tell(prefix + msg)

  #----------------------------------------
  # Show a client their hand from the GUI
  #----------------------------------------
  def showGUIHand(self, player):
    player.tell("//{hand}//" + player.getHand())
    self.wait(.25)

  #----------------------------------------
  # Sleep for given time
  #----------------------------------------
  def wait(self, sleepTime):
      sleep(sleepTime)

  #----------------------------------------
  # Iterator to return next player
  #----------------------------------------
  def nextPlayerIterFunc(self):
      currPlayer = 0
      while True:
        yield self.players[currPlayer]
        if (currPlayer < (len(self.players) - 1)):
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
    def quit(self):
        return True
    def onExit(self):
        return self.model.game.checkForVictory()

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
  def startGuards(self):
    return True

  def preplayGuards(self):
    return True

  def doPlay(self):
    return True

  def postplayGuards(self):
    return True

  def checkForVictory(self):
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
    def quit(self):
        return True
    def onExit(self):
        self.model.game.endGame()
        self.model.game.playing = False

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
  # Use to define what happens before and after
  # the game.
  #-------------------------------------------
  def pregameActions(self):
    print("Game started")
    return True

  def endGame(self):
    print("Game completed")

  #--------------------------------------------
  # Methods to control the state machines.
  # Can be extended but shouldn't be.
  #--------------------------------------------

  def runTurn(self):
     self.currentPlayer = next(self.nextPlayer)
     return make(InnerMachine(self.currentPlayer.name + "\'s turn.",self.currentPlayer,self),self.turnSpec).run()


  def runGame(self):
    self.playing = True
    make(OuterMachine("Welcome to the game!", len(self.players), self),self.gameSpec).run()

"""
#----------------------------------------
# Tests
#----------------------------------------

@testFramework
def tryGame():
    game = Game(None)
    game.runGame()



# ---------------------------------------
if __name__ == "__main__":
    rseed()
    testFramework()
"""
