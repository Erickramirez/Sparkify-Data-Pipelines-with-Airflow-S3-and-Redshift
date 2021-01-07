from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 conn_id,
                 table_name,
                 sql_script,
                 truncate_table,
                 *args, **kwargs):
        """
        Load data into Fact table table from the staging tables
        :param conn_id: connection to specific database (in this case redshift)
        :param table_name: table name of the fact table to work on
        :param sql_script:  select script related to the table (check plugins/helpers/sql_queries.py)
        :param truncate_table: boolean to check if it has delete-load functionality (True value) or  append-only (False value)
        """

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.table_name = table_name
        self.sql_script = sql_script
        self.truncate_table = truncate_table

    def execute(self, context):
        """
        Perform load operation into the fact table
        """
        self.log.info(f"LoadFactOperator-->{self.table_name} - Begin")
        # connect to Redshift
        redshift_hook = PostgresHook(postgres_conn_id=self.conn_id)
        self.log.info(f"    connected to {self.conn_id}")
        if self.truncate_table:
            truncate_table_script = f"TRUNCATE TABLE {self.table_name}"
            redshift_hook.run(truncate_table_script)
            self.log.info(f"    Executing: {truncate_table_script}") 
            
        # execute script (insert into)
        insert_sql = f"INSERT INTO {self.table_name} {self.sql_script}"
        self.log.info(f"    Executing: {insert_sql}") 
        redshift_hook.run(insert_sql)
        self.log.info(f"LoadFactOperator-->{self.table_name} - End")
