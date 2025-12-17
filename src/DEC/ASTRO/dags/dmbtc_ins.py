from airflow import DAG
from cosmos import DbtDag, RenderConfig
from datetime import datetime

from include.dbt_profiles import _project_config, _profile_config, _execution_config


def DMBTC_LOAD_VIEW():
    return DbtDag(
        dag_id='DMBTC_LOAD_VIEW',
        project_config=_project_config,
        profile_config=_profile_config,
        execution_config=_execution_config,
        render_config = RenderConfig(
            select=["tag:dmbtc"]
        ),
        operator_args={
            "install_deps": True,
        },
        schedule="@daily",
        start_date=datetime(2023, 1, 1)
    )

DMBTC_LOAD_VIEW()