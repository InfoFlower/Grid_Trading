from airflow.decorators import dag
from pendulum import datetime 
from airflow.operators.empty import EmptyOperator


@dag(
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
)
def my_dag():

    t1 = EmptyOperator(task_id="t1")


dag_object = my_dag()

if __name__ == "__main__":
    conn_path = "include/connections.yaml"
    #variables_path = "variables.yaml"
    #my_conf_var = 23

    dag_object.test(
        execution_date=datetime(2023, 1, 29),
        conn_file_path=conn_path,
        #variable_file_path=variables_path,
        #run_conf={"my_conf_var": my_conf_var},
    )