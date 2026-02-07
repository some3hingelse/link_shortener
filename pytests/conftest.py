import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_cache_warmup(app):
    yield {}


with patch('cache.cache_warmup', mock_cache_warmup):
    from api.main import app


@pytest.fixture(autouse=True)
def mock_all_dependencies():
    """Мокаем все зависимости глобально"""
    mock_db = MagicMock()
    mock_db.create_link = Mock()
    mock_db.get_link_by_short_url = Mock()
    mock_db.add_click_on_link = Mock()
    mock_db.get_all_links = Mock(return_value=[])

    mock_redis = Mock()
    mock_redis.get = Mock(return_value=None)
    mock_redis.set = Mock()

    from dataclasses import dataclass

    @dataclass
    class MockLinkCached:
        original_url: str
        id: int

    mock_link_cached = MockLinkCached(original_url="https://example.com", id=1)

    with patch('api.main.database', mock_db):
        with patch('cache.main.database', mock_db):
            with patch('cache.main.r', mock_redis):
                with patch('cache.main.encrypt_aes256_base64') as mock_encrypt:
                    with patch('cache.main.decrypt_aes256_base64_bytes') as mock_decrypt:
                        mock_encrypt.side_effect = lambda x: f"encrypted_{x}"
                        mock_decrypt.side_effect = lambda x: x.replace("encrypted_", "")

                        yield {
                            'database': mock_db,
                            'redis': mock_redis,
                            'link_cached': mock_link_cached,
                            'encrypt': mock_encrypt,
                            'decrypt': mock_decrypt
                        }


@pytest.fixture
def test_client():
    """Создаем тестовый клиент"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_database(mock_all_dependencies):
    return mock_all_dependencies['database']


@pytest.fixture
def mock_redis(mock_all_dependencies):
    return mock_all_dependencies['redis']


@pytest.fixture
def mock_link_cached(mock_all_dependencies):
    return mock_all_dependencies['link_cached']


@pytest.fixture
def sample_link_data():
    return {
        "url": "https://example.com",
        "length": 6
    }


@pytest.fixture
def mock_link():
    mock_link = Mock()
    mock_link.id = 1
    mock_link.original_url = "https://example.com"
    mock_link.short_url = "abc123"
    return mock_link