from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import ki_serverentwicklung.app as app_module
from ki_serverentwicklung.app import create_app
from ki_serverentwicklung.database import get_session
from ki_serverentwicklung.models import Base, Customer, Order


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        session.add_all(
            [
                Customer(id=1, email="one@example.com", name="One"),
                Customer(id=2, email="two@example.com", name="Two"),
                Order(
                    id=10,
                    customer_id=1,
                    ordered_at=datetime(2025, 1, 1, tzinfo=UTC),
                    status="open",
                    total_cents=100,
                    version=1,
                ),
            ]
        )
        session.commit()

    app = create_app(migrate=False)

    def override_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client, engine
    engine.dispose()


def test_startup_migration_adds_order_version_column(monkeypatch):
    connection = MagicMock()
    transaction = MagicMock()
    transaction.__enter__.return_value = connection
    transaction.__exit__.return_value = False
    fake_engine = MagicMock()
    fake_engine.dialect.name = "postgresql"
    fake_engine.begin.return_value = transaction
    monkeypatch.setattr(app_module, "engine", fake_engine)

    with TestClient(create_app()) as _client:
        pass

    statement = connection.execute.call_args.args[0]
    assert "ALTER TABLE orders ADD COLUMN IF NOT EXISTS version" in str(statement)


def test_list_orders_and_missing_customer(client):
    test_client, _ = client
    response = test_client.get("/customers/1/orders")
    assert response.status_code == 200
    assert [order["id"] for order in response.json()] == [10]
    assert test_client.get("/customers/999/orders").status_code == 404


def test_get_order_and_conditional_get(client):
    test_client, _ = client
    response = test_client.get("/orders/10")
    assert response.status_code == 200
    assert response.headers["etag"] == '"order-10-v1"'
    conditional = test_client.get(
        "/orders/10", headers={"If-None-Match": response.headers["etag"]}
    )
    assert conditional.status_code == 304
    assert conditional.content == b""
    wildcard = test_client.get("/orders/10", headers={"If-None-Match": "*"})
    assert wildcard.status_code == 304
    weak_match = test_client.get(
        "/orders/10", headers={"If-None-Match": 'W/"order-10-v1"'}
    )
    assert weak_match.status_code == 304
    assert test_client.get("/orders/999").status_code == 404


def test_create_valid_invalid_and_unknown_fields(client):
    test_client, _ = client
    created = test_client.post(
        "/customers/2/orders", json={"status": "open", "total_cents": 25}
    )
    assert created.status_code == 201
    assert created.headers["location"] == f"/orders/{created.json()['id']}"
    assert created.headers["etag"] == f'"order-{created.json()["id"]}-v1"'
    assert (
        test_client.post(
            "/customers/2/orders", json={"status": "", "total_cents": 25}
        ).status_code
        == 422
    )
    assert (
        test_client.post(
            "/customers/2/orders",
            json={"status": "open", "total_cents": 25, "unexpected": True},
        ).status_code
        == 422
    )
    assert (
        test_client.post(
            "/customers/999/orders", json={"status": "open", "total_cents": 25}
        ).status_code
        == 404
    )


def test_update_requires_matching_etag_and_is_atomic(client):
    test_client, engine = client
    body = {"status": "shipped", "total_cents": 200}
    assert test_client.put("/orders/10", json=body).status_code == 428

    updated = test_client.put(
        "/orders/10", json=body, headers={"If-Match": '"order-10-v1"'}
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert updated.headers["etag"] == '"order-10-v2"'

    stale = test_client.put(
        "/orders/10",
        json={"status": "lost", "total_cents": 0},
        headers={"If-Match": '"order-10-v1"'},
    )
    assert stale.status_code == 412
    with Session(engine) as session:
        order = session.get(Order, 10)
        assert order is not None
        assert (order.status, order.total_cents, order.version) == ("shipped", 200, 2)


@pytest.mark.parametrize(
    "if_match",
    [
        'W/"order-10-v1"',
        "*",
        "malformed",
        '"order-10-v1", malformed',
    ],
)
def test_update_requires_a_strong_single_version_tag(client, if_match):
    test_client, engine = client
    response = test_client.put(
        "/orders/10",
        json={"status": "shipped", "total_cents": 200},
        headers={"If-Match": if_match},
    )
    assert response.status_code == 412
    with Session(engine) as session:
        order = session.get(Order, 10)
        assert order is not None
        assert (order.status, order.total_cents, order.version) == ("open", 100, 1)


def test_update_accepts_matching_strong_tag_from_list(client):
    test_client, _ = client
    response = test_client.put(
        "/orders/10",
        json={"status": "shipped", "total_cents": 200},
        headers={"If-Match": '"order-10-v0", "order-10-v1"'},
    )
    assert response.status_code == 200
    assert response.json()["version"] == 2


def test_update_rejects_list_without_matching_strong_tag(client):
    test_client, _ = client
    response = test_client.put(
        "/orders/10",
        json={"status": "shipped", "total_cents": 200},
        headers={"If-Match": '"order-10-v0", W/"order-10-v1"'},
    )
    assert response.status_code == 412


def test_update_rejects_mismatched_order_id_and_invalid_body(client):
    test_client, _ = client
    assert (
        test_client.put(
            "/orders/10",
            json={"status": "open", "total_cents": -1},
            headers={"If-Match": '"order-10-v1"'},
        ).status_code
        == 422
    )
    assert (
        test_client.put(
            "/orders/10",
            json={"status": "open", "total_cents": 1},
            headers={"If-Match": '"order-11-v1"'},
        ).status_code
        == 412
    )
    assert (
        test_client.put(
            "/orders/999",
            json={"status": "open", "total_cents": 1},
            headers={"If-Match": '"order-999-v1"'},
        ).status_code
        == 404
    )
