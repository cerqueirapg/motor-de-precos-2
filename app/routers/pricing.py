from fastapi import APIRouter, HTTPException, status

from app.schemas.product import PricingRequest, PricingResponse
from app.services.calculator import PriceCalculatorService

router = APIRouter(prefix="/api/v1/pricing", tags=["Pricing"])


@router.post(
    "/calculate",
    response_model=PricingResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula o preço sugerido do produto",
    description="Aplica regras de margem desejada, margem mínima, taxas de marketplace e filtro estatístico (IQR) sobre a concorrência.",
)
def calculate_price(request: PricingRequest) -> PricingResponse:
    try:
        return PriceCalculatorService.calculate_price(request)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
