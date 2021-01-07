# Sparkify: Data Pipelines with Airflow, S3 and Redshift
This project has to output a Dataware house solution and create high-grade data pipelines that are dynamic and built from reusable tasks, monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top of the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

Sparkify is a fictional popular digital media service created by Udacity, similar to Spotify or 
Pandora; many users use their services every day.

### Data pipeline
It has the following structure:
 ![dag](/images/dag.png)
- begin execution
- Load stage tables(`Stage_events` and `Stage_songs`) :  Load the data from S3 buckets into staging tables in the Redshift Cluster.
- Load data into fact table (`Load_songplays_fact_table`): Transform and load data from stage tables into fact table: `songplays`
- Load data into dimension tables: Transform and load data into  dimension tables from the staging tables, and `time` table is loaded from `songplays` table.
- Execute check operations (`Run_data_quality_checks`): Perform count operations to validate that the data has been inserted.
in the file `etl.py`.
   
### Set up for Redshift cluster
1. Create an IAM Role
    - Go to [Amazon IAM console](https://console.aws.amazon.com/iam)
    - Choose Create role.
    - In the AWS Service group, choose `Redshift`.
    - Under Select your use case, choose `Redshift - Customizable`, and then Next: Permissions.
    - On the Attach permissions policies page, choose `AmazonS3ReadOnlyAccess`
2. Create Security Group
    - Go to [Amazon EC2 console ](https://console.aws.amazon.com/ec2) and under Network and 
    Security in the left navigation pane, select Security Groups.
    - Click on `Create Security Group`
    - Enter a Security group name and description.
    - Select the `Inbound` tab under `Security group rules.`
    - Click on Add Rule and enter the following values:
        - Type: Custom TCP Rule.
        - Protocol: TCP.
        - Port Range: 5439. The default port for Amazon Redshift is 5439, but your port might be different. See note on determining your firewall rules on the earlier "AWS Setup Instructions" page in this lesson.
        - Source: select Custom IP, then type 0.0.0.0/0. Note: or select a specific location to share it.
3. Launch a Redshift Cluster
    - Sign in to the AWS Management Console and open the [Amazon Redshift console](https://console.aws.amazon.com/redshift/)
    - On the Amazon Redshift Dashboard, choose `Launch cluster`.
    - On the Cluster details page, configure `Cluster identifier`, `Database name`, 
    `Database port`, `Master user name` and `Master user password` 
    - select Node time
    - On the Additional Configuration page, enter the following values:
        - Available IAM roles: IAM Role just created
        - VPC security groups: security group created previously
    - choose Launch cluster.

### Airflow configuration
1. Start Airflow, run the `/opt/airflow/start.sh` command to start the Airflow webserver and wait for the Airflow web server to be ready.
2. Go to the Airflow UI
3. Configure Connections (Click on the **Admin** tab and select **Connections**)
    1. Configure AWS Connection
        - **Conn Id:** Enter `aws_credentials`.
        - **Conn Type:** Enter `Amazon Web Services`.
        - **Login:** Enter your **Access key ID** from the IAM User credentials.
        - **Password:** Enter your **Secret access key** from the IAM User credentials.
    2. Configure redshift connection
        - **Conn Id:** Enter `redshift`.
        - **Conn Type:** Enter `Postgres`.
        - **Host:** Enter the endpoint of your Redshift cluster, excluding the port at the end. 
        - **Schema:** Enter `dev`. This is the Redshift database you want to connect to.
        - **Login:** Enter `awsuser`.
        - **Password:** Enter the password you created when launching your Redshift cluster.
        - **Port:** Enter 5439.
4. Configure Variables (Click on the **Admin** tab and select **Variables**)
    1. S3 bucket
        - **Key:** Enter `s3_bucket`.
        - **Val:** Enter `udacity-dend`.
    2. AWS region
        - **Key:** Enter `aws_region`.
        - **Val:** Enter `us-west-2`.
    3. Truncate tables
        - **Key:** Enter `truncate_tables`.
        - **Val:** Enter `True` if you expect that the dimension task will have delete-load functionality or enter `False` if you expect to perform append-only functionality.
        
    
   
 
 ### Prerequisites
The environment needed for this project:
1. [Python 3.6](https://www.python.org/downloads/release/python-360/)
2. [Apache Airflow](https://airflow.apache.org/)
3. [AWS account](https://aws.amazon.com/)
    - [IAM User](https://console.aws.amazon.com/iam) with `Programmatic access` and permission to write on S3.
    - [S3 bucket](https://aws.amazon.com/es/s3/)
5. Chek if you have a Redshift cluster, check `Set up for Redshift cluster` section
6. Configure Airflow, check `Airflow configuration` section

### Explanation of the files in the repository
1. **[dags](./dags)** 
    1. *[create_tables.sql](./dags/create_tables.sql)* SQL script which cotains the the creation of the Redshift tables.
    2. *[udac_example_dag.sql](./dags/udac_example_dag.sql)* python script with the dag definition.
2. **[plugins](./plugins)**
    1. *[helpers](./plugins/helpers)*
        1. *[\_\_init\_\_.py](./plugins/helpers/__init__.py)* load helpers directory  as module to import SqlQueries
        1. *[sql_queries.py](./plugins/helpers/sql_queries.py)* Select statements used to populate fact and dimension tables
    2. *[operatos](./plugins/operatos)*
        1. *[\_\_init\_\_.py](./plugins/operatos/__init__.py)* load operators directory 
        1. *[data_quality.py](./plugins/operatos/data_quality.py)* DAG operator used for data quality checks
        1. *[load_dimension.py](./plugins/operatos/load_dimension.py)* DAG operator used to load data into dimension tables
        1. *[load_fact.py](./plugins/operatos/load_fact.py)* DAG operator used to load data into fact table
        1. *[stage_redshift.py](./plugins/operatos/stage_redshift.py)* DAG operator used to load data into stage tables 
5. **[images](./images):** folder that contains the images used in this file.


### Instructions to run the project
1. clone the github repository: `git clone https://github.com/Erickramirez/Sparkify-Data-Pipelines-with-Airflow-S3-and-Redshift.git`
2. verify the Prerequisites
4. In the Airflow UI, enable the dag `redshift_dag`

## About the Data Warehouse solution
### Datasets
1. **Song data:** `s3://udacity-dend/song_data`  it is a subset of real data from 
[Million Song Dataset](http://millionsongdataset.com/) it is in JSON format: 
    ```
    {
        "num_songs": 1,
        "artist_id": "ARJIE2Y1187B994AB7",
        "artist_latitude": null,
        "artist_longitude": null,
        "artist_location": "",
        "artist_name": "Line Renaud",
        "song_id": "SOUPIRU12A6D4FA1E1",
        "title": "Der Kleine Dompfaff",
        "duration": 152.92036,
        "year": 0
    }
    ```
2. **Log data:** `s3://udacity-dend/log_data` consists of log files in JSON format 
generated by this [event simulator](https://github.com/Interana/eventsim) based on the songs in the dataset above. 
It has the following structure:  ![log-data](/images/log-data.png)

### Database Schema
It will be necesary to copy the JSON file in the S3 buckets into the staging tables. 
After this staging tables, the data is loaded into dimension and fact tables. 
This table definition is in `dags/create_tables.py`
1. **Staging tables**
    - **staging_songs:**  contains the data from the dataset `Song data` 
    - **staging_events:**  contains the data from the dataset `Log data` 
2. **Dimension tables**
    - **users:** users in the app - user_id, first_name, last_name, gender, level
    - **songs:** songs in music database - song_id, title, artist_id, year, duration
    - **artists:** artists in music database - artist_id, name, location, lattitude, longitude
    - **time:** timestamps of records in songplays broken down into specific units - start_time, hour, day, week, month, year, weekday
3. **Fact table**
    - **songplays:** records in event data associated with song plays i.e. records with page NextSong - 
songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
    
