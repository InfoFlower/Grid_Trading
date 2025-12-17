from airflow.decorators import dag
from dbt_airflow.core.task_group import DbtTaskGroup
from datetime import datetime

from include.dbt_profiles import dbt_project_config, dbt_profile_config, dbt_airflow_config

@dag(
    dag_id='DMBTC_LOAD_VIEW',
    start_date=datetime(2023, 1, 1),
    schedule=None, 
    catchup=False
)
def DMBTC_LOAD_VIEW():
    
    dtg = DbtTaskGroup(
        group_id = 'dmbtc_transform',
        dbt_profile_config=dbt_profile_config,
        dbt_project_config=dbt_project_config,
        dbt_airflow_config=dbt_airflow_config
    )

    dtg

DMBTC_LOAD_VIEW()