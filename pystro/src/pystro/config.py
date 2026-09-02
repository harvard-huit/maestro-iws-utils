import json
import logging
import boto3
from pathlib import Path

class Config:
    def __init__(self, data: dict):
        self.aws_secret_arn = data['aws-secret-arn']
        self.aws_region = data['aws-region']
        self.base_url = data['apigee-api-url']
        self.api_token = None

        self.set_api_token()
        self.log_level = data.get('log_level', "INFO")
        self.log_format = data.get('log_format', "%(asctime)s - %(levelname)s - %(message)s")

    def set_api_token(self):
        """
        Retrieve the authentication token for the API.

        Returns:
            str: The api token.
        """
        if self.api_token is None:
            secrets_client = boto3.client('secretsmanager', region_name=self.aws_region)
            secret_value = secrets_client.get_secret_value(SecretId=self.aws_secret_arn)
            self.api_token = json.loads(secret_value['SecretString'])['apigee-api-key']

    @classmethod
    def from_json(cls, file_name: str = '', environment: str = 'test') -> 'Config':
        if not file_name:
            file_path = Path(__file__).parent / '.config.json'
        else:
            file_path = Path(file_name)
            
        with open(file_path, 'r') as file:
            configuration_data = json.load(file)
        data = configuration_data.get('environments', {}).get(environment, {}) | configuration_data.get('logging', {"foo": "bar"})
        return cls(data)
    
def load_json(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)
            
def get_logger(config: Config, module_name: str) -> logging.Logger:
    """
    Return a logger configured with the specified log format and log level from the config.

    Args:
        config (Config): The configuration object containing log format and log level.
        module_name (str): The name of the module for which the logger is being created.
    """
    log_format = config.log_format
    log_level = config.log_level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(level=numeric_level, format=log_format)
    return logging.getLogger(module_name)