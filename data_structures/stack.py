class Item:
    def __init__(self, value: int):
        self.value: int = value
        self.next: Item = None


class Stack:
    def __init__(self):
        """ The stack will be initialized empty. """
        self.top: Item = None

    def push(self, value: int) -> None:
        """
        Pushes an item on top of the stack.
        If the stack was previously empty, self.top will point towards the first item.
        If the stack was not empty, self.top will point towards the newly pushed item and that item will point towards the previously first item.
        """
        if not self.top:
            self.top = Item(value)
        else:
            new_item = Item(value)
            new_item.next = self.top
            self.top = new_item

    def pop(self) -> int:
        """
        Removes the item (value) on top and returns it.
        """
        if self.top:
            return_item: Item = self.top
            self.top = return_item.next
            return return_item.value
        raise IndexError("pop from empty stack")

    def is_empty(self) -> bool:
        """
        Checks if the stack is empty, returns True or False.
        """
        return not self.top

    def size(self) -> int:
        """
        Checks the size of the stack, how many items are there. Returns an integer.
        """
        if not self.top:
            return 0
        item: Item = self.top
        count = 1
        while item.next:
            item = item.next
            count += 1
        return count


if __name__ == "__main__":
    # Tests
    s = Stack()

    s.push(5)
    top = s.top and s.top.value
    assert (
        top == 5
    ), f"Push function does not work as intended, value on top of the stack should be 5 but is actually ({top}) (top value exists: {bool(s.top)})"

    s.push(8)
    first_element = s.top and s.top.value
    second_element = s.top and s.top.next and s.top.next.value
    assert (
        first_element == 8
    ), f"Push function does not work as intended, value on top of the stack should now be 8 (we just put 8 on the stack) but is ({first_element})"
    assert (
        second_element == 5
    ), f"Push function does not work as intended, value on top of the stack should be 8 and second element should now be 5, but second element is ({second_element})"

    value = s.pop()
    assert value == 8, f"Pop function does not work as intended, expected value = 8, received value = ({value})"

    value = s.pop()
    assert value == 5, f"Pop function does not work as intended, expected value = 5, received value = ({value})"

    s.push(10)
    is_empty = s.is_empty()
    assert is_empty is False, f"is_empty() function should return False but gave back ({is_empty})"

    size = s.size()
    assert size == 1, f"size() function should return 1 but gave back ({size})"

    s.pop()
    is_empty = s.is_empty()
    assert is_empty is True, f"is_empty() function should return True but gave back ({is_empty})"

    size = s.size()
    assert size == 0, f"size() function should return 0 but gave back ({size})"
