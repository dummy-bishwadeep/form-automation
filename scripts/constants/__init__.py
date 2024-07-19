import os

class EnvironmentConstants:
    project_id = os.getenv("PROJECT_ID")
    base_path = os.getenv('BASE_PATH')
    auth_endpoint = os.getenv('AUTH_ENDPOINT')
    tz = os.getenv('tz')
    key_path = os.getenv('keys_path')