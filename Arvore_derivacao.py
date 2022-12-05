class Arvore_derivacao:
    def __init__(self) -> None:
        self.size = 0
        self.root = None

class Node:
    def __init__(self, label: str) -> None:
        self.label: str = label
        self.father: Node = None
        self.children: list[Node] = []
        self.weight = 0

    def append(self, node):
        self.children.append(node)