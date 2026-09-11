import statistics
from decimal import ROUND_HALF_UP, Decimal

from app.schemas.product import PricingRequest, PricingResponse


class PriceCalculatorService:
    ONE = Decimal("1.0")
    ZERO = Decimal("0.0")
    SAFE_DIVISOR_MIN = Decimal("0.01")
    PRECISION_MONEY = Decimal("0.01")
    PRECISION_PERCENT = Decimal("0.0001")

    @classmethod
    def _round_money(cls, value: Decimal) -> Decimal:
        """Arredonda moeda para 2 casas decimais (ROUND_HALF_UP)."""
        return value.quantize(cls.PRECISION_MONEY, rounding=ROUND_HALF_UP)

    @classmethod
    def _round_margin(cls, value: Decimal) -> Decimal:
        """Arredonda margem para 4 casas decimais."""
        return value.quantize(cls.PRECISION_PERCENT, rounding=ROUND_HALF_UP)

    @classmethod
    def filter_outliers_iqr(cls, prices: list[Decimal]) -> Decimal:
        """Filtra discrepâncias de mercado via Intervalo Interquartil (IQR)."""
        if not prices:
            return cls.ZERO

        prices_sorted = sorted(prices)
        n = len(prices_sorted)

        if n < 4:
            return cls._round_money(sum(prices_sorted) / Decimal(str(n)))

        # Conversão temporária para quantiles do módulo statistics
        float_prices = [float(p) for p in prices_sorted]
        q1_f, _, q3_f = statistics.quantiles(float_prices, n=4)

        q1 = Decimal(str(q1_f))
        q3 = Decimal(str(q3_f))
        iqr = q3 - q1

        lower_bound = q1 - (Decimal("1.5") * iqr)
        upper_bound = q3 + (Decimal("1.5") * iqr)

        valid_prices = [p for p in prices_sorted if lower_bound <= p <= upper_bound]

        if not valid_prices:
            valid_prices = prices_sorted

        avg_price = sum(valid_prices) / Decimal(str(len(valid_prices)))
        return cls._round_money(avg_price)

    @classmethod
    def calculate_price(cls, request: PricingRequest) -> PricingResponse:
        alerts: list[str] = []
        cost = request.product.cost_price

        # 1. Média ajustada dos concorrentes sem outliers
        avg_competitor = cls.filter_outliers_iqr(request.competitor_prices)

        # 2. Preço Alvo Ideal: Custo / (1 - (Margem Desejada + Taxa Marketplace))
        total_deductions = request.desired_margin + request.marketplace_tax
        ideal_divisor = cls.ONE - total_deductions

        if ideal_divisor <= cls.ZERO:
            ideal_divisor = cls.SAFE_DIVISOR_MIN
            alerts.append("Margem desejada + taxa excedem o limite operacional.")

        target_price = cost / ideal_divisor
        effective_margin = request.desired_margin
        status = "excelente"

        # 3. Análise do Teto Competitivo (+15% acima da média de mercado)
        market_ceiling = (
            cls._round_money(avg_competitor * Decimal("1.15"))
            if avg_competitor > cls.ZERO
            else target_price
        )

        if target_price > market_ceiling:
            adjusted_price = market_ceiling

            # Recalcula a nova margem se forçar o preço para o teto do mercado
            # Fórmula da margem: 1 - (Custo / Preço) - Taxas
            new_margin = cls.ONE - (cost / adjusted_price) - request.marketplace_tax

            if new_margin < request.min_margin:
                # Viola o piso de segurança: Aplica a margem mínima permitida
                min_divisor = cls.ONE - (request.min_margin + request.marketplace_tax)
                safe_divisor = (
                    min_divisor if min_divisor > cls.ZERO else cls.SAFE_DIVISOR_MIN
                )

                target_price = cost / safe_divisor
                effective_margin = request.min_margin
                status = "incompetitivo"
                alerts.append(
                    "Preço acima do mercado. Não foi possível baixar sem violar a margem mínima."
                )
            else:
                target_price = adjusted_price
                effective_margin = new_margin
                status = "competitivo_ajustado"
                alerts.append("Preço ajustado para o teto competitivo do mercado.")

        return PricingResponse(
            sku=request.product.sku,
            suggested_price=cls._round_money(target_price),
            effective_margin=cls._round_margin(effective_margin),
            adjusted_competitor_avg=avg_competitor,
            viability_status=status,
            alerts=alerts,
        )
