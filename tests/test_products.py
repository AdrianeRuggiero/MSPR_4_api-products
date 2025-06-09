from fastapi.testclient import TestClient
from app.main import app
from app.security.auth import create_access_token

client = TestClient(app)

def get_auth_headers(role="admin"):
    token = create_access_token({"sub": "tester", "role": role})
    return {"Authorization": f"Bearer {token}"}

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

def test_get_product_by_id():
    payload = {
        "name": "Test ID",
        "price": 2.99
    }
    create_resp = client.post("/products/", json=payload, headers=get_auth_headers())
    product_id = create_resp.json()["_id"]

    get_resp = client.get(f"/products/{product_id}", headers=get_auth_headers())
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test ID"

def test_update_product():
    payload = {"name": "Old Product", "price": 4.99}
    create_resp = client.post("/products/", json=payload, headers=get_auth_headers())
    product_id = create_resp.json()["_id"]

    updated = {"name": "New Product", "price": 7.99, "in_stock": False}
    update_resp = client.put(f"/products/{product_id}", json=updated, headers=get_auth_headers())
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Product"

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
