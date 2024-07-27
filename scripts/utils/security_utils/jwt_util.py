import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    MissingRequiredClaimError,
)

from scripts.config.app_configurations import KeyPath
from scripts.constants.app_constants import Secrets
from scripts.logging.logger import logger


class JWT:
    def __init__(self):
        self.max_login_age = Secrets.LOCK_OUT_TIME_MINS
        self.issuer = Secrets.issuer
        self.alg = Secrets.alg
        self.public = KeyPath.public_key
        self.private = KeyPath.private_key
        self.secret_key = Secrets.signature_key

    def encode(self, payload):
        try:
            encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.alg)
            return encoded_jwt
        except Exception as e:
            logger.exception(f"Exception while encoding JWT: {str(e)}")
            raise