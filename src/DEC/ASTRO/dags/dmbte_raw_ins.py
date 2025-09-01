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

url = f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}"
print(url)
#engine = create_engine(url)

#print(engine.connect())

@dag(
    start_date=datetime(2025, 8, 30),
    catchup=False,
) 
def DMBTE_INSERT():

    @task
    def printer():
        pass

    t18 = EmptyOperator(task_id="t2")
    printer()

DMBTE_INSERT()

def insert_csv(file_path, sep=","):

    
    insert_query = """
    LOAD DATA LOCAL INFILE ?
    INTO TABLE ?.? FIELDS TERMINATED BY ?;
    """

