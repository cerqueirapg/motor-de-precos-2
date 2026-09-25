import time
from typing import Any, cast

import pandas as pd

from app.repositories.excel_repository import ExcelRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import PricingRequest
from app.services.calculator import PriceCalculatorService


def main():
    start_time = time.time()

    # Caminho do arquivo preenchido pelo cliente
    caminho_planilha = "scripts/motor_precos_template.xlsx"

    # 1. Lê a lista de SKUs da aba de produtos
    df_produtos = pd.read_excel(caminho_planilha, sheet_name="produtos")
    lista_skus = df_produtos["sku"].dropna().tolist()

    # 2. Instancia repositórios e serviço
    excel_repo = ExcelRepository(file_path=caminho_planilha)
    product_repo = ProductRepository(excel_repo=excel_repo)
    calculator = PriceCalculatorService()

    print(f"--- PROCESSANDO {len(lista_skus)} PRODUTOS DA PLANILHA DO CLIENTE ---")

    for sku in lista_skus:
        produto = product_repo.get_by_sku(sku)

        if not produto:
            print(f"\n[AVISO] SKU {sku} não foi retornado pelo ProductRepository.")
            continue

        precos_concorrentes = excel_repo.get_competitor_prices(sku)

        # Converte o objeto de produto em dicionário para compatibilidade total com o Pydantic
        produto_dict = produto.__dict__ if hasattr(produto, "__dict__") else produto

        # Prepara a requisição
        request_data = PricingRequest(
            product=cast(Any, produto_dict),
            min_margin=produto.min_margin,
            desired_margin=getattr(produto, "desired_margin", None)
            or produto.min_margin,
            competitor_prices=precos_concorrentes,
        )

        resultado = calculator.calculate_price(request=request_data)

        # Inspeciona o objeto de retorno para capturar o preço correto ou o dicionário retornado
        if isinstance(resultado, dict):
            preco_sugerido = (
                resultado.get("recommended_price")
                or resultado.get("suggested_price")
                or resultado.get("price")
            )
        else:
            preco_sugerido = (
                getattr(resultado, "recommended_price", None)
                or getattr(resultado, "suggested_price", None)
                or getattr(resultado, "price", None)
                or getattr(resultado, "calculated_price", None)
            )

        menor_conc = min(precos_concorrentes) if precos_concorrentes else "N/A"

        print(f"\nSKU: {sku} | {produto.name}")
        print(f"  - Custo Base: R$ {produto.cost_price:.2f}")
        print(f"  - Menor Concorrente: R$ {menor_conc}")
        print(f"  - Preço Sugerido pelo Motor: R$ {preco_sugerido}")

    elapsed_time = time.time() - start_time
    print(f"\nProcessamento concluído com sucesso em {elapsed_time:.2f}s!")


if __name__ == "__main__":
    main()
