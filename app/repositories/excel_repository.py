from collections.abc import Generator
from decimal import Decimal

from openpyxl import load_workbook

from app.schemas.product import PricingRequest, ProductBase


class ExcelPricingRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_pricing_requests(self) -> Generator[PricingRequest, None, None]:
        wb = load_workbook(filename=self.file_path, data_only=True, read_only=True)

        ignored_sheets = ["sheet", "indice", "dashboard", "resumo", "menu"]

        for sheet_name in wb.sheetnames:
            # Pula abas vazias ou apenas com cabeçalho
            if sheet_name.lower() in ignored_sheets:
                continue

            ws = wb[sheet_name]
            rows_iter = ws.iter_rows(values_only=True)

            # Pula a primeira linha (cabeçalho)
            try:
                _ = next(rows_iter)
            except StopIteration:
                continue

            # Extrai os dados do produto e preços dos concorrentes na primeira linha de dados (segunda linha da planilha)
            try:
                first_row = next(rows_iter)
            except StopIteration:
                continue

            if (
                not first_row
                or first_row[0] is None
                or first_row[1] is None
                or first_row[2] is None
            ):
                continue  # Pula linhas incompletas

            product = ProductBase(
                sku=str(first_row[0]),
                name=str(first_row[1]),
                cost_price=Decimal(str(first_row[2])),
            )

            competitor_prices: list[Decimal] = []
            if len(first_row) > 3 and first_row[3:] is not None:
                competitor_prices.append(Decimal(str(first_row[3])))

            for row in rows_iter:
                if len(row) > 3 and row[3] is not None:
                    competitor_prices.append(Decimal(str(row[3])))

            yield PricingRequest(
                product=product,
                desired_margin=Decimal("0.25"),
                min_margin=Decimal("0.10"),
                marketplace_tax=Decimal("0.12"),
                competitor_prices=competitor_prices,
            )
        wb.close()
