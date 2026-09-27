import io

import pandas as pd


def generate_pricing_excel_report(relatorio_data: list) -> io.BytesIO:
    # Transforma os dicionários do relatório em um DataFrame
    df = pd.DataFrame(relatorio_data)

    # Renomeia as colunas para exibição profissional
    columns_map = {
        "sku": "SKU",
        "nome": "Produto",
        "custo_base": "Custo Base (R$)",
        "menor_concorrente": "Menor Concorrente (R$)",
        "preco_sugerido": "Preço Sugerido (R$)",
        "margem_minima": "Margem Mínima",
    }
    df = df.rename(columns=columns_map)

    # Ordenação opcional por SKU
    if "SKU" in df.columns:
        df = df.sort_values(by="SKU")

    target_stream = io.BytesIO()

    # Escreve o DataFrame para um stream de memória usando OpenPyXL
    with pd.ExcelWriter(target_stream, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Relatório", index=False)

    target_stream.seek(0)
    return target_stream
