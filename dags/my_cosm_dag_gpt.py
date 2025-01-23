import os
from datetime import datetime
from cosmos import (
    DbtTaskGroup,
    ProjectConfig,
    ProfileConfig,
    ExecutionConfig,
    RenderConfig,
    TestBehavior,
    DbtDag,
)
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping
from airflow import DAG
from airflow.utils.task_group import TaskGroup

# Configuração
airflow_home = os.environ["AIRFLOW_HOME"]

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=GoogleCloudServiceAccountFileProfileMapping(
        conn_id="bigquery_default",
        profile_args={
            "dataset": "airbnb_dbt",
            "project": "airbnb-dbt",
        },
    ),
)

project_config = ProjectConfig(f"{airflow_home}/dags/dbt/airbnb")
execution_config = ExecutionConfig(
    dbt_executable_path=f"{airflow_home}/dbt_venv/bin/dbt"
)

# Criação do DAG
with DAG(
    dag_id="my_cosmos_task_group_dag",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args={"retries": 2}
) as dag:
    
    # TaskGroup para organizar os modelos de staging
    with TaskGroup(group_id="staging_models_group") as staging_models_group:
        DbtTaskGroup(
            render_config=RenderConfig(
                test_behavior=TestBehavior.AFTER_EACH,
                should_detach_multiple_parents_tests=True,
                select=["models/staging/stg_airbnb_calendar*"],  # Filtra apenas os modelos de staging
            ),
            group_id="staging_models",
            project_config=project_config,
            profile_config=profile_config,
            execution_config=execution_config,
        )

    # Definir dependências entre os grupos de tarefas
    staging_models_group 
