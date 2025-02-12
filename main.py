from frequency_counter import FrequencyCounter
from huffman import Huffman

def main():
    working_mode = input("Enter working mode (compress/decompress): ").strip()

    frequency_counter = FrequencyCounter()
    huffman = Huffman()

    if working_mode == "compress":
        input_file = input("Enter the file path to compress (image or text): ").strip()
        output_file = input("Enter the output compressed file path: ").strip()

        frequency_counter.read_file(input_file)
        huffman.huffer(frequency_counter.get_frequency_map())
        huffman.compress_to_file(input_file, output_file)

        print(f"File compressed successfully: {input_file} -> {output_file}")
    
    elif working_mode == "decompress":
        input_file = input("Enter the compressed file path: ").strip()
        output_file = input("Enter the output decompressed file path: ").strip()

        with open(input_file, 'rb') as compressed_file:
            # Read the header first
            huffman.read_header(compressed_file)
            
            # Now reset file pointer to the start for the decompression
            compressed_file.seek(0)
            
            compressed_data = compressed_file.read()
            code_string = "".join([bin(byte)[2:].zfill(8) for byte in compressed_data])

        huffman.decompress_to_file(code_string, output_file)

        print(f"File decompressed successfully: {input_file} -> {output_file}")

if __name__ == "__main__":
    main()
