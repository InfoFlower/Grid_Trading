import os
import sys
from pendulum import datetime

from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook

from airflow.operators.empty import EmptyOperator

from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

WD = os.getenv('WD')

connection = BaseHook.get_connection("GTBDD_DMBTE")
print(connection.schema)
print(connection.login)
url = f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}:{connection.port}/GTBDD"
print(url)

engine = create_engine(url)

with engine.connect() as conn: 
   print(conn)

@dag(
    start_date=datetime(2025, 8, 30),
    catchup=False,
) 
def DMBTE_INSERT():

    @task(task_id="insert_csv")
    def printer():
        pass

    t18 = EmptyOperator(task_id="t2")
    #insert_csv(file_path, connection.schema, table)


# def insert_csv(file_path, schema, table, sep=","):

    
#     insert_query = """
#     LOAD DATA LOCAL INFILE ?
#     INTO TABLE ?.? FIELDS TERMINATED BY ?;
#     """
#     cursor.execute(insert_query, (file_path, schema, table, sep))

