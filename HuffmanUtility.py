# HuffmanUtility.py
class HuffmanUtility:
    @staticmethod
    def write_header(output_file, code_map):
        # Write number of entries (2 bytes)
        num_entries = len(code_map)
        output_file.write(num_entries.to_bytes(2, 'big'))
        
        # Write each entry's info
        for value, code in code_map.items():
            # Write byte value (1 byte)
            output_file.write(bytes([value]))
            # Write code length (1 byte)
            output_file.write(bytes([len(code)]))
            # Write the code itself
            code_bits = int(code, 2)
            code_bytes = ((len(code) + 7) // 8)
            output_file.write(code_bits.to_bytes(code_bytes, 'big'))

    @staticmethod
    def read_header(input_file):
        code_map = {}
        # Read number of entries
        num_entries = int.from_bytes(input_file.read(2), 'big')
        
        for _ in range(num_entries):
            # Read byte value
            value = input_file.read(1)[0]
            # Read code length
            code_len = input_file.read(1)[0]
            # Read code bytes
            code_bytes = input_file.read((code_len + 7) // 8)
            # Convert to binary string
            code = bin(int.from_bytes(code_bytes, 'big'))[2:].zfill(code_len)
            code_map[code] = value
            
        return code_map