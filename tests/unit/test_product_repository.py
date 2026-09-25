from decimal import Decimal
from unittest.mock import MagicMock

from app.models.domain_models import Product
from app.repositories.product_repository import ProductRepository


def test_get_by_sku_success():
    # 1. Arrange: Cria um mock do ExcelRepository
    mock_excel_repo = MagicMock()
    mock_excel_repo.get_product_by_sku.return_value = {
        "sku": "SKU001",
        "nome": "A Morte de Ivan Ilitch",
        "custo_base": "13.90",
        "margem_minima": "0.05",
    }

    repo = ProductRepository(excel_repo=mock_excel_repo)

    # 2. Act: Busca o produto pelo SKU
    product = repo.get_by_sku("SKU001")

    # 3. Assert: Valida se a conversão para Dataclass correu perfeitamente
    assert product is not None
    assert isinstance(product, Product)
    assert product.sku == "SKU001"
    assert product.name == "A Morte de Ivan Ilitch"
    assert product.cost_price == Decimal("13.90")
    assert product.min_margin == Decimal("0.05")
    mock_excel_repo.get_product_by_sku.assert_called_once_with("SKU001")
