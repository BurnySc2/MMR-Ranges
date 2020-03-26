class Node:
    def __init__(self, value: int, next_node: "Node" = None):
        self.value: int = value
        self.next: Node = next_node

    def __repr__(self):
        return f"Node(value: {self.value}, next: {self.next})"


class Queue:
    def __init__(self):
        self.front: Node = None
        self.tail: Node = None
        self.size: int = 0

    def enqueue(self, value: int):
        new_node = Node(value)

        if self.front is None:
            self.front = new_node
        elif self.tail is None:
            self.tail = new_node
            self.front.next = self.tail
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.size += 1

    def dequeue(self):
        if self.front is None:
            raise IndexError("queue is empty")

        return_value = None
        if self.front is not None:
            return_value: int = self.front.value
            self.front = self.front.next

        if self.size == 2:
            self.tail = None

        self.size -= 1
        return return_value


if __name__ == "__main__":
    q = Queue()
    assert q.front is None
    assert q.tail is None

    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)

    print(q.front) # Node(value: 1, next: Node(value: 2, next: Node(value: 3, next: None)))
    print(q.tail) # Node(value: 3, next: None)

    a = q.dequeue()
    assert a == 1

    b = q.dequeue()
    assert b == 2
    assert q.front is not None
    assert q.tail is None

    c = q.dequeue()
    assert c == 3
    assert q.size == 0
    assert q.front is None
    assert q.tail is None
