import threading
import time
import queue
import polars as pl
from config import REPORTING_LOG_PATH

class DataIterator:
    def __init__(self, data_path, every, initial_speed=1):
        """

        STRUCTURE = ['Open time', 'Open', 'High', 'Low', 'Close']
        
        """
        self.every = every
        self.data = pl.read_csv(data_path)
        self.to_datetime()
        self.resample()
        print(self.data.head())

        self.pause_event = threading.Event()
        self.pause_event.set()
        self.speed = initial_speed
        #self.stop_event = threading.Event()
        
        self.lock = threading.Lock()
        self.data_queue = queue.Queue()
        self.current_index = 0
        
    def to_datetime(self):
        """
        """
        self.data = self.data.with_columns(pl.from_epoch(pl.col("Open time"), time_unit="ms"))
        
    def resample(self):
        self.data = self.data.group_by_dynamic(
                    index_column="Open time", 
                    every=self.every, 
                    closed="left"
                    ).agg(
                        Open = pl.col("Open").first(), 
                        High = pl.col("High").max(),
                        Low = pl.col("Low").min(),
                        Close = pl.col("Close").last())

    def set_speed(self, speed):
        with self.lock:
            self.speed = speed

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()

    # def stop(self):
    #     self.stop_event.set()
    #     self.resume()

    def iterate(self):

        while self.current_index < len(self.data):
            self.pause_event.wait()
            with self.lock:
                speed = self.speed
            item = self.data[self.current_index, :]

            item = {key: value.to_list() for key, value in item.to_dict().items()}

            self.data_queue.put(item)
            self.current_index += 1
            time.sleep(speed)

