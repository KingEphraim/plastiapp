import logging

# Configure the logging settings to use the console
logging.basicConfig(
    # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.INFO
)

def add_to_log(log_message):
    logging.info(log_message)