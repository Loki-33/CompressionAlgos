import numpy as np 
dictt = {'A': 0.5, 'B':0.25, 'C':0.125, 'D':0.125}
symbols = list(dictt.keys())
probs = list(dictt.values())

class Tree:
    def __init__(self, symbol=None, prob=0, left=None, right=None):
        self.symbol = symbol
        self.prob = prob
        self.left = left
        self.right = right
    
nodes = [Tree(symbol=s, prob=p) for s, p in dictt.items()]

while len(nodes) > 1:
    nodes = sorted(nodes, key=lambda x: x.prob)
    left = nodes.pop(0)
    right = nodes.pop(0)
    merged = Tree(symbol=None, prob=left.prob + right.prob, left=left, right=right)
    nodes.append(merged)

root = nodes[0]

codes = {}
def generate_codes(node, code=''):
    if node.symbol:
        codes[node.symbol] = code
        return
    if node.left:
        generate_codes(node.left, code + '0')
    if node.right:
        generate_codes(node.right, code + '1')

generate_codes(root)
print(codes)

