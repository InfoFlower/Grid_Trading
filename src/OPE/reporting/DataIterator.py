import threading
import time
import queue
import polars as pl

class DataIterator:
    def __init__(self, data, initial_speed=1.0):
        self.data = data
        self.speed = initial_speed
        self.pause_event = threading.Event()
        self.pause_event.set()
        #self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.current_index = 0
        self.data_queue = queue.Queue()

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

    def iterate(self):#update_callback
        while self.current_index < len(self.data):
            self.pause_event.wait()
            with self.lock:
                speed = self.speed
            item = self.data[self.current_index, :]
            print(item)
            #update_callback(item)
            self.data_queue.put(item.to_dict())
            self.current_index += 1
            time.sleep(speed)

if __name__ == "__main__":

    data = pl.read_csv('/Users/alexanderlunel/Documents/Crypto/Grid_Trading_Gabriel/Grid_Trading/src/OPE/reporting/BACKTESTS/1/data.csv')
    di = DataIterator(data)
    di.iterate()