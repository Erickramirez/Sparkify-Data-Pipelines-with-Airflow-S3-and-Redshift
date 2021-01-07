from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 conn_id,
                 table_name,
                 s3_bucket,
                 s3_path,
                 aws_key,
                 aws_secret,
                 region,
                 copy_json_option= 'auto',
                 *args, **kwargs):
        """

        :param conn_id:  connection to specific database (in this case redshift)
        :param table_name:  table name of the stage table to work on
        :param s3_bucket: string, name of the s3_bucket (to copy the data)
        :param s3_path: internal path in the s3 bucket to work on
        :param aws_key: Access key ID
        :param aws_secret: Secret access key
        :param region: AWS region
        :param copy_json_option: Add extra copy options
        """

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.table_name = table_name
        self.s3_bucket = s3_bucket
        self.s3_path = s3_path
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.region = region 
        self.copy_json_option = copy_json_option

    def execute(self, context):
        """
        Perform load operation into the stage table
        """
        self.log.info(f"StageToRedshiftOperator-->{self.table_name} - Begin")
        # connect to Redshift
        redshift_hook = PostgresHook(postgres_conn_id=self.conn_id)
        self.log.info(f"    connected to {self.conn_id}")
        
        sql_script = f"""
                    COPY {self.table_name} 
                    FROM 's3://{self.s3_bucket}/{self.s3_path}' 
                    ACCESS_KEY_ID '{self.aws_key}'
                    SECRET_ACCESS_KEY '{self.aws_secret}'
                    REGION '{self.region}'
                    JSON '{self.copy_json_option}'
                    TIMEFORMAT as 'epochmillisecs'
                    TRUNCATECOLUMNS 
                    BLANKSASNULL 
                    EMPTYASNULL
                """            
        # execute script (Copy)

        self.log.info(f"    Executing: {sql_script}") 
        redshift_hook.run(sql_script)
        self.log.info(f"StageToRedshiftOperator-->{self.table_name} - End")





