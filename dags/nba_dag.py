from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import team_stats
import pronosticos

default_args = {
    'owner': 'Javier Prieto',
    'depends_on_past': False,
    'start_date': datetime(2021, 1, 1),
    'end_date': None,
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    dag_id="nba-dag",
    default_args=default_args,
    schedule_interval='0 15 * * *',
    catchup=False
    )


extract_task = PythonOperator(
    task_id="extract",
    python_callable=team_stats.extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id="transform",
    python_callable=team_stats.transform,
    dag=dag
)

load_task = PythonOperator(
    task_id="load",
    python_callable=team_stats.load,
    dag=dag
)

pronosticos_extract_task = PythonOperator(
    task_id ="pronostico_extract",
    python_callable=pronosticos.extract,
    dag=dag
)

pronosticos_transform_task = PythonOperator(
    task_id ="pronostico_transform",
    python_callable=pronosticos.transform,
    dag=dag
)

pronosticos_load_task = PythonOperator(
    task_id ="pronostico_load",
    python_callable=pronosticos.load,
    dag=dag
)


extract_task >> transform_task >> load_task >> pronosticos_extract_task >> pronosticos_transform_task >> pronosticos_load_task

