# FrequencyCounter.py
class FrequencyCounter:
    def __init__(self):
        self.frequency_map = {}
    
    def read_file(self, file_name):
        with open(file_name, 'rb') as file:
            while (byte := file.read(1)):
                value = int.from_bytes(byte, 'big')
                self.frequency_map[value] = self.frequency_map.get(value, 0) + 1
        
        # Add pseudo-EOF marker (using 255 since we're limited to byte range)
        self.frequency_map[255] = 1  # Using 255 as EOF marker
    
    def get_frequency_map(self):
        return self.frequency_map