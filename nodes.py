from typing import BinaryIO, Dict, Optional, Union
from dataclasses import dataclass
from collections import Counter

@dataclass
class Node:
    value: Optional[int]
    frequency: int
    left: Optional['Node'] = None
    right: Optional['Node'] = None
    
    def __lt__(self, other: 'Node') -> bool:
        return self.frequency < other.frequency