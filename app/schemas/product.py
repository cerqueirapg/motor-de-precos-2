from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(..., description="Nome do Produto")
    sku: str = Field(..., description="Código Identificador do Produto")
    base_price: Decimal = Field(..., gt=0, description="Preço base do Produto")
    category: str = Field(..., description="Categoria do Produto")


class PricingRequest(BaseModel):
    product: ProductBase
    discount_percentage: Decimal = Field(
        default=Decimal("0.0"),
        ge=Decimal("0.0"),
        le=Decimal("100.0"),
        description="Porcentagem de desconto(0 a 100).",
    )
    tax_percentage: Decimal = Field(
        default=Decimal("0.0"),
        ge=Decimal("0.0"),
        le=Decimal("100.0"),
        description="Porcentagem de impostos/tsxas (0 a 100).",
    )

    @field_validator("discount_percentage", "tax_percentage", mode="before")
    def convert_to_decimal(cls, value):
        if value is not None:
            return Decimal(str(value))
        return Decimal("0.0")


class PricingResponse(BaseModel):
    sku: str
    base_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    final_price: Decimal
