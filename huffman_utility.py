class HuffmanUtility:
    def write_header(self, output_stream, code_map):
        for key, value in code_map.items():
            output_stream.write(bytes([key]))
            output_stream.write(chr(130).encode())
            output_stream.write(value.encode())
            output_stream.write(chr(131).encode())
        output_stream.write(chr(132).encode())

    def read_header(self, input_stream):
        code_map = {}
        character = input_stream.read(1)
        while character != chr(132):
            key = ord(character)
            char_code = ""
            while True:
                character = input_stream.read(1)
                if character == chr(131):
                    break
                char_code += character.decode()
            code_map[key] = char_code
            character = input_stream.read(1)
        return code_map
