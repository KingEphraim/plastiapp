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

# Define the CloudWatch Logs group name and stream name
LOG_GROUP_NAME = '/aws/plastiqz/logs'
LOG_STREAM_NAME = 'plastiqz-log-stream'  # You can modify this based on your use case

# Ensure log group exists
try:
    client.describe_log_groups(logGroupNamePrefix=LOG_GROUP_NAME)
except client.exceptions.ResourceNotFoundException:
    client.create_log_group(logGroupName=LOG_GROUP_NAME)

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        watchtower.CloudWatchLogHandler(log_group=LOG_GROUP_NAME, stream_name=LOG_STREAM_NAME, boto3_client=client),
        logging.StreamHandler()
    ]
)

# Define a function to log messages
def add_to_log(message):
    logging.info(message)
