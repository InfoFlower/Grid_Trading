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
CONNEXION_ID = 'GTBDD_DMBTE'
SCHEMA = 'DMBTE'

def connection_url(conn_id):
    """
    Retourne les informations de la connection conn_id et l'url de connexion à la base de données PostgreSQL
    """

    connection = BaseHook.get_connection(conn_id)
    url = f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}"

    return connection, url

@task
def delete_table(schema, table):


    delete_query = sql.SQL(f"""
        DELETE FROM {schema}.{table}
        """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table)
    )

    connection, url = connection_url(CONNEXION_ID)
    engine = create_engine(url)

    with engine.connect() as conn:
        conn.execute(delete_query.as_string(connection))

@task
def insert_csv(file_path, schema, table, sep=","):

    insert_query = sql.SQL(f"""
        COPY {schema}.{table}
        FROM STDIN WITH CSV HEADER DELIMITER '{sep}'
        NULL 'None'
        """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        sep=sql.Literal(sep)
    )

    # connection = BaseHook.get_connection("GTBDD_DMBTE")
    # url = f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}"
    connection, url = connection_url(CONNEXION_ID)
    engine = create_engine(url)
    
    fake_conn = engine.raw_connection()
    fake_cur = fake_conn.cursor()
    with open(file_path, "r") as f:
        fake_cur.copy_expert(insert_query.as_string(connection), f)
    fake_conn.commit()
    fake_cur.close()
    fake_conn.close()

mapping_file_table = [
    (f"{DATA_DIR}/ORDER.csv", 'e_order'),
    (f"{DATA_DIR}/POSITION.csv", 'e_position'),
    (f"{DATA_DIR}/BACKTEST.csv", 'e_trading_session'),
    (f"{DATA_DIR}/STRATEGY_PARAM.csv", 'e_strategy_param'),
]

@dag(
    start_date=datetime(2025, 8, 30),
    catchup=False,
) 
def DMBTE_INSERT():

    
    
    for file, table in mapping_file_table:
        
        del_task = delete_table.override(task_id=f"delete_{table}")(
            schema=SCHEMA,
            table=table
        )

        ins_task = insert_csv.override(task_id=f"insert_{table}")(
            file_path=file,
            schema=SCHEMA,
            table=table)

        del_task >> ins_task


DMBTE_INSERT()
