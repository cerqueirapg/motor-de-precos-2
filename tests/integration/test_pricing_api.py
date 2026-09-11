from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calculate_pricing_endpoint_success():
    payload = {
        "product": {"sku": "MOUSE-001", "name": "Mouse Gamer", "cost_price": "50.00"},
        "desired_margin": "0.20",
        "min_margin": "0.10",
        "marketplace_tax": "0.10",
        "competitor_prices": ["80.00", "85.00", "82.00"],
    }

    response = client.post("/api/v1/pricing/calculate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "MOUSE-001"
    assert data["suggested_price"] == "71.43"
    assert data["viability_status"] == "excelente"


def test_calculate_pricing_endpoint_validation_error():
    # Envia custo inválido (<= 0) para disparar erro de validação do Pydantic
    payload = {
        "product": {
            "sku": "INVALID-001",
            "name": "Produto Sem Custo",
            "cost_price": "-10.00",
        },
        "desired_margin": "0.20",
        "min_margin": "0.10",
    }

    response = client.post("/api/v1/pricing/calculate", json=payload)

    assert response.status_code == 422  # Unprocessable Entity


def test_calculate_pricing_endpoint_value_error():
    # Simula um ValueError disparado pelo serviço para testar o tratamento do router (400 Bad Request)
    payload = {
        "product": {"sku": "MOCK-001", "name": "Produto Mock", "cost_price": "100.00"},
        "desired_margin": "0.20",
        "min_margin": "0.10",
    }

    with patch(
        "app.services.calculator.PriceCalculatorService.calculate_price",
        side_effect=ValueError("Parâmetro de cálculo incorreto"),
    ):
        response = client.post("/api/v1/pricing/calculate", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Parâmetro de cálculo incorreto"
