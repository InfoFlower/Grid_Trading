import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')

def csv_file_to_feather(file_in : str, file_out : str):
    """
    file_in : csv
    file_out : feather
    """

    df = pd.read_csv(file_in)
    df.to_feather(file_out)

def csv_file_to_parquet(file_in : str, file_out : str):
    """
    file_in : csv
    file_out : feather
    """

    df = pd.read_csv(file_in)
    df.to_parquet(file_out)

file = f"{WD}data/DATA_RAW_S_ORIGIN/data_raw_BTCUSDT"

file_in = f"{file}.csv"

file_out = f"{file}.feather"
csv_file_to_feather(file_in, file_out)

file_out = f"{file}.parquet"
csv_file_to_parquet(file_in, file_out)