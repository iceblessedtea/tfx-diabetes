from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

PROJECT_DIR = "/usr/local/airflow/tfx_diabetes"

default_args = {
    "owner": "Lingga",
    "start_date": datetime(2024, 1, 1)
}

with DAG(
    "tfx_diabetes_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    run_tfx_pipeline = BashOperator(
        task_id="run_tfx_pipeline",
        bash_command=f"python3 {PROJECT_DIR}/pipeline/pipeline.py"
    )

    run_tfx_pipeline
