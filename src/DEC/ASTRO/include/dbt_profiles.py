from cosmos import ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

AIRFLOW_PATH = "/usr/local/airflow"
DBT_PATH = f"{AIRFLOW_PATH}/dbt"
DBT_EXE_PATH = f"{AIRFLOW_PATH}/dbt_venv/bin/dbt"
DBT_PROJECT_PATH = f"{DBT_PATH}/tb_dbt"

_project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH
)

_profile_config = ProfileConfig(
    profile_name="tb_dbt",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="GTBDD",
        profile_args={
            "schema":'dmbtc'
        }
    )
)

_execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXE_PATH
)