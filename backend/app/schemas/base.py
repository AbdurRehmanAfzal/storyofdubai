from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(cls, data: T, meta: PaginationMeta = None):
        return cls(success=True, data=data, meta=meta, error=None)

    @classmethod
    def fail(cls, code: str, message: str, details: dict = None):
        return cls(
            success=False,
            data=None,
            meta=None,
            error=ErrorDetail(code=code, message=message, details=details or {}),
        )
