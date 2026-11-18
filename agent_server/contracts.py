from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from mcp_server.server import Period


class AgentError(Exception):
    def __init__(self, code, message, status=503, query_id=None):
        super().__init__(message)
        self.code, self.message, self.status, self.query_id = code, message, status, query_id


class Context(BaseModel):
    model_config = ConfigDict(extra='forbid')
    period: Period
    products: list[str] = Field(default_factory=list, max_length=100)
    categories: list[str] = Field(default_factory=list, max_length=100)
    basises: list[str] = Field(default_factory=list, max_length=100)

    @field_validator('products', 'categories', 'basises')
    @classmethod
    def names(cls, values):
        if any(not value.strip() or len(value) > 255 or ',' in value for value in values):
            raise ValueError('Названия должны быть непустыми строками без запятых, до 255 символов.')
        return sorted(set(value.strip() for value in values))

    def arguments(self):
        values = self.model_dump()
        return {key:value for key,value in values.items() if value != []}


class Message(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['summary', 'comparison', 'details', 'chat']
    context: Context
    baseline: Period | None = None
    message: str = Field(default='', max_length=4000)
    history: list[Message] = Field(default_factory=list, max_length=8)

    @field_validator('message')
    @classmethod
    def trim(cls, value):
        return value.strip()
