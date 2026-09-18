import time

from app.repositories.excel_repository import ExcelPricingRepository
from app.services.calculator import PriceCalculatorService


def main():
    repo = ExcelPricingRepository("tests/fixtures/precos_concorrentes.xlsx")
    requests = repo.get_all_pricing_requests()

    print("--- Processando produtos do Excel (modo streaming) ---\n")

    count = 0
    start_time = time.time()

    for req in requests:
        count += 1
        result = PriceCalculatorService.calculate_price(req)

        print(f"[{count}] SKU: {result.sku}")
        print(f"    Preço Sugerido: R$ {result.suggested_price}")
        print(f"    Média Concorrentes: R$ {result.adjusted_competitor_avg}")
        print(f"    Status: {result.viability_status}")
        print("-" * 45)

    elapsed_time = time.time() - start_time
    print(f"\nTotal de produtos processados: {count}")
    print(f"Tempo total: {elapsed_time:.2f}s")


if __name__ == "__main__":
    main()
