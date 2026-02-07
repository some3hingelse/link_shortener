from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AESConfig(BaseSettings):
    """
    Конфигурация для AES-256 шифрования.

    :param aes_key_b64: Ключ шифрования в формате base64 (32 байта)
    :param aes_iv_b64: Вектор инициализации в формате base64 (16 байт)
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
    """
    Конфигурация для подключения к SQLite базе данных.

    :param db_filename: Путь к файлу базы данных SQLite
    """
    db_filename: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra="ignore"


class RedisConfig(BaseSettings):
    """
    Конфигурация для подключения к Redis серверу.

    :param redis_url: URL для подключения к Redis (например, redis://localhost:6379)
    """
    redis_url: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra="ignore"


class ApiConfig(BaseSettings):
    """
    Конфигурация для запуска API на FastAPI

    :param host: Хост на котором будет развёрнуто API (например, 0.0.0.0).
    :param port: Порт на котором будет развёрнуто API (например, 8000).
    """
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra="ignore"
