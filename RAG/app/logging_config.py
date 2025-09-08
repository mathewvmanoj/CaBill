import json
import os
import logging

# Load the configuration from the config.json file
config_file = './configs/config.json'

with open(config_file, 'r') as file:
    config = json.load(file)

# Get log settings from config
log_file = config['logging'].get('log_file', 'logs/system.log')  # Default log file path
log_level_str = config['logging'].get('log_level', 'INFO')  # Default log level
api_key = config.get("groq_api_key")

# Convert log level string to logging level constant
log_level = getattr(logging, log_level_str.upper(), logging.INFO)

# Ensure the log directory exists
log_dir = os.path.dirname(log_file)
if not os.path.exists(log_dir) and log_dir != '':
    os.makedirs(log_dir)

# Create a logger
def configure_logger():
    # Create a logger
    logger = logging.getLogger(__name__)
    
    # Set the minimum level of logging
    logger.setLevel(log_level)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)  # Log file location from config
    file_handler.setLevel(log_level)  # Set level for file logging
    
    console_handler = logging.StreamHandler()  # Console handler to log to the terminal
    console_handler.setLevel(log_level)  # Set level for console logging
    
    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
