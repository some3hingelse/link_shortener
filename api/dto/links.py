from pydantic import BaseModel, PositiveInt
from pydantic_core import Url


class CreateShortLinkRequest(BaseModel):
    """Тело запроса на создание короткой ссылки"""
    url: Url
    length: PositiveInt
