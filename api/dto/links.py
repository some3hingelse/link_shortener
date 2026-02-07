from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_core import Url


class CreateShortLinkRequest(BaseModel):
    """Тело запроса на создание короткой ссылки"""
    url: Url
    length: int = Field(..., ge=5, le=15)
    expires_at: Optional[datetime] = None
