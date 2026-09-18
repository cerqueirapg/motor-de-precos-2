import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_models import PricingHistoryModel


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_calculation(
        self,
        tenant_id: uuid.UUID | str,
        product_id: uuid.UUID | str,
        price: Decimal,
        margin: Decimal,
        status: str,
        applied_iqr: bool,
    ) -> PricingHistoryModel:
        tenant_uuid = (
            uuid.UUID(str(tenant_id)) if isinstance(tenant_id, str) else tenant_id
        )
        product_uuid = (
            uuid.UUID(str(product_id)) if isinstance(product_id, str) else product_id
        )

        history = PricingHistoryModel(
            tenant_id=tenant_uuid,
            product_id=product_uuid,
            calculated_price=price,
            effective_margin=margin,
            status=status,
            applied_iqr_filter=applied_iqr,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
