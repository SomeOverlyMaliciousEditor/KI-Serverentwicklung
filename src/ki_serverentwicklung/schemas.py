from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OrderWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Annotated[str, Field(min_length=1, max_length=50)]
    total_cents: Annotated[int, Field(ge=0, le=2_147_483_647)]


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    ordered_at: datetime
    status: str
    total_cents: int
    version: int
