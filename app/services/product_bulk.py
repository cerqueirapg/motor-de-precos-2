from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_models import (
    ProductModel,  # Ajuste conforme o nome do seu Model SQLAlchemy
)


async def bulk_insert_products(
    db: AsyncSession, products_data: list[dict[str, Any]]
) -> int:
    """Realiza a inserção em lote (bulk insert) de produtos no banco de dados."""
    if not products_data:
        return 0

    db.add_all([ProductModel(**data) for data in products_data])
    await db.commit()
    return len(products_data)
