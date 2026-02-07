import pytest
import base64
from utils import encrypt_aes256_base64, decrypt_aes256_base64_bytes, generate_random_string


class TestEncryption:
    """Тесты для функций шифрования/дешифрования."""

    def test_encrypt_decrypt_roundtrip(self):
        """Тест шифрования и дешифрования - возврат исходного значения."""
        # Arrange
        test_string = "https://example.com/test-url"

        # Act
        encrypted = encrypt_aes256_base64(test_string)
        decrypted = decrypt_aes256_base64_bytes(encrypted)

        # Assert
        assert decrypted == test_string
        assert encrypted != test_string

    def test_encrypt_different_strings(self):
        """Тест, что разные строки дают разный зашифрованный результат."""
        # Arrange
        string1 = "https://example.com/test1"
        string2 = "https://example.com/test2"

        # Act
        encrypted1 = encrypt_aes256_base64(string1)
        encrypted2 = encrypt_aes256_base64(string2)

        # Assert
        assert encrypted1 != encrypted2

    def test_encrypt_empty_string(self):
        """Тест шифрования пустой строки."""
        # Arrange
        empty_string = ""

        # Act
        encrypted = encrypt_aes256_base64(empty_string)
        decrypted = decrypt_aes256_base64_bytes(encrypted)

        # Assert
        assert decrypted == empty_string

    def test_decrypt_invalid_base64(self):
        """Тест дешифрования невалидной base64 строки."""
        # Arrange
        invalid_base64 = "not-a-valid-base64-string!"

        # Act & Assert
        with pytest.raises(Exception):
            decrypt_aes256_base64_bytes(invalid_base64)


class TestRandomStringGeneration:
    """Тесты для генерации случайных строк."""

    def test_generate_random_string_length(self):
        """Тест генерации строки правильной длины."""
        # Arrange
        lengths = [5, 10, 15]

        for length in lengths:
            # Act
            result = generate_random_string(length)

            # Assert
            assert len(result) == length

    def test_generate_random_string_characters(self):
        """Тест, что строка содержит только допустимые символы."""
        # Arrange
        length = 10
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        # Act
        result = generate_random_string(length)

        # Assert
        for char in result:
            assert char in allowed_chars

    def test_generate_random_string_uniqueness(self):
        """Тест, что генерируются разные строки."""
        # Arrange
        length = 8

        # Act
        strings = [generate_random_string(length) for _ in range(10)]

        # Assert
        assert len(set(strings)) == len(strings)

    def test_generate_random_string_zero_length(self):
        """Тест генерации строки нулевой длины."""
        # Arrange
        length = 0

        # Act
        result = generate_random_string(length)

        # Assert
        assert result == ""
        assert len(result) == 0