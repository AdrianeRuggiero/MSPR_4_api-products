from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.security.auth import create_access_token, verify_token
import app.messaging.rabbitmq as rabbitmq

client = TestClient(app)

def get_auth_headers(role="admin"):
    token = create_access_token({"sub": "tester", "role": role})
    return {"Authorization": f"Bearer {token}"}

@patch("app.services.product_service.publish_product_created", lambda x: None)
def test_create_product():
    payload = {
        "name": "Café du Brésil",
        "description": "Torréfaction lente",
        "price": 6.49,
        "in_stock": True
    }
    response = client.post("/products/", json=payload, headers=get_auth_headers())
    assert response.status_code == 201
    assert response.json()["name"] == "Café du Brésil"

def test_list_products():
    response = client.get("/products/", headers=get_auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("app.services.product_service.publish_product_created", lambda x: None)
def test_get_product_by_id():
    payload = {"name": "Test ID", "price": 2.99}
    create_resp = client.post("/products/", json=payload, headers=get_auth_headers())
    product_id = create_resp.json()["_id"]

    get_resp = client.get(f"/products/{product_id}", headers=get_auth_headers())
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test ID"

@patch("app.services.product_service.publish_product_created", lambda x: None)
def test_update_product():
    payload = {"name": "Old Product", "price": 4.99}
    create_resp = client.post("/products/", json=payload, headers=get_auth_headers())
    product_id = create_resp.json()["_id"]

    updated = {"name": "New Product", "price": 7.99, "in_stock": False}
    update_resp = client.put(f"/products/{product_id}", json=updated, headers=get_auth_headers())
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Product"

@patch("app.services.product_service.publish_product_created", lambda x: None)
def test_delete_product():
    payload = {"name": "ToDelete", "price": 1.99}
    create_resp = client.post("/products/", json=payload, headers=get_auth_headers())
    product_id = create_resp.json()["_id"]

    delete_resp = client.delete(f"/products/{product_id}", headers=get_auth_headers())
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/products/{product_id}", headers=get_auth_headers())
    assert get_resp.status_code == 404

def test_unauthorized_access():
    response = client.get("/products/")
    assert response.status_code == 401

def test_forbidden_access():
    token = create_access_token({"sub": "user", "role": "user"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 403

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200

def test_token_generation():
    response = client.post(
        "/token",
        data={"username": "admin", "password": "any"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_token():
    invalid_token = "invalid.token.structure"
    payload = verify_token(invalid_token)
    assert payload is None

def test_get_product_by_id_not_found():
    response = client.get("/products/000000000000000000000000", headers=get_auth_headers())
    assert response.status_code == 404

def test_update_product_not_found():
    response = client.put(
        "/products/000000000000000000000000",
        json={"name": "Updated", "price": 10.0},
        headers=get_auth_headers()
    )
    assert response.status_code == 404

def test_delete_product_not_found():
    response = client.delete("/products/000000000000000000000000", headers=get_auth_headers())
    assert response.status_code == 404

def test_publish_product_created():
    mock_channel = MagicMock()
    with patch("app.messaging.rabbitmq.get_channel", return_value=mock_channel):
        rabbitmq.publish_product_created({"name": "Test", "price": 1.0})
        mock_channel.basic_publish.assert_called_once()
        mock_channel.close.assert_called_once()

def test_publish_product_created_mocked_channel():
    mock_channel = MagicMock()
    with patch("app.messaging.rabbitmq.get_channel", return_value=mock_channel):
        product_data = {"name": "Mock Product", "price": 9.99}
        rabbitmq.publish_product_created(product_data)

        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='product_created',
            body='{"name": "Mock Product", "price": 9.99}',
            properties=rabbitmq.pika.BasicProperties(delivery_mode=2),
        )
        mock_channel.close.assert_called_once()

def test_get_channel_connection():
    with patch("app.messaging.rabbitmq.pika.BlockingConnection") as mock_conn:
        mock_channel = MagicMock()
        mock_conn.return_value.channel.return_value = mock_channel

        channel = rabbitmq.get_channel()
        assert channel == mock_channel
        mock_channel.queue_declare.assert_called_once_with(queue='product_created', durable=True)