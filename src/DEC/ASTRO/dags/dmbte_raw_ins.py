import os
import sys


from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
#from airflow.operators.postgresql import PostgresOperator
from airflow.operators.python import PythonOperator

from pendulum import datetime
from sqlalchemy import create_engine
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

WD = os.getenv('WD')

DATA_DIR = Variable.get('DATA_DIR')



@task
def insert_csv(file_path, schema, table, sep=","):

    # insert_query = """
    #     COPY ?.?
    #     FROM ?
    #     DELIMITER ?
    #     CSV HEADER;
    #     """

    # with engine.connect() as conn:
    #     conn.execute(insert_query, (file_path, schema, table, sep))

    insert_query = sql.SQL(f"""
        COPY {schema}.{table}
        FROM STDIN WITH CSV HEADER DELIMITER '{sep}'
        """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        sep=sql.Literal(sep)
    )

    connection = BaseHook.get_connection("GTBDD_DMBTE")
    url = f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}"
    engine = create_engine(url)
    
    fake_conn = engine.raw_connection()
    fake_cur = fake_conn.cursor()
    with open(file_path, "r") as f:
        fake_cur.copy_expert(insert_query.as_string(connection), f)

mapping_file_table = [
    (f"{DATA_DIR}/ORDER.csv", 'e_order'),
    (f"{DATA_DIR}/POSITION.csv", 'e_position'),
    (f"{DATA_DIR}/BACKTEST.csv", 'e_trading_session'),
]

@dag(
    start_date=datetime(2025, 8, 30),
    catchup=False,
) 
def DMBTE_INSERT():

    schema = 'DMBTE'
    
    for file, table in mapping_file_table:
        print("AAAAAAAAAAAAAAAAAAAAZ")
        print(file, table)
        insert_csv.override(task_id=f"insert_{table}")(
            file_path=file,
            schema=schema,
            table=table)


DMBTE_INSERT()
