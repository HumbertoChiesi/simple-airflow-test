from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import pandas as pd

import os

def download_data():
    data = pd.read_csv('/tmp/data.csv', header=None)

    now = pd.Timestamp.now()
    year = now.year
    month = now.month
    day = now.day

    data_dir = f'/airflow/data/data/{year}/{month}/{day}'
    os.makedirs(data_dir, exist_ok=True)

    cleaned_data.to_csv(f'{data_dir}/data.csv', index=False)

dag = DAG(
    'exchange_rate_etl',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 22 * * *',
    catchup=False
)

download_task = BashOperator(
    task_id='download_file',
    bash_command='curl -o data.csv https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?format=csvdata',
    cwd='/tmp',
    dag=dag,
)

save_data_task = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    dag=dag,
)

send_email_task = EmailOperator(
    task_id='send_email',
    to='your_email@gmail.com',
    subject='Data Download - Successful',
    html_content='The data has been successfully downloaded.',
    dag=dag,
)

download_task >> save_data_task >> send_email_task
