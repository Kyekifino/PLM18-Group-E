# vim: set filetype=python ts=2 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random
from testFramework import testFramework


def rseed(seed=1):
    random.seed(int(seed))


def shuffle(lst):
    random.shuffle(lst)
    return lst

def contains(all, some):
    return all.find(some) != -1

def isa(k, seen=None):
    assert isinstance(k, type), "superclass must be 'object'"
    seen = seen or set()
    if k not in seen:
        seen.add(k)
        yield k
        for sub in k.__subclasses__():
            for x in isa(sub, seen):
                yield x


class Thing(object):
    def __repr__(i):
        return i.__class__.__name__ + kv(i.__dict__)


class o(Thing):
    def __init__(i, **dic): i.__dict__.update(dic)

    def __getitem__(i, x): return i.__dict__[x]

class BigPayloadException(Exception):
    def __init__(i, message="Payload too large..."):
        i.message = message

# ---------------------------------------
def asLambda(i, txt):
    def methodsOf(i):
        return [s for s in i.__dir__() if s[0] is not "_"]

    for one in methodsOf(i):
        txt = re.sub(one, 'z.%s()' % one, txt)
    txt = "lambda z: " + txt
    code = eval(txt)
    # e.g. print("> ",code(i))


# ---------------------------------------
# <BEGIN>
# Base implementation for State class
class State(Thing):
    tag = ""

    def __init__(i, name, m):
        i.name = name
        i._trans = []
        i.model = m

    def trans(i, gaurd, there):
        i._trans += [o(gaurd=gaurd, there=there)]

    def step(i):
        for j in i._trans:
            if j.gaurd(i):
                #print("now", j.gaurd.__name__)
                i.onExit()
                j.there.onEntry()
                return j.there
        return i

    def onEntry(i):
        pass

    def onExit(i):
        pass

    def quit(i):
        return False

#-------------------------------------------------------------------------------
# All code inside this block is just an example for this test implementation!

# Example for outer class to use for turn control
""" class NewTurn(State):
    tag = "*"
    currPlayer = 1

    def onEntry(i):
        name = "Player " + str(i.currPlayer) + " is up!"
        make(InnerMachine(name,i.currPlayer,5),
            spec001).run()

    def onExit(i):
        if i.currPlayer < i.model.numPlayers:
            i.currPlayer += 1
        else:
            i.currPlayer = 1

class Sad(State):
    tag = ":-("

class Exit(State):
    tag = "."

    def quit(i):
        return True

    def onExit(i):
        print("bye bye")
        return i
"""
# ------------------------------------------------------------------------------
class Machine(Thing):
    """Maintains a set of named states.
       Creates new states if its a new name.
       Returns old states if its an old name."""

    def __init__(i, name):
        i.all = {}
        i.name = name
        i.start = None
        i.functions = {}

    def isa(i, x):
        if isinstance(x, State):
            return x
        for k in isa(State):
            if k.tag and contains(x, k.tag):
                return k(x, i)
        return State(x, i)

    def state(i, x):
        i.all[x] = y = i.all[x] if x in i.all else i.isa(x)
        i.start = i.start or y
        return y

    def trans(i, here, gaurd, there):
        i.state(here).trans(gaurd,
                            i.state(there))

    def run(i):
        print(i.name)
        state = i.start
        state.onEntry()
        while True:
            state = state.step()
            if state.quit():
                break
        return state.onExit()

    def maybe(i, s):
        return random.random() < 0.5

    def true(i, s):
        return True

# Create with win condition specs to allow player control
class OuterMachine(Machine):

    def __init__(i, name, numPlayers, game):
        i.all = {}
        i.name = name
        i.start = None
        i.numPlayers = numPlayers
        i.repeat = 0
        i.game = game



# Create with specs to simulate a turn
class InnerMachine(Machine):

    def __init__(i, name, currPlayer, game):
        i.all = {}
        i.name = name
        i.start = None
        i.currPlayer = currPlayer
        i.game = game


# ---------------------------------------
# Creates a new machine with given specifications
def make(machine, specification):
    specification(machine, machine.state, machine.trans)
    return machine


# ------------------------------------------
# Test specs to show how to create machines
# and implement rules
# ------------------------------------------
"""
def spec001(m, s, t):
    def rain(i): return random.random() < 0.3
    def sunny(i): return random.random() < 0.6
    def sick(i): return random.random() < 0.2
    m.rain = rain
    m.sick = sick
    m.sunny = sunny
    grin = s("cheery:-)")
    cry = s("crying:-(")
    t("start", m.true, grin)
    t(grin, m.rain, cry)
    t(grin, m.sick, cry)
    t(grin, m.maybe, "sleeping.")
    t(cry, m.sunny, grin)

def spec002(m, s, t):
    def timeToExit(i):
        try:
            return i.repeat == 10
        except AttributeError:
            i.repeat = 0
    def repeatTurns(i):
        try:
            i.repeat += 1
        except AttributeError:
            i.repeat = 1
        return i.repeat < 10
    m.leave = timeToExit
    m.repeat = repeatTurns
    player = s("player*")
    exit = s("exit.")
    t("start", m.true, player)
    t(player, m.repeat, player)
    t(player, m.leave, exit)

@testFramework
def nestedMachine():
    make(OuterMachine("Welcome to the game!", 5),
         spec002).run()


# ---------------------------------------
if __name__ == "__main__":
    rseed()
    testFramework()
"""
