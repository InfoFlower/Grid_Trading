import pandas as pd
import mariadb
from sqlalchemy import create_engine


def load_csv_to_database(conn, csv_path, table_name):
    # Step 1: Read the CSV file using Polars
    df = pd.read_csv(csv_path)
    df.to_sql(con=conn, name=table_name, if_exists='replace', index=False)


if __name__ == "__main__":
    url="mariadb+mariadbconnector://LeRequeteur:LenulAlex@localhost:3306/DTM_GridTrading"
    conn = create_engine(url, echo=True)
    csv_path = "data/trade_history/position_hist.csv"  # Replace with your actual CSV file path
    table_name = "eq_position_hist"  # Replace with your actual table name
    script_file_path = r"src\database_config\EQ_POSITION_HIST_CREATE_TABLE.sql"
    load_csv_to_database(conn, csv_path, table_name)