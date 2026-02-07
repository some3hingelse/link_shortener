"""
Тесты для модуля базы данных.
"""
import pytest
import sqlite3


class TestDatabaseClass:
    """Тесты для класса Database."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        from database import Database
        self.db = Database()

    def test_init_creates_connection(self):
        """Тест инициализации подключения к базе данных."""
        # Assert
        assert self.db.connection is not None
        assert self.db.cursor is not None
        assert isinstance(self.db.connection, sqlite3.Connection)

    def test_get_link_by_short_url_not_found(self):
        """Тест поиска несуществующей ссылки."""
        # Act
        result = self.db.get_link_by_short_url("nonexistent_url_12345")

        # Assert
        assert result is None

    def test_add_click_on_link(self):
        """Тест добавления клика по ссылке."""
        # Act - просто проверяем что функция не падает
        try:
            self.db.add_click_on_link(99999, "test metadata")  # Несуществующий ID
            assert True
        except Exception as e:
            if "FOREIGN KEY" in str(e):
                assert True
            else:
                pytest.fail(f"Функция add_click_on_link упала с ошибкой: {e}")


class TestLinkModel:
    """Тесты для модели Link."""

    def test_link_creation(self):
        """Тест создания объекта Link."""
        from database import Link

        link = Link(
            id=1,
            _short_url="enc_short",
            _original_url="enc_orig",
            clicks=5,
            short_url_length=8,
            _banned="0",
            _banned_at=None,
            _created_at="2024-01-01 10:00:00",
            _expires_at=None
        )

        assert link.id == 1
        assert link.clicks == 5
        assert link.short_url_length == 8