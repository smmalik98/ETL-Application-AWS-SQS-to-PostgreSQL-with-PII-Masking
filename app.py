Here are the docstrings added to each function to explain their purpose and functionality:

```python
# Import necessary libraries
import boto3
import json
import os
from hashlib import sha256
import psycopg2
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# AWS and LocalStack configuration
aws_region = 'us-east-1'
localstack_endpoint = 'http://localhost:4566/'
sqs_queue_name = 'login-queue'
sqs_queue_url = 'http://localhost:4566/000000000000/login-queue'

def configure_dummy_credentials():
    """
    Set dummy AWS credentials for LocalStack.
    This function sets environment variables for AWS access key and secret key with dummy values.
    """
    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'

def fetch_sqs_messages():
    """
    Fetch messages from the SQS queue and process them.
    This function connects to the SQS queue, retrieves messages, processes each message by masking PII,
    and then inserts the processed data into a PostgreSQL database.
    """
    configure_dummy_credentials()
    sqs_client = boto3.client('sqs', region_name=aws_region, endpoint_url=localstack_endpoint)

    print("Attempting to fetch messages from SQS queue...")
    try:
        messages_response = sqs_client.receive_message(
            QueueUrl=sqs_queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=30,
            WaitTimeSeconds=20,
            AttributeNames=['All'],
            MessageAttributeNames=['All'],
        )

        print("Received response from SQS.")
        if 'Messages' in messages_response:
            messages = messages_response['Messages']
            print(f'Number of messages received: {len(messages)}')
            for msg in messages:
                json_body = json.loads(msg['Body'])
                handle_json_message(json_body)
        else:
            print('No messages found in the queue.')

    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
            print(f"The queue named {sqs_queue_name} does not exist.")
        else:
            print(f"Unexpected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def mask_pii_fields(data):
    """
    Mask PII fields in the JSON data.
    This function takes a dictionary, copies it, and replaces the values of 'device_id' and 'ip' fields
    with their SHA-256 hashed equivalents.

    Args:
        data (dict): The input dictionary containing PII fields.

    Returns:
        dict: A copy of the input dictionary with masked PII fields.
    """
    data_copy = data.copy()
    fields_to_mask = ['device_id', 'ip']

    for field in fields_to_mask:
        if field in data_copy:
            original_value = data_copy[field]
            masked_value = sha256(original_value.encode()).hexdigest()
            data_copy[field] = masked_value

    return data_copy

def handle_json_message(data):
    """
    Process and transform JSON data.
    This function checks the validity of the message type, masks PII fields, flattens the JSON structure,
    and inserts the transformed data into the PostgreSQL database.

    Args:
        data (dict): The input JSON data to process.
    """
    if 'foo' in data and data['foo'] == 'invalid_message_type':
        print('Error: Invalid message type received.')
    else:
        print(f'Processing message: {data}')
        masked_data = mask_pii_fields(data)
        flattened_data = flatten_json(masked_data)
        insert_into_postgres(flattened_data)

def flatten_json(data):
    """
    Flatten a nested JSON structure.
    This function takes a nested dictionary and flattens it into a single-level dictionary with dot-separated keys.

    Args:
        data (dict): The input nested dictionary.

    Returns:
        dict: A flattened version of the input dictionary.
    """
    flattened = {}

    for key, value in data.items():
        if isinstance(value, dict):
            nested_flattened = flatten_json(value)
            for subkey, subvalue in nested_flattened.items():
                flattened[f"{key}.{subkey}"] = subvalue
        else:
            flattened[key] = value

    return flattened

def alter_app_version_column():
    """
    Alter the app_version column data type in PostgreSQL.
    This function connects to the PostgreSQL database and changes the data type of the 'app_version' column
    in the 'user_logins' table to varchar.
    """
    connection = psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )

    cursor = connection.cursor()
    alter_query = "ALTER TABLE user_logins ALTER COLUMN app_version TYPE varchar"

    try:
        cursor.execute(alter_query)
        connection.commit()
        print('Altered app_version column type to varchar.')
    except psycopg2.Error as error:
        connection.rollback()
        print(f'Error: {error}')

    connection.close()

def insert_into_postgres(flattened_data):
    """
    Insert flattened data into PostgreSQL.
    This function inserts the provided flattened dictionary into the 'user_logins' table in PostgreSQL.

    Args:
        flattened_data (dict): The flattened data to insert into the database.
    """
    connection = psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )

    cursor = connection.cursor()

    user_id = flattened_data['user_id']
    device_type = flattened_data['device_type']
    masked_ip = flattened_data['ip']
    masked_device_id = flattened_data['device_id']
    locale = flattened_data['locale']
    app_version = str(flattened_data['app_version'])  # Ensure app_version is a string for varchar type
    create_date = flattened_data.get('create_date', None)

    insert_query = """
    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    data_tuple = (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)

    try:
        cursor.execute(insert_query, data_tuple)
        connection.commit()
        print(f'Data inserted for user_id: {user_id}')
    except psycopg2.Error as error:
        connection.rollback()
        print(f'Error inserting data: {error}')

    connection.close()

def display_user_logins_table():
    """
    Print the contents of the user_logins table.
    This function retrieves and prints all records from the 'user_logins' table in the PostgreSQL database.
    """
    connection = psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )

    cursor = connection.cursor()
    select_query = "SELECT * FROM user_logins"
    cursor.execute(select_query)
    records = cursor.fetchall()

    print('\nContents of user_logins table:\n')
    print('user_id | device_type | masked_ip | masked_device_id | locale | app_version | create_date')
    for row in records:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    """
    Main entry point of the script.
    This section of the script alters the app_version column, fetches and processes messages from SQS,
    and displays the contents of the user_logins table.
    """
    print("Starting application...")
    alter_app_version_column()
    fetch_sqs_messages()
    display_user_logins_table()
    print("Application finished.")
```