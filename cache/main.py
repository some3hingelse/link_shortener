import dataclasses
from contextlib import asynccontextmanager

import redis

from config import RedisConfig
from database.core import database
from utils import encrypt_aes256_base64, decrypt_aes256_base64_bytes

redis_config = RedisConfig()
r = redis.from_url(redis_config.redis_url.get_secret_value())


def set_short_link(short_url: str, original_url: str, link_id: int):
    """
    Сохраняет короткую ссылку в Redis кэше.

    :param short_url: Короткий URL
    :param original_url: Оригинальный URL
    :param link_id: ID ссылки в базе данных
    """
    r.set(encrypt_aes256_base64(short_url), encrypt_aes256_base64(original_url)+"_"+str(link_id))


@dataclasses.dataclass
class LinkCached:
    original_url: str
    id: int


def get_short_link(short_url) -> LinkCached | None:
    """
    Получает кэшированную ссылку из Redis.

    :param short_url: Короткий URL для поиска в кэше
    :return: Объект LinkCached с данными ссылки или None, если ссылка не найдена
    """
    try:
        result = r.get(encrypt_aes256_base64(short_url)).decode()
        link_id = int(result.split("_")[-1])
        original_url = decrypt_aes256_base64_bytes(result.split("_")[0])
        return LinkCached(original_url, link_id)
    except:
        return None


@asynccontextmanager
async def cache_warmup(_):
    links = database.get_all_links()
    for link in links:
        r.set(link[1], link[2]+"_"+str(link[0]))
    yield

