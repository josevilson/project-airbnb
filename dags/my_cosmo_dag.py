from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig, DbtTaskGroup
import os
from datetime import datetime

from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping


airflow_home = os.environ["AIRFLOW_HOME"]

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=GoogleCloudServiceAccountFileProfileMapping(
        conn_id="bigquery_default",  # Seu Airflow connection ID para o BigQuery
        profile_args={
            "dataset": "airbnb_dbt",  # Nome do dataset no BigQuery
            "project": "airbnb-dbt",  # ID do projeto no Google Cloud
        },
    ),
)

my_cosmos_dag = DbtDag(
    project_config=ProjectConfig(
        f"{airflow_home}/dags/dbt/airbnb"
    ),
    profile_config=profile_config,
    execution_config=ExecutionConfig(
        dbt_executable_path=f"{airflow_home}/dbt_venv/bin/dbt",
    ),
    # normal dag parameters
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    dag_id="my_cosmos_dag",
    default_args={"retries": 2},
)
