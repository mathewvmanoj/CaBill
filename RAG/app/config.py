# config.py
import json

# Load the configuration from the config.json file
config_file = './configs/config.json'

with open(config_file, 'r') as file:
    config = json.load(file)

# Get log settings from config
log_file = config['logging'].get('log_file', 'logs/system.log')  # Default log file path
log_level_str = config['logging'].get('log_level', 'INFO')  # Default log level
api_key = config.get("groq_api_key")
