from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

continuous_dag = DAG(
    dag_id = 'continuous_robot',
    default_args=default_args,
    description='Keep the robot running continuously',
    schedule='@hourly',
    start_date=datetime(2025, 5, 1),
    catchup=False,
)

globals()["continuous_dag"] = continuous_dag

# Task to run robot.py
run_robot = BashOperator(
    task_id='run_robot',
    bash_command='python3 /mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/robot.py',
    dag=continuous_dag,
)