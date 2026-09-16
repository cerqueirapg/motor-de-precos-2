# tests/unit/test_calculator.py
from decimal import Decimal

from app.schemas.product import PricingRequest, ProductBase
from app.services.calculator import PriceCalculatorService


def test_calculate_price_competitor_outlier_filtering():
    """Valida se o cálculo de IQR descarte o outlier 500.00."""
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

    # A média correta de (98 + 99 + 100 + 101 + 102 + 103) / 6 = 100.50
    assert avg == Decimal("100.50")


def test_calculate_price_adjusted_by_market_ceiling():
    """Valida o ajuste automático quando o preço alvo supera o teto do mercado (+15%)."""
    product = ProductBase(
        sku="MOUSE-001", name="Mouse Gamer", cost_price=Decimal("50.00")
    )
    request = PricingRequest(
        product=product,
        desired_margin=Decimal("0.30"),  # Preço alvo ideal seria 50 / 0.60 = 83.33
        min_margin=Decimal("0.15"),
        marketplace_tax=Decimal("0.10"),
        competitor_prices=[
            Decimal("60.00"),
            Decimal("65.00"),
            Decimal("70.00"),
        ],  # Média = 65.00
    )

    response = PriceCalculatorService.calculate_price(request)

    # Média concorrentes = 65.00 | Teto (+15%) = 65.00 * 1.15 = 74.75
    assert response.suggested_price == Decimal("74.75")
    assert response.viability_status == "competitivo_ajustado"
    assert "Preço ajustado para o teto competitivo do mercado." in response.alerts
