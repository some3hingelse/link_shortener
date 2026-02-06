from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings


class AESConfig(BaseSettings):
    """
    Конфигурация для AES-256 шифрования.
    Ожидает ключ и IV в base64 формате.
    """

    aes_key_b64: SecretStr
    aes_iv_b64: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra="ignore"


class DbConfig(BaseSettings):
    db_filename: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra="ignore"
