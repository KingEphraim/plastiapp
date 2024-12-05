import logging
import boto3
import watchtower
import json

# Load AWS configuration from the config file
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize CloudWatch Logs client
client = boto3.client(
    'logs',
    region_name=config['aws_region'],
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key']
)

# Define the CloudWatch Logs group name
LOG_GROUP_NAME = '/aws/plastiqz/logs'

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        watchtower.CloudWatchLogHandler(log_group=LOG_GROUP_NAME, boto3_client=client),
        logging.StreamHandler()
    ]
)

# Define a function to log messages
def add_to_log(message):
    logging.info(message)
