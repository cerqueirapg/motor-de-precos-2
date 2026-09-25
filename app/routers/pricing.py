from fastapi import APIRouter, HTTPException, status

from app.schemas.product import PricingRequest, PricingResponse
from app.services.calculator import PriceCalculatorService

router = APIRouter(prefix="/api/v1/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PricingResponse)
async def calculate_price(payload: PricingRequest):
    try:
        return PriceCalculatorService.calculate_price(payload)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
