from cosmos import DbtDag, RenderConfig
from cosmos.airflow.task_group import DbtTaskGroup
#from airflow.sdk import dag
from pendulum import datetime

from include.dbt_profiles import _project_config, _profile_config, _execution_config


def LOAD_EXAMPLE():
    
    return DbtDag(
        dag_id='LOAD_EXAMPLE',
        project_config=_project_config,
        profile_config=_profile_config,
        execution_config=_execution_config,
        render_config = RenderConfig(
            select=["tag:dmbtc"]
        ),
        schedule=None
        , start_date=datetime(2023, 1, 1)
        , catchup=False
    )

test = LOAD_EXAMPLE()

# @dag(schedule=None, start_date=datetime(2023, 1, 1), catchup=False)  
# def TEST_MODEL_DISCOVERY():
#     from cosmos.dbt.graph import DbtGraph
#     from cosmos.dbt.project import create_project
    
#     project = create_project(_project_config)
#     graph = DbtGraph(project=project, profile_config=_profile_config)
    
#     # Force model discovery
#     models = graph.load()
#     print(f"Models found: {len(models)}")
    
#     # Test selection
#     selected = graph.select_nodes(select="tag:example")
#     print(f"Selected models: {selected}")

# TEST_MODEL_DISCOVERY_DAG = TEST_MODEL_DISCOVERY()