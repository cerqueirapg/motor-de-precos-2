from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.product import PricingRequest, ProductBase


def test_product_base_creation():
    product = ProductBase(
        sku="CAM-001",
        name="Camiseta Tech",
        cost_price=Decimal("100.00"),
    )
    assert product.sku == "CAM-001"
    assert product.cost_price == Decimal("100.00")


def test_pricing_request_validation():
    product = ProductBase(
        sku="NOTE-001",
        name="Notebook",
        cost_price=Decimal("2500.00"),
    )
    request = PricingRequest(
        product=product,
        desired_margin=Decimal("0.20"),
        min_margin=Decimal("0.10"),
        marketplace_tax=Decimal("0.12"),
        competitor_prices=[Decimal("3000.00"), Decimal("3200.00")],
    )
    assert request.desired_margin == Decimal("0.20")
    assert request.marketplace_tax == Decimal("0.12")
    assert len(request.competitor_prices) == 2


def test_product_invalid_price():
    with pytest.raises(ValidationError):
        ProductBase(
            sku="INV-001",
            name="Produto Inválido",
            cost_price=Decimal("-10.00"),  # Custo deve ser > 0
        )
