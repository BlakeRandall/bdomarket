#reference: https://github.com/shrddr/huffman_heap/

from typing import TypeVar, Any, Optional, Union, Dict, List, Tuple, Collection, Iterator
from copy import deepcopy
from io import FileIO, BytesIO
from struct import calcsize, unpack
from bitstring import Bits, BitArray
from marshmallow_dataclass import dataclass
from dataclasses import field

T = TypeVar('T')

def group_by_n_elements(dataset: Collection[Any], groupSize) -> Collection[Tuple[Any, ...]]:
    return (dataset[n:n+groupSize] for n in range(0, len(dataset), groupSize))

class MinHeap(Collection[T]):
    def __init__(self, initialHeap: Optional[List[T]] = None):
        self.heap: List[T] = []

        for obj in initialHeap or []:
            self.push(obj)

    def __str__(self) -> str:
        return self.heap.__str__()

    def __repr__(self) -> str:
        return self.heap.__repr__()

    def __len__(self) -> int:
        return self.heap.__len__()

    def __iter__(self) -> Iterator[T]:
        return self.heap.__iter__()

    def __contains__(self, obj: T) -> bool:
        return self.heap.__contains__(obj)

    def _parent(self, i) -> int:
        return (i - 1) // 2

    def _left_child(self, i) -> int:
        return 2 * i + 1

    def _right_child(self, i) -> int:
        return 2 * i + 2

    def _swap(self, i, j) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def push(self, obj: T) -> None:
        self.heap.append(obj)
        self._swim(len(self) - 1)

    def peek(self) -> T:
        if len(self) > 0:
            return self.heap[0]
        else:
            return None

    def pop(self) -> T:
        if len(self) == 0:
            return None
        elif len(self) == 1:
            return self.heap.pop()
        else:
            obj = self.heap[0]
            self.heap[0] = self.heap.pop()
            self._sink(0)
            return obj

    def _swim(self, i) -> None:
        while i > 0 and self.heap[i] < self.heap[self._parent(i)]:
            self._swap(i, self._parent(i))
            i = self._parent(i)

    def _sink(self, i) -> None:
        while i < len(self):
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)
            if left < len(self) and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < len(self) and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

@dataclass(repr=True, eq=True, order=True)
class HuffmanNode:
    frequency: Optional[Any] = None
    char: Optional[Any] = field(default=None, compare=False)
    left: Optional["HuffmanNode"] = field(default=None, compare=False)
    right: Optional["HuffmanNode"] = field(default=None, compare=False)

    def __add__(self, other: "HuffmanNode"):
        if not isinstance(other, HuffmanNode):
            raise NotImplementedError
        return HuffmanNode(
            frequency=self.frequency + other.frequency,
            left=self,
            right=other
        )

@dataclass
class HuffmanData(object):
    raw_data: Union[bytes, BytesIO, FileIO]
    data: Any = None
    frequency: Dict[Any, Any] = None
    tree: HuffmanNode = None
    table: Dict[Any, Any] = None

    def _read(cls, file_like_obj: Union[FileIO, BytesIO], fmt: Union[str, bytes]) -> Tuple[Any, ...]:
        ret = unpack(fmt, file_like_obj.read(calcsize(fmt)))
        return ret[0] if isinstance(ret, tuple) and len(ret) == 1 else ret

    def __post_init__(self) -> None:
        if isinstance(self.raw_data, bytes):
            self.raw_data = BytesIO(self.raw_data)

        self._working_copy_raw_data = deepcopy(self.raw_data)
        self.frequency = {}
        self.tree = HuffmanNode()
        self.table = {}
        self.data = ''

        length, always0, chars_count = self._read(self._working_copy_raw_data, 'III')
        self.frequency = {
            chr(char): count
            for count, char
            in group_by_n_elements(self._read(self._working_copy_raw_data, 'II' * chars_count), 2)
        }

        heap: MinHeap[HuffmanNode] = MinHeap(initialHeap=[
            HuffmanNode(frequency=frequency, char=char)
            for char, frequency
            in self.frequency.items()
        ])
        while len(heap) > 1:
            heap.push(heap.pop() + heap.pop())
        self.tree = heap.peek()

        tree_stack: List[Tuple[HuffmanNode, str]] = [(self.tree, '')]
        while tree_stack:
            node, code = tree_stack.pop()
            if node.char is not None:
                self.table[code] = node.char
            if node.left is not None:
                tree_stack.append((node.left, code + '0'))
            if node.right is not None:
                tree_stack.append((node.right, code + '1'))

        packed_bits_length, packed_bytes_length, unpacked_bytes_length = self._read(self._working_copy_raw_data, 'III')
        data = self._working_copy_raw_data.read(packed_bytes_length)
        bits = BitArray(bytes=data)[:packed_bits_length]
        bit_pos_start = 0
        bit_pos_stop = 1
        while bit_pos_stop <= len(bits):
            current_bit = bits[bit_pos_start:bit_pos_stop]
            lookup = self.table.get(current_bit.bin)
            if lookup:
                self.data += lookup
                bit_pos_start = bit_pos_stop
            bit_pos_stop += 1