import logging
import boto3
import watchtower
import json

# Load region and credentials from config.json file
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize the CloudWatch Logs client using credentials from config.json
client = boto3.client(
    'logs',
    region_name=config['aws_region'],
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key']
)

log_group_name = '/aws/myapp/logs'

# Set up logging to CloudWatch
cloudwatch_handler = watchtower.CloudWatchLogHandler(log_group=log_group_name, boto3_client=client)

# Set up local console logging
console_handler = logging.StreamHandler()

# Configure logging format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# Attach the handlers to the logger
cloudwatch_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Set up the logging configuration
logging.basicConfig(
    level=logging.INFO,
    handlers=[cloudwatch_handler, console_handler]
)

def add_to_log(log_message):
    logging.info(log_message)
