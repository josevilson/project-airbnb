import os
from datetime import datetime
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig, TestBehavior,DbtDag
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping
from airflow import DAG

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
    dag_id="my_cosmos_task_groupx",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args={"retries": 2},
) as dag:
    # Grupo de tarefas para rodar todos os modelos
    run_models_task_group = DbtTaskGroup(
        render_config=RenderConfig(
            test_behavior=TestBehavior.AFTER_ALL,
            #should_detach_multiple_parents_tests=True
            select=["models/marts"]
        ),
        group_id="staging_models",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        
    )

    # Garantir que os testes rodem após os modelos
    run_models_task_group
