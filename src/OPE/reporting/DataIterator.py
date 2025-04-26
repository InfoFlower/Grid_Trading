import os
import threading
import time
import queue
import polars as pl
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')

class DataIterator:
    def __init__(self, backtest_path, every, initial_speed=1):
        """

        STRUCTURE = ['Open time', 'Open', 'High', 'Low', 'Close']
        
        """
        # LOAD et TRANSFORM
        self.every = every
        self.data = pl.read_csv(f'{WD}data/DATA_RAW_S_ORIGIN/data_raw_BTCUSDT.csv', truncate_ragged_lines=True)
        self.position_event = pl.read_csv(f'{backtest_path}/Position.csv')
        self.to_datetime()
        self.resample()

        

        self.pause_event = threading.Event()
        self.pause_event.set()
        self.speed = initial_speed
        #self.stop_event = threading.Event()
        
        self.lock = threading.Lock()
        self.data_queue = queue.Queue()
        self.current_index = 0
        
    def to_datetime(self):
        """
        'Open time' en datatime
        """
        self.data = self.data.with_columns(pl.from_epoch(pl.col("Open time"), time_unit="ms"))
        self.position_event = self.position_event.with_columns(pl.from_epoch(pl.col("timestamp"), time_unit="ms"))
        
    def resample(self):
        """
        Resample en fonction de every.
        every est une période sur laquelle on retravaille les bougies de 1 secondes actuellement
        Pour every="1m", on modifie les bougies pour que chacune d'elles représente l'évolution d'une minute.

            Open = Open de la première bougie de la période
            High = Max(High) sur la période
            Low = Min(Low) sur la période
            Close = Close de la dernière bougie de la période

        self.every in ("1m", "15m", "1h", ...)
        """
        self.data = self.data.group_by_dynamic(
                    index_column="Open time", 
                    every=self.every, 
                    closed="left"
                    ).agg(
                        Open = pl.col("Open").first(), 
                        High = pl.col("High").max(),
                        Low = pl.col("Low").min(),
                        Close = pl.col("Close").last())
        
        self.position_event = self.position_event.with_columns(pl.col("timestamp").dt.truncate(self.every))

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

