from decimal import Decimal
from typing import Any

from app.models.domain_models import PricingHistory, Product
from app.repositories.excel_repository import ExcelRepository


class ProductRepository:
    def __init__(self, excel_repo: ExcelRepository):
        self.excel_repo = excel_repo

    def get_by_sku(self, sku: str) -> Product | None:
        """Busca os dados do produto na planilha Excel pelo SKU."""
        product_data = self.excel_repo.get_product_by_sku(sku)
        if not product_data:
            return None
        return Product(
            sku=product_data["sku"],
            name=product_data.get("nome"),
            cost_price=Decimal(str(product_data["custo_base"])),
            min_margin=Decimal(str(product_data["margem_minima"])),
        )

    def save_calculation(
        self,
        sku: str,
        price: Decimal,
        margin: Decimal,
        status: str,
        applied_iqr: bool,
    ) -> PricingHistory:
        """Cria e retorna o registro de cálculo efetuado."""
        history = PricingHistory(
            sku=sku,
            calculated_price=price,
            effective_margin=margin,
            status=status,
            applied_iqr_filter=applied_iqr,
        )
        # Opcional: Persistir o resultado em uma nova aba ou planilha de saída
        # self.excel_repo.save_pricing_history(history)
        return history

    def bulk_create(self, products_data: list[dict[str, Any]]) -> int:
        """Processa e valida em lote os produtos vindos da planilha."""
        if not products_data:
            return 0

        count = 0
        for data in products_data:
            if "sku" in data and "custo_base" in data:
                count += 1

        return count
