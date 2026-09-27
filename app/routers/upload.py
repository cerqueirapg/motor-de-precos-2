import asyncio
import io
import os
import zipfile
from decimal import Decimal, InvalidOperation
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

# Ajustado o prefixo para coincidir com as chamadas do frontend
router = APIRouter(prefix="/api/upload", tags=["Upload"])

TEMPLATE_PATH = os.path.join("scripts", "motor_precos_template.xlsx")


def _write_file(path: str, contents: bytes) -> None:
    with open(path, "wb") as f:
        f.write(contents)


# Rota final: GET /api/upload/download-template
@router.get("/download-template")
def download_template():
    """Permite ao usuário baixar a planilha modelo .xlsx em 1 clique."""
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(
            status_code=404,
            detail="Planilha modelo não encontrada no servidor.",
        )

    return FileResponse(
        path=TEMPLATE_PATH,
        filename="motor_precos_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Rota final: POST /api/upload/excel
@router.post("/excel")
async def upload_excel(file: Annotated[UploadFile, File()]):
    """Recebe a planilha, valida as abas e retorna o relatório comparativo de preços."""
    filename = file.filename or ""
    if not filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo inválido. Envie um arquivo Excel.",
        )

    contents = await file.read()

    try:
        xls = pd.ExcelFile(io.BytesIO(contents))
    except (ValueError, ImportError, OSError, zipfile.BadZipFile) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao ler o arquivo Excel: {e!s}",
        )

    # Atualização dentro da função upload_excel em upload.py:

    # Validação das novas abas obrigatórias
    required_sheets = ["Meus Produtos", "Concorrentes", "Taxas de Marketplace"]
    for sheet in required_sheets:
        if sheet not in xls.sheet_names:
            raise HTTPException(
                status_code=400,
                detail=f"Aba obrigatória ausente no arquivo: '{sheet}'",
            )

    temp_file_path = "temp_uploaded_motor.xlsx"
    await asyncio.to_thread(_write_file, temp_file_path, contents)

    try:
        # Leitura com os novos nomes de abas e colunas
        df_produtos = pd.read_excel(temp_file_path, sheet_name="Meus Produtos")
        df_concorrentes = pd.read_excel(temp_file_path, sheet_name="Concorrentes")
        df_marketplaces = pd.read_excel(
            temp_file_path, sheet_name="Taxas de Marketplace"
        )

        # Normalização dos nomes de colunas (para minúsculo/sem espaços se necessário)
        df_produtos.columns = df_produtos.columns.str.strip()
        df_concorrentes.columns = df_concorrentes.columns.str.strip()
        df_marketplaces.columns = df_marketplaces.columns.str.strip()

        # Obter taxa e outros custos padrão do primeiro marketplace (ou aplicar fallback)
        taxa_mkt = Decimal(0)
        outros_custos_mkt = Decimal(0)

        if not df_marketplaces.empty:
            primeira_taxa = df_marketplaces.iloc[0]
            try:
                taxa_mkt = Decimal(str(primeira_taxa.get("Taxa Mínima", 0)))
                outros_custos_mkt = Decimal(str(primeira_taxa.get("Outros Custos", 0)))
            except (InvalidOperation, ValueError):
                pass

        # Evita duplicidade de processamento para o mesmo SKU
        lista_skus = df_produtos["SKU"].dropna().unique().tolist()
        relatorio_comparativo = []

        for sku in lista_skus:
            row_prod = df_produtos[df_produtos["SKU"] == sku].iloc[0]
            nome_produto = row_prod.get("Meus Produtos", f"SKU {sku}")

            try:
                custo_base = Decimal(str(row_prod.get("Custo Base", 0)))
                margem_minima = Decimal(str(row_prod.get("Margem Mínima", 0)))
            except (InvalidOperation, ValueError):
                custo_base = Decimal(0)
                margem_minima = Decimal(0)

            # Tratamento seguro de preços dos concorrentes. Filtra preços dos concorrentes para o SKU atual
            precos_conc_series = df_concorrentes[df_concorrentes["SKU"] == sku][
                "Preços Concorrentes"
            ].dropna()

            precos_conc_decimal = []
            for p in precos_conc_series:
                try:
                    precos_conc_decimal.append(Decimal(str(p)))
                except (InvalidOperation, ValueError):
                    continue

            menor_conc = min(precos_conc_decimal) if precos_conc_decimal else None

            # --- CÁLCULO DE PREÇO COM TAXAS DE MARKETPLACE ---
            # Preço base sem taxas
            custo_com_margem = (
                custo_base * (Decimal(1) + margem_minima) + outros_custos_mkt
            )

            # Fator divisor para cobrir a comissão percentual sobre a venda
            divisor = (
                Decimal(1) - taxa_mkt if taxa_mkt < Decimal(1) else Decimal("0.86")
            )

            preco_sugerido = (
                custo_com_margem / divisor if divisor > 0 else custo_com_margem
            )

            relatorio_comparativo.append(
                {
                    "sku": str(sku),
                    "nome": str(nome_produto),
                    "custo_base": float(custo_base),
                    "menor_concorrente": float(menor_conc)
                    if menor_conc is not None
                    else None,
                    "preco_sugerido": float(round(preco_sugerido, 2)),
                    "margem_minima": float(margem_minima),
                }
            )

        return {
            "message": "Planilha processada com sucesso!",
            "total_produtos": len(relatorio_comparativo),
            "data": relatorio_comparativo,
        }

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
