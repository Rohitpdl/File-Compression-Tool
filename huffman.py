# huffman.py
from typing import BinaryIO, Dict, Optional, Union
import heapq
from dataclasses import dataclass
from collections import Counter
import struct
import io
from nodes import Node

class HuffmanCodec:
    EOF_MARKER = 256  # Using 256 instead of 255 since we need all byte values (0-255)
    CHUNK_SIZE = 8192  # Read file in chunks
    
    def __init__(self):
        self.encoding_map: Dict[int, str] = {}
        self.decoding_map: Dict[str, int] = {}
    
    def _build_tree(self, data: bytes) -> Node:
        # Count frequencies including all bytes in the input
        frequencies = Counter(data)
        frequencies[self.EOF_MARKER] = 1  # Add EOF marker
        
        # Create priority queue
        heap = [Node(value=byte, frequency=freq) for byte, freq in frequencies.items()]
        heapq.heapify(heap)
        
        # Build tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            parent = Node(value=None, frequency=left.frequency + right.frequency, left=left, right=right)
            heapq.heappush(heap, parent)
            
        return heap[0] if heap else Node(value=self.EOF_MARKER, frequency=1)
    
    def _generate_codes(self, node: Node, code: str = "") -> None:
        if node.value is not None:
            self.encoding_map[node.value] = code
            self.decoding_map[code] = node.value
            return
        
        if node.left:
            self._generate_codes(node.left, code + "0")
        if node.right:
            self._generate_codes(node.right, code + "1")
    
    def _write_header(self, output: BinaryIO) -> None:
        # Write number of entries (4 bytes for larger files)
        output.write(struct.pack('>I', len(self.encoding_map)))
        
        # Write data size for verification (8 bytes)
        output.write(struct.pack('>Q', self.original_size))
        
        # Write each entry with fixed-size format
        for value, code in self.encoding_map.items():
            code_len = len(code)
            code_int = int(code, 2)
            # 2 bytes for value (including EOF), 2 bytes for code length
            output.write(struct.pack('>HH', value, code_len))
            # Write code padded to nearest byte
            code_bytes = ((code_len + 7) // 8)
            output.write(code_int.to_bytes(code_bytes, byteorder='big'))
    
    def _read_header(self, input: BinaryIO) -> int:
        # Read number of entries and original file size
        num_entries = struct.unpack('>I', input.read(4))[0]
        original_size = struct.unpack('>Q', input.read(8))[0]
        
        # Read each entry
        for _ in range(num_entries):
            value, code_len = struct.unpack('>HH', input.read(4))
            code_bytes = input.read((code_len + 7) // 8)
            code = bin(int.from_bytes(code_bytes, byteorder='big'))[2:].zfill(code_len)
            
            self.decoding_map[code] = value
            self.encoding_map[value] = code
            
        return original_size
    
    def compress(self, input: BinaryIO, output: BinaryIO) -> None:
        # Read input data in chunks and store in memory buffer
        buffer = io.BytesIO()
        while chunk := input.read(self.CHUNK_SIZE):
            buffer.write(chunk)
        
        # Get the complete data and its size
        data = buffer.getvalue()
        self.original_size = len(data)
        
        if not data:
            return
        
        # Build Huffman tree and generate codes
        root = self._build_tree(data)
        self._generate_codes(root)
        
        # Write header
        self._write_header(output)
        
        # Write compressed data
        bit_buffer = ""
        bytes_written = 0
        
        for byte in data:
            bit_buffer += self.encoding_map[byte]
            # Write complete bytes
            while len(bit_buffer) >= 8:
                output.write(bytes([int(bit_buffer[:8], 2)]))
                bytes_written += 1
                bit_buffer = bit_buffer[8:]
        
        # Add EOF marker and padding
        bit_buffer += self.encoding_map[self.EOF_MARKER]
        while bit_buffer:
            if len(bit_buffer) < 8:
                bit_buffer += '0' * (8 - len(bit_buffer))
            output.write(bytes([int(bit_buffer[:8], 2)]))
            bytes_written += 1
            bit_buffer = bit_buffer[8:]
    
    def decompress(self, input: BinaryIO, output: BinaryIO) -> None:
        # Read and parse header
        original_size = self._read_header(input)
        bytes_written = 0
        
        # Read compressed data
        current_code = ""
        output_buffer = bytearray()
        
        while bytes_written < original_size:
            byte = input.read(1)
            if not byte:
                break
                
            # Convert byte to bits
            bits = format(byte[0], '08b')
            for bit in bits:
                current_code += bit
                if current_code in self.decoding_map:
                    value = self.decoding_map[current_code]
                    if value == self.EOF_MARKER:
                        break
                    output_buffer.append(value)
                    bytes_written += 1
                    current_code = ""
                    
                    # Write in chunks to save memory
                    if len(output_buffer) >= self.CHUNK_SIZE:
                        output.write(output_buffer)
                        output_buffer.clear()
        
        # Write any remaining data
        if output_buffer:
            output.write(output_buffer)