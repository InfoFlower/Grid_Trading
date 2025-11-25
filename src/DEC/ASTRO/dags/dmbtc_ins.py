from cosmos import DbtDag, RenderConfig
from airflow.decorators import dag
from pendulum import datetime

from include.dbt_profiles import _project_config, _profile_config, _execution_config

@dag(schedule="@daily", start_date=datetime(2023, 1, 1))
def DMBTC_LOAD_VIEW():
    return DbtDag(
        dag_id = 'DMBTC_LOAD_VIEW',
        project_config=_project_config,
        profile_config=_profile_config,
        execution_config=_execution_config,
        render_config = RenderConfig(
            select="tag:dmbtc"
        )
    )

DMBTC_LOAD_VIEW()