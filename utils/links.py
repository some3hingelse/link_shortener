import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import secrets
import string

from config import AESConfig


aes_config = AESConfig()


def encrypt_aes256_base64(plaintext: str) -> str:
    """
    Функция шифрования строки в aes-256 + base64
    """
    key_b64 = aes_config.aes_key_b64.get_secret_value()
    iv_b64 = aes_config.aes_iv_b64.get_secret_value()

    if not key_b64 or not iv_b64:
        raise ValueError("AES_KEY_B64 и AES_IV_B64 должны быть установлены в переменных окружения")

    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
    if len(key) != 32:
        raise ValueError("Ключ должен быть 32 байта для AES-256")
    if len(iv) != 16:
        raise ValueError("IV должен быть 16 байт")

    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt_aes256_base64_bytes(encrypted_base64: str) -> str:
    """
    Функция дешифрования строки из base64 + aes-256
    """
    key_b64 = aes_config.aes_key_b64.get_secret_value()
    iv_b64 = aes_config.aes_iv_b64.get_secret_value()

    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)

    if len(key) != 32:
        raise ValueError("Ключ должен быть 32 байта для AES-256")
    if len(iv) != 16:
        raise ValueError("IV должен быть 16 байт")

    ciphertext = base64.b64decode(encrypted_base64)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted_data.decode('utf-8')


def generate_random_string(length: int) -> str:
    """
    Генерация случайной строки заданной длины.

    :param length: Длина генерируемой строки

    :returns: Случайная строка из букв и цифр
    """
    charset = string.ascii_letters + string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))
