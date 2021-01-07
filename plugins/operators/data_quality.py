from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 conn_id,
                 tables=[],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.tables = tables

    def execute(self, context):
        self.log.info(f"LoadDimensionOperator--> Begin")
        
        redshift_hook = PostgresHook(postgres_conn_id = self.conn_id)
        self.log.info(f"    connected to {self.conn_id}")

        for table in self.tables:
            self.log.info(f'    Data quality check on on {table}')

            records = redshift.get_records(f"SELECT COUNT(*) FROM {table}")
            if len(records) < 1 or len(records[0]) < 1:
                raise ValueError(f"    Data quality check failed. {table}, there isn't any result")
            num_records = records[0][0]
            if num_records < 1:
                raise ValueError(f"    Data quality check failed. there are 0 rows in {table}")
            logging.info(f"    Data quality check on table {table} passed with {num_records} records")
            
        self.log.info(f"LoadDimensionOperator--> End")
        