"""
This file exposes configurations from config file and environments as Class Objects
"""

import os.path
import sys
from configparser import BasicInterpolation, ConfigParser


class EnvInterpolation(BasicInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)

        if not os.path.expandvars(value).startswith("$"):
            return os.path.expandvars(value)
        else:
            return

try:
    config = ConfigParser(interpolation=EnvInterpolation())

    current_file_path = os.path.abspath(__file__)
    project_parent_path = current_file_path

    for _ in range(3):
        project_parent_path = os.path.dirname(project_parent_path)
    config_path = os.path.join(project_parent_path, 'conf/application.conf')
    config.read(config_path)
except Exception as e:
    print(f"Error while loading the config: {e}")
    print("Failed to Load Configuration. Exiting!!!")
    sys.stdout.flush()
    sys.exit()


class LoggingDetails:
    LOG_PATH: str = config["LOGGING"]["LOG_PATH"]
    LOG_LEVEL: str = config["LOGGING"]["LOG_LEVEL"]
    BACKUP_COUNT: int = int(config["LOGGING"]["BACKUP_COUNT"])
    MAX_BYTES: int = int(config["LOGGING"]["MAX_BYTES"])


class Path:
    CONFIG_PATH: str = config["PATH"]["CONFIG_PATH"]


class Service:
    SERVICE_HOST: str = config["SERVICE"]["SERVICE_HOST"]
    SERVICE_PORT: int = int(config["SERVICE"]["SERVICE_PORT"])
    WORKERS: str = config["SERVICE"]["WORKERS"]
    PROJECT_NAME: str = config["SERVICE"]["PROJECT_NAME"]


class EnvironmentDetails:
    AUTH_ENDPOINT: str = config["ENVIRONMENT"]["AUTH_ENDPOINT"]
    BASE_PATH: str = config["ENVIRONMENT"]["BASE_PATH"]
    PROJECT_ID: str = config["ENVIRONMENT"]["PROJECT_ID"]
    tz: str = config["ENVIRONMENT"]["tz"]


class KeyPath:
    private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQClilTaeHq6Zc+kWHCNl1O0btGRm7ct3O5zqWx1mwwLUWH14eft
Hi5wIbOYh79JQ9BO2OA4UjPq31uwmJ96Okl0OULfENhwd/D7P3mnoRlktPT2t+tt
RRrKvx3wNpOy/3nBsXnNt8EKxyA7k9vbqLbv9pGw2hcqOYe/NGTkmm1PswIDAQAB
AoGAZPARR1l5NBkKYGKQ1rU0E+wSmx+AtVVmjF39RUSyNmB8Q+poebwSgsr58IKt
T6Yq6Tjyl0UAZTGmferCK0xJJrqyP0hMn4nNNut+acWMKyt+9YrA2FO+r5Jb9JuT
SK35xXnM4aZLGppgWJxRzctpIz+qkf6oLRSZme0AuiqcwYECQQDY+QDL3wbWplRW
bze0DsZRMkDAkNY5OCydvjte4SR/mmAzsrpNrS5NztWbaaQrefoPbsdYBPbd8rS7
C/s/0L1zAkEAw1EC5zt2STuhkcKLa/tL+bk8WHHHtf19aC9kBj1TvWBFh+JojWCo
86iK5fLcHzhyQx5Qi3E9LG2HvOWhS1iUwQJAKbEHHyWW2c4SLJ2oVXf1UYrXeGkc
UNhjclgobl3StpZCYAy60cwyNo9E6l0NR7FjhG2j7lzd1t4ZLkvqFmQU0wJATLPe
yQIwBLh3Te+xoxlQD+Tvzuf3/v9qpWSfClhBL4jEJYYDeynvj6iry3whd91J+hPI
m8o/tNfay5L+UcGawQJAAtbqQc7qidFq+KQYLnv5gPRYlX/vNM+sWstUAqvWdMze
JYUoTHKgiXnSZ4mizI6/ovsBOMJTb6o1OJCKQtYylw==
-----END RSA PRIVATE KEY-----
"""

    public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQClilTaeHq6Zc+kWHCNl1O0btGR
m7ct3O5zqWx1mwwLUWH14eftHi5wIbOYh79JQ9BO2OA4UjPq31uwmJ96Okl0OULf
ENhwd/D7P3mnoRlktPT2t+ttRRrKvx3wNpOy/3nBsXnNt8EKxyA7k9vbqLbv9pGw
2hcqOYe/NGTkmm1PswIDAQAB
-----END PUBLIC KEY-----
"""

