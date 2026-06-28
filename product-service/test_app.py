# product-service/test_app.py
# Run with: pytest -v
# Uses Flask's built-in test client — no real HTTP server needed

import pytest
from app import app   # Import the Flask app object


@pytest.fixture
def client():
    """Create a test client for each test."""
    app.config['TESTING'] = True   # Enables error propagation in tests
    with app.test_client() as client:
        yield client               # Provide client to each test, then clean up


# ── Test: GET /products ────────────────────────────────────────────────────────

def test_get_products_returns_200(client):
    """GET /products should return HTTP 200."""
    res = client.get('/products')
    assert res.status_code == 200

def test_get_products_returns_list(client):
    """GET /products should return a JSON array with at least one item."""
    res  = client.get('/products')
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_product_has_required_fields(client):
    """Each product must have id, name, and price."""
    res     = client.get('/products')
    product = res.get_json()[0]
    assert 'id'    in product
    assert 'name'  in product
    assert 'price' in product

def test_product_price_is_numeric(client):
    """Price should be a number (int or float)."""
    res     = client.get('/products')
    product = res.get_json()[0]
    assert isinstance(product['price'], (int, float))


# ── Test: GET /health ──────────────────────────────────────────────────────────

def test_health_returns_ok(client):
    """GET /health should return { status: 'ok' }."""
    res  = client.get('/health')
    data = res.get_json()
    assert res.status_code == 200
    assert data['status'] == 'ok'


# ── Test: 404 for unknown routes ───────────────────────────────────────────────

def test_unknown_route_returns_404(client):
    """Unknown routes should return 404."""
    res = client.get('/this-does-not-exist')
    assert res.status_code == 404
