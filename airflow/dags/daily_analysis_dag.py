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

daily_dag = DAG(
    dag_id = 'daily_analysis',
    default_args=default_args,
    description='Run daily analysis scripts and insert data into the database',
    schedule='@daily',
    start_date=datetime(2025, 5, 1),
    catchup=False,
)

# Ensure the DAG is properly registered in the global namespace
globals()["daily_analysis"] = daily_dag

# Task to run technical_analysis.py
run_technical_analysis = BashOperator(
    task_id='run_technical_analysis',
    bash_command='echo "Starting technical analysis" && python3 /mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/technical_analysis.py',
    dag=daily_dag,
)

# Task to run week_analysis.py
run_week_analysis = BashOperator(
    task_id='run_week_analysis',
    bash_command='python3 /mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/week_analysis.py',
    dag=daily_dag,
)

# Task to run years_analysis.py
run_years_analysis = BashOperator(
    task_id='run_years_analysis',
    bash_command='python3 /mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/years_analysis.py',
    dag=daily_dag,
)

# Define task dependencies
run_technical_analysis >> run_week_analysis >> run_years_analysis