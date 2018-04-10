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
            yield from isa(sub, seen)


class Thing(object):
    def __repr__(self):
        return self.__class__.__name__


class o(Thing):
    def __init__(self, **dic): self.__dict__.update(dic)

    def __getitem__(self, x): return self.__dict__[x]

# ---------------------------------------
def asLambda(self, txt):
    def methodsOf(self):
        return [s for s in self.__dir__() if s[0] is not "_"]

    for one in methodsOf(self):
        txt = re.sub(one, 'z.%s()' % one, txt)
    txt = "lambda z: " + txt

# ---------------------------------------
# <BEGIN>
# Base implementation for State class
class State(Thing):
    tag = ""

    def __init__(self, name, m):
        self.name = name
        self._trans = []
        self.model = m

    def trans(self, gaurd, there):
        self._trans += [o(gaurd=gaurd, there=there)]

    def step(self):
        for j in self._trans:
            if j.gaurd():
                self.onExit()
                j.there.onEntry()
                return j.there
        return self

    def onEntry(self):
        pass

    def onExit(self):
        pass

    def quit(self):
        return False

# ------------------------------------------------------------------------------
class Machine(Thing):
    """Maintains a set of named states.
       Creates new states if its a new name.
       Returns old states if its an old name."""

    def __init__(self, name):
        self.all = {}
        self.name = name
        self.start = None
        self.functions = {}

    def isa(self, x):
        if isinstance(x, State):
            return x
        for k in isa(State):
            if k.tag and contains(x, k.tag):
                return k(x, self)
        return State(x, self)

    def state(self, x):
        self.all[x] = y = self.all[x] if x in self.all else self.isa(x)
        self.start = self.start or y
        return y

    def trans(self, here, gaurd, there):
        self.state(here).trans(gaurd,
                            self.state(there))

    def run(self):
        print(self.name)
        state = self.start
        state.onEntry()
        while True:
            state = state.step()
            if state.quit():
                break
        return state.onExit()

    def true(self):
        return True

# Create with win condition specs to allow player control
class OuterMachine(Machine):

    def __init__(self, name, numPlayers, game):
        self.all = {}
        self.name = name
        self.start = None
        self.numPlayers = numPlayers
        self.repeat = 0
        self.game = game



# Create with specs to simulate a turn
class InnerMachine(Machine):

    def __init__(self, name, currPlayer, game):
        self.all = {}
        self.name = name
        self.start = None
        self.currPlayer = currPlayer
        self.game = game


# ---------------------------------------
# Creates a new machine with given specifications
def make(machine, specification):
    specification(machine, machine.state, machine.trans)
    return machine
