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
            if j.gaurd():
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

    def true(i):
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
