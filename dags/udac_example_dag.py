from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator,DataQualityOperator)
from helpers import SqlQueries

AWS_KEY = AwsHook('aws_credentials').get_credentials().access_key
AWS_SECRET = AwsHook('aws_credentials').get_credentials().secret_key
AWS_S3_BUCKET = Variable.get("s3_bucket")
AWS_REGION =  Variable.get("aws_region")
TRUNCATE_TABLE =  Variable.get("truncate_tables")
REDSHIFT_CONN_ID = 'redshift'

def str_to_bool(string):
    """
    :param string: string to evaluate
    :return: boolean True if the parameter is one of the following elements
    """
    return string.lower() in ("yes", "true", "t", "1")

default_args = {
                'owner': 'udacity',
                'start_date': datetime(2020, 1, 12),
                'retries': 3,
                'retry_delay': timedelta(minutes=5),
                'email': ['erickramireztebalan@gmail.com'],
                'email_on_failure': True,
                'email_on_retry': False,  
                'depends_on_past': False,
}

dag = DAG('redshift_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@hourly',
          catchup=False
        )



start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

create_tables_task = PostgresOperator(
    task_id='create_tables',
    dag=dag,
    postgres_conn_id=REDSHIFT_CONN_ID,
    sql='create_tables.sql'
)


stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='staging_events',
    s3_bucket=AWS_S3_BUCKET,
    s3_path='log_data',
    aws_key=AWS_KEY,
    aws_secret=AWS_SECRET,
    region=AWS_REGION,
    copy_json_option= f's3://{AWS_S3_BUCKET}/log_json_path.json'
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='staging_songs',
    s3_bucket=AWS_S3_BUCKET,
    s3_path='song_data',
    aws_key=AWS_KEY,
    aws_secret=AWS_SECRET,
    region=AWS_REGION,
    copy_json_option='auto'
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='songplays',
    sql_script= SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='users',
    sql_script= SqlQueries.user_table_insert,
    truncate_table = str_to_bool (TRUNCATE_TABLE)
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='songs',
    sql_script= SqlQueries.song_table_insert,
    truncate_table = str_to_bool (TRUNCATE_TABLE)
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='artists',
    sql_script= SqlQueries.artist_table_insert,
    truncate_table = str_to_bool (TRUNCATE_TABLE)
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    table_name='time',
    sql_script= SqlQueries.time_table_insert,
    truncate_table = str_to_bool (TRUNCATE_TABLE)
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    provide_context=True,
    conn_id=REDSHIFT_CONN_ID,
    tables=['songplays', 'songs', 'artists', 'users', 'time']
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> \
    create_tables_task \
    >> [stage_events_to_redshift,
        stage_songs_to_redshift]  \
    >> load_songplays_table\
    >> [load_time_dimension_table,
        load_user_dimension_table,
        load_song_dimension_table,
        load_artist_dimension_table] \
    >> run_quality_checks \
    >> end_operator

