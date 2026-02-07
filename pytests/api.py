from unittest.mock import Mock, ANY
from database import ShortLinkWithThatUrlAlreadyExists, ThisLengthPoolFilled


class TestShortenEndpoint:
    """Тесты для эндпоинта создания короткой ссылки"""

    def test_successful_shorten(self, test_client, mock_database, mock_redis, sample_link_data):
        """Успешное создание короткой ссылки"""
        mock_database.create_link.return_value = (1, "abc123")

        response = test_client.post("/api/v1/shorten", json=sample_link_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        assert response.json() == {"url": "abc123"}

        mock_database.create_link.assert_called_once_with("https://example.com/", 6)
        mock_redis.set.assert_called_once()

    def test_shorten_existing_url(self, test_client, mock_database, sample_link_data):
        """Попытка создать ссылку для уже существующего URL"""
        mock_database.create_link.side_effect = ShortLinkWithThatUrlAlreadyExists(
            "Short link with that url already exists"
        )

        response = test_client.post("/api/v1/shorten", json=sample_link_data)

        assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
        assert "already exists" in response.json()["detail"]

    def test_shorten_pool_filled(self, test_client, mock_database, sample_link_data):
        """Попытка создать ссылку когда пул заданной длины заполнен"""
        mock_database.create_link.side_effect = ThisLengthPoolFilled(
            "Pool of short links with that length is filled"
        )

        response = test_client.post("/api/v1/shorten", json=sample_link_data)

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Pool" in response.json()["detail"]

    def test_shorten_technical_error(self, test_client, mock_database, sample_link_data):
        """Техническая ошибка при создании ссылки"""
        mock_database.create_link.side_effect = Exception("Database error")

        response = test_client.post("/api/v1/shorten", json=sample_link_data)

        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        assert "Technical troubles" in response.json()["detail"]


class TestRedirectEndpoint:
    """Тесты для эндпоинта редиректа"""

    def test_successful_redirect(self, test_client, mock_database, mock_redis, mock_link):
        """Успешный редирект по короткой ссылке"""
        mock_database.get_link_by_short_url.return_value = mock_link

        response = test_client.get("/abc123", follow_redirects=False)

        assert response.status_code == 307, f"Expected 307, got {response.status_code}"
        assert response.headers["location"] == "https://example.com"

        mock_redis.get.assert_called_once()
        mock_database.get_link_by_short_url.assert_called_once_with("abc123")
        mock_database.add_click_on_link.assert_called_once_with(1, ANY)

    def test_redirect_with_cache(self, test_client, mock_database, mock_redis, mock_link_cached):
        """Редирект с использованием кэша"""
        mock_redis.get.return_value = Mock(decode=Mock(return_value="encrypted_https://example.com_1"))

        import cache.main
        original_decrypt = cache.main.decrypt_aes256_base64_bytes
        cache.main.decrypt_aes256_base64_bytes = Mock(return_value="https://example.com")

        try:
            response = test_client.get("/abc123", follow_redirects=False)

            assert response.status_code == 307, f"Expected 307, got {response.status_code}"
            assert response.headers["location"] == "https://example.com"

            mock_database.get_link_by_short_url.assert_not_called()
            mock_database.add_click_on_link.assert_called_once_with(1, ANY)
        finally:
            cache.main.decrypt_aes256_base64_bytes = original_decrypt

    def test_redirect_nonexistent_link(self, test_client, mock_database, mock_redis):
        """Редирект по несуществующей ссылке"""
        mock_redis.get.return_value = None
        mock_database.get_link_by_short_url.return_value = None

        response = test_client.get("/nonexistent")

        assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
        assert "does not exist" in response.json()["detail"]

    def test_redirect_metadata_captured(self, test_client, mock_database, mock_redis, mock_link):
        """Проверка захвата метаданных при редиректе"""
        mock_database.get_link_by_short_url.return_value = mock_link

        headers = {
            "User-Agent": "Test-Agent/1.0"
        }

        response = test_client.get("/abc123", headers=headers, follow_redirects=False)

        assert response.status_code == 307, f"Expected 307, got {response.status_code}"

        call_args = mock_database.add_click_on_link.call_args
        assert call_args is not None
        metadata = call_args[0][1]
        assert "User-Agent: Test-Agent/1.0" in metadata

        assert "IP:" in metadata