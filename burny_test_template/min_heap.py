from typing import List, Optional
import math

class Minheap:
    def __init__(self):
        """ Implementation of binary heap as min-heap """
        self.heap: List[int] = [-1]

    def __repr__(self):
        return_list = []
        multiples_of_two = {2 ** n for n in range(1, 1 + int(math.log(len(self.heap), 2)))}
        for i, value in enumerate(self.heap[1:], start=1):
            if i in multiples_of_two:
                return_list.append("\n")
            return_list.append(value)
            return_list.append(" ")
        return "".join(str(x) for x in return_list)

    def get_parent(self, index: int) -> int:
        return self.heap[index // 2]

    def get_parent_index(self, index: int) -> int:
        return index // 2

    def get_left_child_index(self, index: int) -> int:
        return index * 2

    def get_right_child_index(self, index: int) -> int:
        return index * 2 + 1

    def get_left_child(self, index: int) -> Optional[int]:
        try:
            return self.heap[index * 2]
        except IndexError:
            return None

    def get_right_child(self, index: int) -> Optional[int]:
        try:
            return self.heap[index * 2 + 1]
        except IndexError:
            return None

    def is_empty(self) -> bool:
        return len(self.heap) < 2

    def _swap(self, index1: int, index2: int):
        self.heap[index1], self.heap[index2] = self.heap[index2], self.heap[index1]

    def _move_up(self, number: int, index: int):
        if index <= 1:
            return
        parent = self.get_parent(index)
        if parent > number:
            parent_index = self.get_parent_index(index)
            self._swap(parent_index, index)
            self._move_up(number, parent_index)

    def _move_down(self, number: int, index: int):
        # Swap position with the smallest child
        left = self.get_left_child(index)
        right = self.get_right_child(index)
        # Has no children
        if left is None:
            return
        # Has only left child, so try to swap with that if it is smaller than 'number'
        if right is None:
            if number > left:
                self._swap(self.get_left_child_index(index), index)
            return
        # Has both children, check which child is the smallest, swap if smallest child is smaller than 'number'
        left_index = self.get_left_child_index(index)
        right_index = self.get_right_child_index(index)
        smallest_child_index = left_index if left < right else right_index
        smallest_child = self.heap[smallest_child_index]
        if smallest_child < number:
            self._swap(smallest_child_index, index)
            self._move_down(number, smallest_child_index)

    def insert(self, number: int):
        self.heap.append(number)
        self._move_up(len(self.heap) - 1, len(self.heap) - 1)

    def getMin(self) -> int:
        if len(self.heap) > 0:
            return self.heap[1]
        raise IndexError("getMin from empty heap")

    def deleteMin(self):
        # Swap minimum with last item in list before removing
        if len(self.heap) < 2:
            raise IndexError("deleteMin from empty heap")
        if len(self.heap) < 3:
            self.heap.pop(1)
            return
        last_item_index = len(self.heap) - 1
        self._swap(1, last_item_index)
        # Move the item at index 1 down to its proper position
        self.heap.pop()
        self._move_down(self.heap[1], 1)

    def build(self, my_list: list):
        self.heap: List[int] = [-1]
        for i in my_list:
            self.insert(i)


if __name__ == "__main__":
    p = Minheap()
    build_list = [1, 2, 3, 4, 5, 6, 7]
    p.build(build_list)
    assert len(p.heap) == 8, f"build() function or insert() function not working as expected"
    """ p:
    1
    2 3
    4 5 6 7
    """
    for i in build_list:
        assert not p.is_empty(), f"Min heap should be not empty, but is returned to be empty"
        value = p.getMin()
        assert (
            value == i
        ), f"getMin or deleteMin function not working as expected, received value '{value}' but should have been '{i}', heap:\n{p}"
        p.deleteMin()

    assert p.is_empty(), f"Min heap should be empty, but isn't"
