from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    sku: str = Field(..., description="Código identificador do produto")
    name: str = Field(..., description="Nome do produto")
    cost_price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Custo de aquisição do produto (ex: 50.00)",
    )


class PricingRequest(BaseModel):
    product: ProductBase
    desired_margin: Decimal = Field(
        ...,
        ge=0,
        lt=1,
        decimal_places=4,
        description="Margem de lucro desejada (ex: 0.20 para 20%)",
    )
    min_margin: Decimal = Field(
        ...,
        ge=0,
        lt=1,
        decimal_places=4,
        description="Margem de lucro mínima aceitável",
    )
    marketplace_tax: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        lt=1,
        decimal_places=4,
        description="Taxa da plataforma (ex: 0.12 para 12%)",
    )
    competitor_prices: list[Decimal] = Field(
        default_factory=list, description="Lista de preços da concorrência"
    )

    @field_validator("min_margin")
    @classmethod
    def validate_min_margin(cls, v: Decimal, info) -> Decimal:
        """Garante que a margem mínima não seja maior que a margem desejada."""
        desired = info.data.get("desired_margin")
        if desired is not None and v > desired:
            raise ValueError(
                "A margem mínima não pode ser maior que a margem desejada."
            )
        return v


class PricingResponse(BaseModel):
    sku: str
    suggested_price: Decimal = Field(
        ..., decimal_places=2, description="Preço sugerido para venda"
    )
    effective_margin: Decimal = Field(
        ...,
        decimal_places=4,
        description="Margem de lucro efetiva com base no preço sugerido",
    )
    adjusted_competitor_avg: Decimal = Field(
        ..., decimal_places=2, description="Média ajustada dos preços da concorrência"
    )
    viability_status: str = Field(
        ..., description="Status de viabilidade do preço sugerido"
    )
    alerts: list[str] = Field(..., description="Alertas relacionados ao preço sugerido")
