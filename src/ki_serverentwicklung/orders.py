import re
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ki_serverentwicklung.database import get_session
from ki_serverentwicklung.models import Customer, Order
from ki_serverentwicklung.schemas import OrderRead, OrderWrite

router = APIRouter(tags=["orders"])
SessionDependency = Annotated[Session, Depends(get_session)]
_ETAG_PATTERN = re.compile(r'^"order-(\d+)-v(\d+)"$')


def _etag(order: Order) -> str:
    return f'"order-{order.id}-v{order.version}"'


def _required_if_match(value: str | None) -> list[tuple[int, int]]:
    if value is None:
        raise HTTPException(status_code=428, detail="If-Match header is required")
    candidates = [item.strip() for item in value.split(",")]
    if "*" in candidates:
        raise HTTPException(status_code=412, detail="If-Match does not match")
    tags = [
        match
        for candidate in candidates
        if not candidate.startswith("W/")
        if (match := _ETAG_PATTERN.fullmatch(candidate)) is not None
    ]
    if not tags:
        raise HTTPException(status_code=412, detail="If-Match does not match")
    return [(int(match.group(1)), int(match.group(2))) for match in tags]


@router.get("/customers/{customer_id}/orders", response_model=list[OrderRead])
def list_customer_orders(customer_id: int, session: SessionDependency) -> list[Order]:
    if session.get(Customer, customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return list(
        session.scalars(
            select(Order).where(Order.customer_id == customer_id).order_by(Order.id)
        )
    )


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    response: Response,
    session: SessionDependency,
    if_none_match: Annotated[str | None, Header()] = None,
) -> OrderRead | Response:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    tag = _etag(order)
    response.headers["ETag"] = tag
    if if_none_match is not None:
        candidates = [candidate.strip() for candidate in if_none_match.split(",")]
        weak_candidates = [candidate.removeprefix("W/") for candidate in candidates]
        if "*" in candidates or tag in weak_candidates:
            return Response(
                status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": tag}
            )
    return OrderRead.model_validate(order)


@router.post(
    "/customers/{customer_id}/orders",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    customer_id: int,
    body: OrderWrite,
    response: Response,
    session: SessionDependency,
) -> Order:
    if session.get(Customer, customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    order = Order(customer_id=customer_id, **body.model_dump())
    session.add(order)
    session.commit()
    session.refresh(order)
    response.headers["Location"] = f"/orders/{order.id}"
    response.headers["ETag"] = _etag(order)
    return order


@router.put("/orders/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    body: OrderWrite,
    response: Response,
    session: SessionDependency,
    if_match: Annotated[str | None, Header()] = None,
) -> OrderRead:
    tags = _required_if_match(if_match)
    versions = [version for tag_id, version in tags if tag_id == order_id]
    if not versions:
        raise HTTPException(status_code=412, detail="If-Match does not match")

    values = body.model_dump()
    updated_id = session.execute(
        update(Order)
        .where(Order.id == order_id, Order.version.in_(versions))
        .values(**values, version=Order.version + 1)
        .returning(Order.id)
        .execution_options(synchronize_session=False)
    ).scalar_one_or_none()
    if updated_id is None:
        session.rollback()
        if session.get(Order, order_id) is None:
            raise HTTPException(status_code=404, detail="Order not found")
        raise HTTPException(status_code=412, detail="Order version is stale")

    session.commit()
    updated = session.get(Order, order_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Order not found")
    response.headers["ETag"] = _etag(updated)
    return OrderRead.model_validate(updated)
