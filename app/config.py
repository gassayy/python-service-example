"""Config file for Pydantic and FastAPI, using environment variables."""

import base64
import os
from enum import Enum
from functools import lru_cache
from typing import Union, TypeAlias

from pydantic import Field
from pydantic.networks import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

HttpUrlStr: TypeAlias = HttpUrl

class Settings(BaseSettings):
    """Configuration settings for the application."""
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # DEBUG mode for development
    DEBUG: bool = Field(default=False, env="DEBUG")
    APP_NAME: str = Field(default="service-example", env="APP_NAME")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    # Database configuration
    DB_CONN_URL: str = Field(..., env="DB_CONN_URL")



@lru_cache
def get_settings():
    """Cache settings when accessed throughout app."""
    _settings = Settings()

    if _settings.DEBUG:
        # Enable detailed Python async debugger
        os.environ["PYTHONASYNCIODEBUG"] = "1"
        print(f"Loaded settings: {_settings.model_dump()}")
    return _settings

@lru_cache
def get_cipher_suite():
    """Cache cypher suite."""
    # Fernet is used by cryptography as a simple and effective default
    # it enforces a 32 char secret.
    #
    # In the future we could migrate this to HS384 encryption, which we also
    # use for our JWT signing. Ideally this needs 48 characters, but for now
    # we are stuck at 32 char to maintain support with Fernet (reuse the same key).
    
    return Fernet(settings.ENCRYPTION_KEY.get_secret_value())


def encrypt_value(password: Union[str, HttpUrlStr]) -> str:
    """Encrypt value before going to the DB."""
    cipher_suite = get_cipher_suite()
    encrypted_password = cipher_suite.encrypt(password.encode("utf-8"))
    return base64.b64encode(encrypted_password).decode("utf-8")


def decrypt_value(db_password: str) -> str:
    """Decrypt the database value."""
    cipher_suite = get_cipher_suite()
    encrypted_password = base64.b64decode(db_password.encode("utf-8"))
    decrypted_password = cipher_suite.decrypt(encrypted_password)
    return decrypted_password.decode("utf-8")



settings = get_settings()