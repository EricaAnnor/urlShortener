import threading
import time
import os 
from dotenv import load_dotenv

load_dotenv()


class Snowflake:
    epoch = 1654041600000  # Custom epoch

    

    def __init__(self):
        self.machine_id = int(os.getenv("MACHINE_ID",0))
        self.data_center_id = int(os.getenv("DATACENTER_ID",0))
        
        if not 0 <= self.machine_id < (1 << 5) or not 0 <= self.data_center_id < (1 << 5):
            raise Exception("ID out of bounds")
        
       
        self.last_timestamp = -1
        self.lock = threading.Lock()
        self.sequence = 0

    def get_current_time(self):
        return int(time.time() * 1000)

    def next_time(self):
        timestamp = self.get_current_time()
        while timestamp <= self.last_timestamp:
            timestamp = self.get_current_time()
        return timestamp

    def create_sequence(self):
        with self.lock:
            current = self.get_current_time()

            if current < self.last_timestamp:
                raise Exception("Clock moved backwards")

            if current == self.last_timestamp:
                self.sequence += 1
                if self.sequence > (1 << 12) - 1:
                    current = self.next_time()
                    self.sequence = 0
            else:
                self.sequence = 0

            self.last_timestamp = current

            unique_id = ((current - self.epoch) << 22) | \
                        (self.machine_id << 17) | \
                        (self.data_center_id << 12) | \
                        self.sequence

            return unique_id



