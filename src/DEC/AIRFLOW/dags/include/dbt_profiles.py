from pathlib import Path

from dbt_airflow.core.config import DbtAirflowConfig, DbtProfileConfig, DbtProjectConfig
from dbt_airflow.operators.execution import ExecutionOperator

AIRFLOW_PATH = Path("/opt/airflow")
DBT_PATH = Path(f"{AIRFLOW_PATH}/dbt")
DBT_PROJECT_PATH = Path(f"{DBT_PATH}/tb_dbt")
DBT_PROFILE_PATH = Path(f"{DBT_PROJECT_PATH}/profiles")
DBT_MANIFEST_PATH = Path(f"{DBT_PROJECT_PATH}/target/manifest.json")

dbt_project_config = DbtProjectConfig(
    project_path=DBT_PROJECT_PATH,
    manifest_path=DBT_MANIFEST_PATH
)

dbt_profile_config = DbtProfileConfig(
    profiles_path=DBT_PROFILE_PATH,
    target="dev"
)

def dbt_airflow_config(tags):
    return DbtAirflowConfig(
        execution_operator=ExecutionOperator.BASH,
        include_tags=tags
    )