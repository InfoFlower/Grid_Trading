from airflow.decorators import dag
from airflow.datasets import Dataset
from dbt_airflow.core.task_group import DbtTaskGroup
from datetime import datetime

from include.dbt_profiles import dbt_project_config, dbt_profile_config, dbt_airflow_config

TAGS = ['dmbtc']

#DATASETS
schedule_dataset = [Dataset("DMBTE")]
#outlets_dataset = [Dataset("DMBTC")]

@dag(
    dag_id='DMBTC_LOAD_VIEW',
    start_date=datetime(2023, 1, 1),
    schedule=schedule_dataset,
    tags=TAGS,
    catchup=False
)
def DMBTC_LOAD_VIEW():
    
    dtg = DbtTaskGroup(
        group_id = f'load_{TAGS[0]}',
        dbt_profile_config=dbt_profile_config,
        dbt_project_config=dbt_project_config,
        dbt_airflow_config=dbt_airflow_config(TAGS)
    )

    dtg

DMBTC_LOAD_VIEW()