from decimal import Decimal

import pandas as pd


class ExcelRepository:
    def __init__(self, file_path: str = "tests/fixtures/motor_precos_fixtures.xlsx"):
        self.file_path = file_path

    def get_product_by_sku(self, sku: str) -> dict | None:
        df_produtos = pd.read_excel(self.file_path, sheet_name="produtos")
        product = df_produtos[df_produtos["sku"] == sku]
        if product.empty:
            return None
        row = product.iloc[0]
        return {
            "sku": str(row["sku"]),
            "nome": str(row["nome"]),
            "custo_base": Decimal(str(row["custo_base"])),
            "margem_minima": Decimal(str(row["margem_minima"])),
        }

    def get_competitor_prices(self, sku: str) -> list[Decimal]:
        df_conc = pd.read_excel(self.file_path, sheet_name="concorrentes")
        prices = df_conc[df_conc["sku"] == sku]["preco_concorrente"].tolist()
        return [Decimal(str(p)) for p in prices]
