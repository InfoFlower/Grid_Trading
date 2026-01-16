from airflow.decorators import dag
from airflow.datasets import Dataset
from airflow.operators.dummy import DummyOperator
from dbt_airflow.core.task_group import DbtTaskGroup
from datetime import datetime

from include.dbt_profiles import dbt_project_config, dbt_profile_config, dbt_airflow_config

TAGS = ['dmbtc']

#DATASETS
schedule_dataset = [Dataset("DMBTE")]
outlets_dataset = [Dataset("DMBTC")]

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

    dataset_task = DummyOperator(task_id="dataset")
    dataset_task.outlets=outlets_dataset

    dtg >> dataset_task

DMBTC_LOAD_VIEW()