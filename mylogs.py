import logging
import boto3
import watchtower

# Initialize the CloudWatch Logs client
client = boto3.client('logs', region_name='us-west-2')  # Change region if needed
log_group_name = '/aws/myapp/logs'

# Set up logging to CloudWatch
cloudwatch_handler = watchtower.CloudWatchLogHandler(log_group=log_group_name)

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
