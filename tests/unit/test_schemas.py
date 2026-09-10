from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.product import PricingRequest, ProductBase


def test_product_base_creation():
    product = ProductBase(
        name="Camiseta Tech",
        sku="CAM-001",
        base_price=Decimal("100.00"),
        category="Vestuário",
    )
    assert product.sku == "CAM-001"
    assert product.base_price == Decimal("100.00")


def test_pricing_request_validation():
    product = ProductBase(
        name="Notebook",
        sku="NOTE-001",
        base_price=Decimal("3500.00"),
        category="Eletrônicos",
    )
    request = PricingRequest(
        product=product,
        discount_percentage=Decimal("10.0"),
        tax_percentage=Decimal("5.0"),
    )
    assert request.discount_percentage == Decimal("10.0")
    assert request.tax_percentage == Decimal("5.0")


def test_product_invalid_price():
    with pytest.raises(ValidationError):
        ProductBase(
            name="Produto Inválido",
            sku="INV-001",
            base_price=Decimal("-10.00"),  # Preço não pode ser <=
            category="Geral",
        )
