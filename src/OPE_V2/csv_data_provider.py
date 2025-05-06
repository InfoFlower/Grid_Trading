import os
import polars as pl
from typing import Dict
from datetime import datetime

from event import Event, EventType, EventDispatcher

class CSVDataProvider:
    """
    Gère la donnée chargée en csv
    Emet un event de type MARKET_DATA à chaque itération grâce à stream_data()
    """
    
    CSV_DATA_STRUCTURE = ['Open time', 'Open', 'Close', 'Low', 'High']
    DATA_STRUCTURE = ['TimeCol','OpenCol','CloseCol','LowCol','HighCol']


    def __init__(self, file_path : str, event_dispatcher : EventDispatcher):

        self.event_dispatcher = event_dispatcher
        
        #Initialisation de la data
        data = pl.read_csv(file_path, truncate_ragged_lines=True)
        self.data = data[self.CSV_DATA_STRUCTURE]
        self.data.columns = self.DATA_STRUCTURE

    def get_initial_data(self) -> Dict[str, float | int]:
        return self.data.row(0, named=True)

    def stream_data(self):
        """
        Emet un évènement de type MARKET_DATA à chaque itération en envoyant la data
        """
        for row in self.data.iter_rows(named=True):
            self.event_dispatcher.dispatch(Event(
                type = EventType.MARKET_DATA,
                data = row,
                timestamp = datetime.now()
            ))
    

    


    
