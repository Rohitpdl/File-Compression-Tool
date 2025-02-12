# Huffman.py
import heapq
from Node import Node
from HuffmanUtility import HuffmanUtility
from FrequencyCounter import FrequencyCounter
import io

class Huffman:
    def __init__(self):
        self.code_map = {}
        self.reverse_code_map = {}
        self.EOF_MARKER = 255

    def build_tree(self, frequency_map):
        heap = []
        for value, freq in frequency_map.items():
            heapq.heappush(heap, (freq, Node(value, freq)))
        
        while len(heap) > 1:
            left = heapq.heappop(heap)[1]
            right = heapq.heappop(heap)[1]
            merged = Node(None, left.frequency + right.frequency)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, (merged.frequency, merged))
        
        return heap[0][1] if heap else None

    def generate_codes(self, node, current_code=""):
        if node is None:
            return
        if node.value is not None:
            self.code_map[node.value] = current_code
            self.reverse_code_map[current_code] = node.value
            return
        self.generate_codes(node.left, current_code + "0")
        self.generate_codes(node.right, current_code + "1")

    def compress(self, input_file, output_file):
        # Read the entire input file
        input_data = input_file.read()
        if not input_data:
            return
        
        # Build frequency map
        frequency_map = {}
        for byte in input_data:
            frequency_map[byte] = frequency_map.get(byte, 0) + 1
        frequency_map[self.EOF_MARKER] = 1
        
        # Build Huffman tree and generate codes
        root = self.build_tree(frequency_map)
        self.generate_codes(root)
        
        # Write header
        HuffmanUtility.write_header(output_file, self.code_map)
        
        # Compress data
        bit_buffer = ""
        for byte in input_data:
            bit_buffer += self.code_map[byte]
            # Write complete bytes
            while len(bit_buffer) >= 8:
                byte_val = int(bit_buffer[:8], 2)
                output_file.write(bytes([byte_val]))
                bit_buffer = bit_buffer[8:]
        
        # Add EOF marker
        bit_buffer += self.code_map[self.EOF_MARKER]
        
        # Pad and write remaining bits
        if bit_buffer:
            while len(bit_buffer) < 8:
                bit_buffer += '0'
            final_byte = int(bit_buffer, 2)
            output_file.write(bytes([final_byte]))

    def decompress(self, input_file, output_file):
        # Read header
        self.reverse_code_map = HuffmanUtility.read_header(input_file)
        
        # Read compressed data
        compressed_data = input_file.read()
        if not compressed_data:
            return
        
        # Convert to bit string
        bit_string = ''
        for byte in compressed_data:
            bit_string += format(byte, '08b')
        
        # Decompress
        current_code = ''
        output_buffer = bytearray()
        
        for bit in bit_string:
            current_code += bit
            if current_code in self.reverse_code_map:
                value = self.reverse_code_map[current_code]
                if value == self.EOF_MARKER:
                    break
                output_buffer.append(value)
                current_code = ''
        
        # Write decompressed data
        output_file.write(output_buffer)