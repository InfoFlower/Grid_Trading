import pandas as pd
import csv

def simple_json_to_csv(data : dict, filepath_out : str):
    """
    Prend un json simple (un seul niveau, Dict[k, v : v==scalar])
    {
    'level': 9345.0,
    'asset_qty': 0.001,
    'leverage': 1.0,
    'tp_pct': 0.01,
    'sl_pct': 0.005
    }
    
    Retourne un csv : key,value

    key,value
    level,9345.0
    asset_qty,0.001
    leverage,1.0
    tp_pct,0.01
    sl_pct,0.005
    """
    with open(filepath_out, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["key", "value"])  # en-têtes
        for k, v in data.items():
            writer.writerow([k, v])