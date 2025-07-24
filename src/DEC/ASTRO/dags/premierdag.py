from datetime import datetime

from airflow.decorators import dag

from astro import sql as aql
from astro.sql.table import Table

connection_id = 'postgresql_GTBDD'

@aql.transform
def select(input_table : Table):
    return 'SELECT * FROM {{input_table}}'

@dag(schedule = None,
     start_date = datetime(2024,7,25),
     catchup = False
)
def lol():

    mdr = select(input_table="ORDERI", conn_id = connection_id)

dag = lol()

if __name__ == "__main__":
    conn_path = "include/connections.yml"

    dag.test(
    execution_date = datetime(2026, 7, 24),
    conn_file_path = conn_path
    )