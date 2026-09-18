from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.product_repository import ProductRepository


def get_product_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductRepository:
    return ProductRepository(db=db)


ProductRepoDep = Annotated[ProductRepository, Depends(get_product_repository)]
