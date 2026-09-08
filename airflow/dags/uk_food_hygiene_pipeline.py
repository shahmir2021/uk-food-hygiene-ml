# ============================================================
# UK FOOD HYGIENE ML
# AIRFLOW DATA PIPELINE
# ============================================================

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

import pendulum


# ============================================================
# CREATE DAG
# ============================================================

with DAG(
    dag_id="uk_food_hygiene_pipeline",

    # Run automatically every Sunday at 3:00 AM
    schedule="0 3 * * 0",

    # Pipeline timezone
    start_date=pendulum.datetime(
        2026,
        9,
        1,
        tz="Europe/London",
    ),

    # Do not run historical missed schedules
    catchup=False,

    # Prevent multiple full pipeline runs overlapping
    max_active_runs=1,

    tags=["uk-food-hygiene"],

) as dag:


    # ========================================================
    # TASK 1
    # AWS S3 TO AWS RDS BRONZE
    # ========================================================

    load_s3_to_rds = BashOperator(
        task_id="load_s3_to_rds",

        bash_command=(
            "python "
            "/opt/airflow/project/src/load_s3_to_rds.py"
        ),
    )


    # ========================================================
    # TASK 2
    # DBT BRONZE TO SILVER
    # ========================================================

    run_dbt_silver = BashOperator(
        task_id="run_dbt_silver",

        bash_command=(
            "dbt run "
            "--project-dir /opt/airflow/project/dbt "
            "--profiles-dir /opt/airflow/project/dbt "
            "--select stg_fsa_establishments_full"
        ),
    )


    # ========================================================
    # TASK 3
    # DBT SILVER TO GOLD ML DATASET
    # ========================================================

    run_dbt_gold = BashOperator(
        task_id="run_dbt_gold",

        bash_command=(
            "dbt run "
            "--project-dir /opt/airflow/project/dbt "
            "--profiles-dir /opt/airflow/project/dbt "
            "--select fct_food_hygiene_full_ml"
        ),
    )


    # ========================================================
    # TASK 4
    # DBT DATA QUALITY TESTS
    # ========================================================

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",

        bash_command=(
            "dbt test "
            "--project-dir /opt/airflow/project/dbt "
            "--profiles-dir /opt/airflow/project/dbt "
            "--select "
            "stg_fsa_establishments_full "
            "fct_food_hygiene_full_ml"
        ),
    )


    # ========================================================
    # TASK ORDER
    # ========================================================

    (
        load_s3_to_rds
        >> run_dbt_silver
        >> run_dbt_gold
        >> run_dbt_tests
    )