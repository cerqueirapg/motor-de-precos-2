import os

import pandas as pd

TEMPLATE_PATH = os.path.join("scripts", "motor_precos_template.xlsx")


def create_template():
    os.makedirs("scripts", exist_ok=True)

    # 1. Aba 'Meus Produtos'
    df_produtos = pd.DataFrame(
        columns=["SKU", "Meus Produtos", "Custo Base", "Margem Mínima"]
    )

    # Dados de exemplo opcionais
    df_produtos.loc[0] = ["SKU001", "Produto Exemplo A", 50.00, 0.15]
    df_produtos.loc[1] = ["SKU002", "Produto Exemplo B", 120.00, 0.20]

    # 2. Aba 'Concorrentes'
    df_concorrentes = pd.DataFrame(
        columns=["SKU", "Concorrentes", "Preços Concorrentes", "Data da Coleta"]
    )
    df_concorrentes.loc[0] = ["SKU001", "Loja X", 75.90, "2026-09-26"]
    df_concorrentes.loc[1] = ["SKU001", "Loja Y", 72.00, "2026-09-26"]

    # 3. Aba 'Taxas de Marketplace'
    df_marketplaces = pd.DataFrame(
        columns=["Marketplace", "Taxa Mínima", "Outros Custos"]
    )
    df_marketplaces.loc[0] = ["Mercado Livre", 0.14, 5.00]
    df_marketplaces.loc[1] = ["Shopee", 0.12, 3.00]

    # Salva no arquivo .xlsx com as 3 abas
    with pd.ExcelWriter(TEMPLATE_PATH, engine="openpyxl") as writer:
        df_produtos.to_excel(writer, sheet_name="Meus Produtos", index=False)
        df_concorrentes.to_excel(writer, sheet_name="Concorrentes", index=False)
        df_marketplaces.to_excel(writer, sheet_name="Taxas de Marketplace", index=False)

    print(f"Modelo atualizado gerado em: {TEMPLATE_PATH}")


if __name__ == "__main__":
    create_template()
