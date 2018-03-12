# vim: set filetype=python ts=2 sw=2 sts=2 expandtab:
import re, random


def rseed(seed=1):
    random.seed(int(seed))


def shuffle(lst):
    random.shuffle(lst)
    return lst


def about(f):
    print("\n-----| %s |-----------------" % f.__name__)
    if f.__doc__:
        print("# " + re.sub(r'\n[ \t]*', "\n# ", f.__doc__))

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
    def __repr__(self):
        return self.__class__.__name__ + kv(self.__dict__)


class o(Thing):
    def __init__(self, **dic): self.__dict__.update(dic)

    def __getitem__(self, x): return self.__dict__[x]

class BigPayloadException(Exception):
    def __init__(self, message="Payload too large..."):
        self.message = message

# ---------------------------------------
def asLambda(self, txt):
    def methodsOf(self):
        return [s for s in self.__dir__() if s[0] is not "_"]

    for one in methodsOf(self):
        txt = re.sub(one, 'z.%s()' % one, txt)
    txt = "lambda z: " + txt
    # e.g. print("> ",code(self))


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
        for j in shuffle(self._trans):
            if j.gaurd(self):
                #print("now", j.gaurd.__name__)
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

    def maybe(self, s):
        return random.random() < 0.5

    def true(self, s):
        return True

# Create with win condition specs to allow player control
class OuterMachine(Machine):

    def __init__(self, name, numPlayers):
        self.all = {}
        self.name = name
        self.start = None
        self.numPlayers = numPlayers
        self.repeat = 0



# Create with specs to simulate a turn
class InnerMachine(Machine):

    def __init__(self, name, currPlayer, currRank):
        self.all = {}
        self.name = name
        self.start = None
        self.currPlayer = currPlayer
        self.currRank = currRank


# ---------------------------------------
# Creates a new machine with given specifications
def make(machine, specification):
    specification(machine, machine.state, machine.trans)
    return machine