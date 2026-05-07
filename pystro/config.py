import json
import boto3

class Config:
    def __init__(self, data: dict):
        self.aws_secret_arn = data['aws-secret-arn']
        self.aws_region = data['aws-region']
        self.base_url = data['maestro-api-url']
        self.api_token = None

        self.set_api_token()

    def set_api_token(self):
        """
        Retrieve the authentication token for the API.

        Returns:
            str: The api token.
        """
        if self.api_token is None:
            secrets_client = boto3.client('secretsmanager', region_name=self.aws_region)
            secret_value = secrets_client.get_secret_value(SecretId=self.aws_secret_arn)
            self.api_token = json.loads(secret_value['SecretString'])['maestro-api-key']
            

    @classmethod
    def from_json(cls, file_path: str = './pystro/.config.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return cls(data)