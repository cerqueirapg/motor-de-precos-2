from decimal import Decimal

from app.schemas.product import PricingRequest, ProductBase
from app.services.calculator import PriceCalculatorService


def test_calculate_price_success():
    request = PricingRequest(
        product=ProductBase(
            sku="SKU-TEST-1",
            name="Test Product",
            cost_price=Decimal("100.00"),
        ),
        competitor_prices=[
            Decimal("150.00"),
            Decimal("160.00"),
            Decimal("155.00"),
            Decimal("500.00"),  # Outlier
        ],
        desired_margin=Decimal("0.20"),
        min_margin=Decimal("0.10"),
        marketplace_tax=Decimal("0.10"),
    )

    response = PriceCalculatorService.calculate_price(request)

    assert response.sku == "SKU-TEST-1"
    assert response.suggested_price > Decimal("0.00")
    assert response.adjusted_competitor_avg < Decimal("500.00")
