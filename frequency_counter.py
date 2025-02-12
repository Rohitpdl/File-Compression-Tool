class FrequencyCounter:
    def __init__(self):
        self.frequency_map = {}

    def read_file(self, file_name):
        with open(file_name, 'rb') as f:
            byte = f.read(1)
            while byte:
                byte_val = ord(byte)  # Convert byte to integer value
                if byte_val in self.frequency_map:
                    self.frequency_map[byte_val] += 1
                else:
                    self.frequency_map[byte_val] = 1
                byte = f.read(1)

    def get_frequency_map(self):
        return self.frequency_map
