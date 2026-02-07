import dataclasses
import datetime
from typing import Optional, Union

import utils


@dataclasses.dataclass
class Link:
    """Модель для представления записи из таблицы links."""
    id: int
    _short_url: str = dataclasses.field()
    _original_url: str = dataclasses.field()
    clicks: int
    short_url_length: int

    _banned: Union[str, bool] = dataclasses.field(default="0")
    _banned_at: Optional[Union[str, datetime.datetime]] = dataclasses.field(default=None)
    _created_at: Union[str, datetime.datetime] = dataclasses.field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    _expires_at: Optional[Union[str, datetime.datetime]] = dataclasses.field(default=None)

    def __post_init__(self):
        """Преобразуем строковые значения после инициализации."""
        if isinstance(self._banned, str):
            self._banned = self._banned == "1"
        elif isinstance(self._banned, int):
            self._banned = bool(self._banned)

        if self._banned_at and isinstance(self._banned_at, str):
            self._banned_at = datetime.datetime.strptime(self._banned_at, "%Y-%m-%d %H:%M:%S")

        if self._created_at and isinstance(self._created_at, str):
            self._created_at = datetime.datetime.strptime(self._created_at, "%Y-%m-%d %H:%M:%S")

        if self._expires_at and isinstance(self._expires_at, str):
            self._expires_at = datetime.datetime.strptime(self._expires_at, "%Y-%m-%d %H:%M:%S")

    @property
    def banned(self) -> bool:
        """Флаг блокировки ссылки."""
        return self._banned

    @banned.setter
    def banned(self, value: bool) -> None:
        """Установка флага блокировки."""
        self._banned = bool(value)

    @property
    def banned_at(self) -> Optional[datetime.datetime]:
        """Дата блокировки ссылки."""
        return self._banned_at

    @banned_at.setter
    def banned_at(self, value: Optional[datetime.datetime]) -> None:
        """Установка даты блокировки."""
        self._banned_at = value

    @property
    def created_at(self) -> datetime.datetime:
        """Дата создания ссылки."""
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        """Установка даты создания."""
        if isinstance(value, str):
            self._created_at = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        else:
            self._created_at = value

    @property
    def expires_at(self) -> Optional[datetime.datetime]:
        """Дата истечения срока действия ссылки."""
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: Optional[datetime.datetime]) -> None:
        """Установка даты истечения срока."""
        if isinstance(value, str):
            if value:
                self._expires_at = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            else:
                self._expires_at = None
        else:
            self._expires_at = value

    @property
    def short_url(self) -> str:
        """Расшифрованный короткий URL."""
        return self._short_url

    @short_url.setter
    def short_url(self, value: str) -> None:
        """Установка короткого URL в расшифрованном виде."""
        try:
            self._short_url = utils.decrypt_aes256_base64_bytes(value)
        except Exception as e:
            print(e)
            self._short_url = value

    @property
    def original_url(self) -> str:
        """Расшифрованный оригинальный URL."""
        return self._original_url

    @original_url.setter
    def original_url(self, value: str) -> None:
        """Установка оригинального URL в расшифрованном виде."""
        try:
            self._original_url = utils.decrypt_aes256_base64_bytes(value)
        except Exception as e:
            print(e)
            self._original_url = value
