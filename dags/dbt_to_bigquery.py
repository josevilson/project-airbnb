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
    dag_id="dag_dbt_to_bigquery",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args={"retries": 2}
) as dag:
    
    # TaskGroup para organizar os modelos de staging
    with TaskGroup(group_id="staging_models_group_all") as staging_models_group_all:
        DbtTaskGroup(
            render_config=RenderConfig(
                test_behavior=TestBehavior.AFTER_EACH,
                should_detach_multiple_parents_tests=True,
                select=["models/staging"],  # Filtra apenas os modelos de staging
            ),
            group_id="staging_models_all",
            project_config=project_config,
            profile_config=profile_config,
                operator_args={"install_deps": True },
            execution_config=execution_config,
        )

    with TaskGroup(group_id="int_models_group_all") as int_models_group_all:
        DbtTaskGroup(
            render_config=RenderConfig(
                test_behavior=TestBehavior.AFTER_EACH,
                should_detach_multiple_parents_tests=True,
                select=["models/intermediate"],  # Filtra apenas os modelos de intermeadiate
            ),
            group_id="intermediate_models_all",
            project_config=project_config,
            profile_config=profile_config,
                operator_args={"install_deps": True },
            execution_config=execution_config
        )
    
    with TaskGroup(group_id="mart_models_group_all") as mart_models_group_all:
        DbtTaskGroup(
            render_config=RenderConfig(
                test_behavior=TestBehavior.AFTER_EACH,
                should_detach_multiple_parents_tests=True,
                select=["models/marts"],  # Filtra apenas os modelos de mart
            ),
            group_id="mart_models_all",
            project_config=project_config,
            profile_config=profile_config,
                operator_args={"install_deps": True },
            execution_config=execution_config,
        )
    

    # Definir dependências entre os grupos de tarefas
    staging_models_group_all >> int_models_group_all >> mart_models_group_all
