from dbt_airflow.core.config import DbtAirflowConfig, DbtProfileConfig, DbtProjectConfig
from dbt_airflow.operators.execution import ExecutionOperator

AIRFLOW_PATH = "/usr/local/airflow"
DBT_PATH = f"{AIRFLOW_PATH}/dbt"
DBT_PROJECT_PATH = f"{DBT_PATH}/tb_dbt"
DBT_PROFILE_PATH = f"{DBT_PROJECT_PATH}/profiles.yml"
DBT_MANIFEST_PATH = f"{DBT_PROJECT_PATH}/target/manifest.yml"

dbt_project_config = DbtProjectConfig(
    project_path=DBT_PROJECT_PATH,
    manifest_path=DBT_MANIFEST_PATH
)

dbt_profile_config = DbtProfileConfig(
    profiles_path=DBT_PROFILE_PATH,
    target="dev"
)

dbt_airflow_config = DbtAirflowConfig(
    dbt_executable_path=ExecutionOperator.BASH,
    include_tags=['dmbtc']
)