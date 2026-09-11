from decimal import Decimal

from app.schemas.product import PricingRequest, ProductBase
from app.services.calculator import PriceCalculatorService


def test_calculate_price_ideal_scenario():
    product = ProductBase(
        sku="TECL-001", name="Teclado Mecânico", cost_price=Decimal("100.00")
    )
    request = PricingRequest(
        product=product,
        desired_margin=Decimal("0.20"),
        min_margin=Decimal("0.10"),
        marketplace_tax=Decimal("0.10"),
        competitor_prices=[Decimal("150.00"), Decimal("155.00"), Decimal("148.00")],
    )

    response = PriceCalculatorService.calculate_price(request)

    assert response.suggested_price == Decimal("142.86")
    assert response.viability_status == "excelente"
    assert len(response.alerts) == 0


def test_calculate_price_competitor_outlier_filtering():
    prices = [
        Decimal("98.00"),
        Decimal("99.00"),
        Decimal("100.00"),
        Decimal("101.00"),
        Decimal("102.00"),
        Decimal("103.00"),
        Decimal("500.00"),  # Outlier
    ]
    avg = PriceCalculatorService.filter_outliers_iqr(prices)

    assert avg < Decimal("110.00")
