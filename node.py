class Node:
    INTERNAL_NODE_CHARACTER = chr(128)

    def __init__(self, character, frequency=0):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None

    def get_frequency(self):
        return self.frequency

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def get_character(self):
        return self.character

    def __lt__(self, other):
        return self.frequency < other.frequency

