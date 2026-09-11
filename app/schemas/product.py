from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    sku: str = Field(..., description="Código identificador do produto")
    name: str = Field(..., description="Nome do produto")
    cost_price: Decimal = Field(..., gt=0, description="Custo de aquisição do produto")


class PricingRequest(BaseModel):
    product: ProductBase
    desired_margin: Decimal = Field(
        ..., description="Margem de lucro desejada (ex: 0.20 para 20%)"
    )
    min_margin: Decimal = Field(..., description="Margem de lucro mínima aceitável")
    marketplace_tax: Decimal = Field(
        default=Decimal("0.0"), description="Taxa da plataforma (ex: 0.12 para 12%)"
    )
    competitor_prices: list[Decimal] = Field(
        default_factory=list, description="Lista de preços da concorrência"
    )

    @field_validator("desired_margin", "min_margin", "marketplace_tax", mode="before")
    def convert_to_decimal(cls, value):
        return Decimal(str(value)) if value is not None else Decimal("0.0")


class PricingResponse(BaseModel):
    sku: str
    suggested_price: Decimal
    effective_margin: Decimal
    adjusted_competitor_avg: Decimal
    viability_status: str
    alerts: list[str]
