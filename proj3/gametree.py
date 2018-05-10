from Bartok import canPlay

class Node(object):
    def __init__(self, root, depth):
        self.value = root
        self.size = 0
        self.children = []
        self.depth = depth;
        if (self.depth == 1):
            for (card in myDeck):
                if (Bartok.canPlay())
    
    def addChild(self, child):
        self.children.append(Node(child))
        self.size += 1

gameRepr = {
    currCard = 'S3'
    players = [
        {'hand': 5},
        {'hand': 5},
        {'hand': 5}
    ],
    myDeck = ['DA', 'S4', 'S2', 'H10', 'DK'],
    turn = 1
}
