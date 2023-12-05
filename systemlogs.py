import logging

def configure_logging():
    try:
        logging.basicConfig(filename='systemlogs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    except Exception as e:
        print(f"An error occurred while configuring logging: {e}")

def log_debug(message):
    logging.debug(message)

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

def log_critical(message):
    logging.critical(message)