from airflow.decorators import dag
from dbt_airflow.core.task_group import DbtTaskGroup
from datetime import datetime

from include.dbt_profiles import dbt_project_config, dbt_profile_config, dbt_airflow_config

TAGS = ['dmbtd']

@dag(
    dag_id='DMBTD_LOAD_VIEW',
    start_date=datetime(2023, 1, 1),
    schedule=None,
    tags=TAGS,
    catchup=False
)
def DMBTD_LOAD_VIEW():
    
    dtg = DbtTaskGroup(
        group_id = f'insert_{TAGS[0]}',
        dbt_profile_config=dbt_profile_config,
        dbt_project_config=dbt_project_config,
        dbt_airflow_config=dbt_airflow_config(TAGS)
    )

    dtg

DMBTD_LOAD_VIEW()