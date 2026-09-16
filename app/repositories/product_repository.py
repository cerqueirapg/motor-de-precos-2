from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_models import PricingHistoryModel


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_calculation(
        self,
        tenant_id: str,
        product_id: str,
        price: Decimal,
        margin: Decimal,
        status: str,
        applied_iqr: bool,
    ) -> PricingHistoryModel:
        history = PricingHistoryModel(
            tenant_id=tenant_id,
            product_id=product_id,
            calculated_price=price,
            effective_margin=margin,
            status=status,
            applied_iqr_filter=applied_iqr,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
