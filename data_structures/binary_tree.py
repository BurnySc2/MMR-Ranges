from typing import List
import itertools

class Node:
    def __init__(self, value: any, left: "Node" = None, right: "Node" = None):
        self.value: any = value
        self.left: Node = left
        self.right: Node = right

    def __repr__(self):
        return f"Node(value: {self.value}, left: {self.left}, right: {self.right})"

    def add(self, value: any):
        if value < self.value:
            if self.left is not None:
                self.left.add(value)
            else:
                self.left = Node(value)
        else:
            if self.right is not None:
                self.right.add(value)
            else:
                self.right = Node(value)

class Tree:
    def __init__(self):
        self.root: Node = None
        self.size: int = 0

    def add(self, value: int):
        if self.root is not None:
            self.root.add(value)
        else:
            self.root = Node(value)

    def find(self, value):
        """ Finds value and returns position? """

    def pop(self, value):
        """ Finds value and removes it """

    def popmin(self):
        """ Finds the minimum value and returns it """
    def popmax(self):
        """ Finds the maximum value and returns it """

    def load(self, string: str):
        height: List[str] = string.strip().split("\n")
        for i, row in enumerate(height, start=0):
            if i == 0:
                assert len(row) == 1
                self.root = Node(row)
                continue
            for value, j in zip(row, itertools.product("01", repeat=i)):
                # ["00", "01", "10", "11"]
                cur: Node = self.root
                for j2 in j[:-1]: # "0", then "1" etc
                    if j2 == "0":
                        cur = cur.left
                    else:
                        cur = cur.right
                if j[-1] == "0":
                    cur.left = Node(value)
                else:
                    cur.right = Node(value)

    # TODO: Export tree to latex TIKZ

    def in_order_traversal(self, node: Node):
        if node.left:
            self.in_order_traversal(node.left)
        print(f"Value: {node.value}")
        if node.right:
            self.in_order_traversal(node.right)

    def pre_order_traversal(self, node: Node):
        print(f"Value: {node.value}")
        if node.left:
            self.pre_order_traversal(node.left)
        if node.right:
            self.pre_order_traversal(node.right)

    def post_order_traversal(self, node: Node):
        if node.left:
            self.post_order_traversal(node.left)
        if node.right:
            self.post_order_traversal(node.right)
        print(f"Value: {node.value}")

    # TODO balance the tree, turn tree into min or max heap tree

if __name__ == '__main__':
    t = Tree()
    """
        A 
     B     C
    D E   F  G
         H I
    """
    t.root = Node("A", Node(
        "B", Node("D"), Node("E")
    ), Node(
        "C", Node(
            "F", Node("H"), Node("I")
        ), Node("G")
    ))
    print()
    t.in_order_traversal(t.root)
    print()
    t.pre_order_traversal(t.root)
    print()
    t.post_order_traversal(t.root)
    print()

    """
        E 
     A     Q
    S Y   U   T
         E S    I
              O   N
    """
    t.root = Node("E", Node(
        "A", Node("S"), Node("Y")
    ), Node(
        "Q", Node(
            "U", Node("E"), Node("S")
        ), Node("T", None, Node("I", Node("O", Node("N"))))
    ))
    print()
    # t.in_order_traversal(t.root)
    # print()
    t.pre_order_traversal(t.root) # EASYQUESTION
    # print()
    # t.post_order_traversal(t.root)
    print()

    """
        E 
     A     Q
    S Y   U   I
         E  S   O
           T     N
    """
    t.root = Node("E", Node(
        "A", Node("S"), Node("Y")
    ), Node(
        "Q", Node(
            "U", Node("E"), Node("S", Node("T"))
        ), Node("I", None, Node("O", Node("N")))
    ))
    print()
    # t.in_order_traversal(t.root)
    # print()
    t.pre_order_traversal(t.root) # EASYQUESTION
    # print()
    # t.post_order_traversal(t.root)
    print()

    t = Tree()
    t.load("""
A
 C
  FG
    HI  
    """)
    t.in_order_traversal(t.root)
    print()
    t.pre_order_traversal(t.root)
    print()
    t.post_order_traversal(t.root)
