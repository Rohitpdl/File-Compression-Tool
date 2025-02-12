import heapq
from node import Node

class Huffman:
    def __init__(self):
        self.code_map = {}
        self.root_node = None

    def huffer(self, frequency_map):
        huffman_queue = []
        for char, freq in frequency_map.items():
            heapq.heappush(huffman_queue, (freq, Node(char, freq)))
        heapq.heappush(huffman_queue, (1, Node(Node.INTERNAL_NODE_CHARACTER, 1)))

        while len(huffman_queue) > 1:
            left_freq, left_node = heapq.heappop(huffman_queue)
            right_freq, right_node = heapq.heappop(huffman_queue)
            new_node = Node(Node.INTERNAL_NODE_CHARACTER, left_freq + right_freq)
            new_node.set_left(left_node)
            new_node.set_right(right_node)
            heapq.heappush(huffman_queue, (new_node.get_frequency(), new_node))
        
        self.root_node = huffman_queue[0][1]
        self.encode_characters(self.root_node, "")

    def encode_characters(self, node, code_string):
        if node is None:
            return
        if node.get_character() != Node.INTERNAL_NODE_CHARACTER:
            self.code_map[node.get_character()] = code_string
        self.encode_characters(node.get_left(), code_string + "0")
        self.encode_characters(node.get_right(), code_string + "1")

    def compress_to_file(self, input_file, output_file):
        with open(input_file, 'rb') as infile:
            file_data = infile.read()
            compressed_data = ""
            for byte in file_data:
                compressed_data += self.code_map.get(byte, "")

            padding = 8 - len(compressed_data) % 8
            compressed_data = compressed_data + '0' * padding

            byte_data = bytearray()
            for i in range(0, len(compressed_data), 8):
                byte = compressed_data[i:i+8]
                byte_data.append(int(byte, 2))

            with open(output_file, 'wb') as outfile:
                outfile.write(byte_data)

    def decompress_to_file(self, code_string, decompressed_file_name):
        with open(decompressed_file_name, 'wb') as outputStream:
            traversing_pointer = self.root_node
            for i in range(0, len(code_string)):
                if code_string[i] == '0':
                    traversing_pointer = traversing_pointer.get_left()
                else:
                    traversing_pointer = traversing_pointer.get_right()

                if traversing_pointer.get_character() != Node.INTERNAL_NODE_CHARACTER:
                    if traversing_pointer.get_character() == chr(129):
                        break
                    outputStream.write(bytes([traversing_pointer.get_character()]))
                    traversing_pointer = self.root_node

    def read_header(self, input_stream):
    code_map = {}
    while True:
        # Read a single byte from the stream
        char = input_stream.read(1)
        if not char:
            break  # End of file
        
        # If we reach the separator, skip it
        if char == bytes([131]):  # HEADER_ENTRY_SEPERATOR
            continue
        
        # The current character
        character = char
        
        # Start reading the corresponding code
        code = ''
        while True:
            char = input_stream.read(1)
            if char == bytes([131]):  # HEADER_ENTRY_SEPERATOR
                break  # End of this entry, move to the next one
            code += char.decode('utf-8')  # Decode bytes to string and append

        # Save the character and its code in the map
        code_map[character.decode('utf-8')] = code

    return code_map

