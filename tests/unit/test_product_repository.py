import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.domain_models import PricingHistoryModel, ProductModel, TenantModel
from app.repositories.product_repository import ProductRepository


@pytest.mark.anyio
async def test_save_calculation_success(async_session):
    # 1. Arrange: Cria Tenant e Produto para satisfazer as FKs
    tenant = TenantModel(id=uuid.uuid4(), name="Empresa Teste", active=True)
    async_session.add(tenant)
    await async_session.flush()

    product = ProductModel(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        sku="TEST-SKU-001",
        name="Produto Teste",
        cost_price=Decimal("100.00"),
        min_margin=Decimal("0.10"),
    )
    async_session.add(product)
    await async_session.commit()

    repo = ProductRepository(db=async_session)

    # 2. Act: Salva o cálculo através do repositório
    history = await repo.save_calculation(
        tenant_id=tenant.id,
        product_id=product.id,
        price=Decimal("150.00"),
        margin=Decimal("0.25"),
        status="excelente",
        applied_iqr=True,
    )

    # 3. Assert: Verifica se o objeto retornado possui os dados corretos
    assert history.id is not None
    assert history.tenant_id == tenant.id
    assert history.product_id == product.id
    assert history.calculated_price == Decimal("150.00")
    assert history.effective_margin == Decimal("0.25")
    assert history.status == "excelente"
    assert history.applied_iqr_filter is True

    # 4. Assert DB: Garante que foi persistido de fato no SQLite
    stmt = select(PricingHistoryModel).where(PricingHistoryModel.id == history.id)
    result = await async_session.execute(stmt)
    db_history = result.scalar_one_or_none()

    assert db_history is not None
