from datetime import date, datetime
from math import ceil
from typing import Generic, Optional, Sequence, TypeVar
from uuid import UUID

from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel, conint

T = TypeVar("T")


class PaginationQueryParams(BaseModel, AbstractParams):
    page: conint(ge=1) = 1  # type: ignore
    per_page: int = 100

    def to_raw_params(self) -> RawParams:
        return RawParams(limit=self.per_page, offset=(self.page - 1) * self.per_page)


class Page(AbstractPage[T], Generic[T]):
    items: Sequence[T]
    total: conint(ge=0)  # type: ignore
    current_page: int
    next_page: int
    total_pages: int

    __params_type__ = PaginationQueryParams

    @classmethod
    def create(  # type: ignore[override]
        cls, items: Sequence[T], total: int, params: AbstractParams
    ) -> "Page[T]":
        raw = params.to_raw_params()
        if raw.limit == 0:  # type: ignore[attr-defined]
            total_pages = 0
        else:
            total_pages = int(ceil(total / float(raw.limit)))  # type: ignore[attr-defined]

        current_page = int((raw.offset / raw.limit) + 1)  # type: ignore[attr-defined]

        if current_page >= total_pages:
            next_page = -1
        else:
            next_page = current_page + 1

        return cls(
            items=items,
            total=total,
            current_page=current_page,
            next_page=next_page,
            total_pages=total_pages,
        )


class InDBBaseSerializer(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[date] = None

    class Config:
        orm_mode = True
