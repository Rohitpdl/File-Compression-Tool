class Node:
    INTERNAL_NODE_CHARACTER = None  # Changed for binary compatibility
    
    def __init__(self, value, frequency=0):
        self.value = value  # Can be byte or pseudo-EOF
        self.frequency = frequency
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.frequency < other.frequency
    
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
    
    def get_value(self):
        return self.value
