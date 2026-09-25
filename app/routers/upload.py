import asyncio
import io
import os
import zipfile
from decimal import Decimal
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.repositories.excel_repository import ExcelRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import PricingRequest, ProductBase
from app.services.calculator import PriceCalculatorService

router = APIRouter(prefix="/api/v1/upload", tags=["Upload"])

TEMPLATE_PATH = os.path.join("scripts", "motor_precos_template.xlsx")


def _write_file(path: str, contents: bytes) -> None:
    with open(path, "wb") as f:
        f.write(contents)


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

    required_sheets = ["produtos", "concorrentes"]
    for sheet in required_sheets:
        if sheet not in xls.sheet_names:
            raise HTTPException(
                status_code=400,
                detail=f"Aba obrigatória ausente no arquivo: {sheet}",
            )

    temp_file_path = "temp_uploaded_motor.xlsx"
    await asyncio.to_thread(_write_file, temp_file_path, contents)

    try:
        excel_repo = ExcelRepository(file_path=temp_file_path)
        product_repo = ProductRepository(excel_repo=excel_repo)
        calculator = PriceCalculatorService()

        df_produtos = pd.read_excel(temp_file_path, sheet_name="produtos")
        lista_skus = df_produtos["sku"].dropna().tolist()

        relatorio_comparativo = []

        for sku in lista_skus:
            produto = product_repo.get_by_sku(sku)
            if not produto:
                continue

            precos_concorrentes = excel_repo.get_competitor_prices(sku)
            produto_base = ProductBase.model_validate(produto, from_attributes=True)

            request_data = PricingRequest(
                product=produto_base,
                min_margin=Decimal(str(produto.min_margin)),
                desired_margin=Decimal(str(produto.min_margin)),
                competitor_prices=[Decimal(str(p)) for p in precos_concorrentes],
            )

            resultado = calculator.calculate_price(request=request_data)

            # Captura com fallback genérico
            preco_sugerido = (
                getattr(resultado, "recommended_price", None)
                or getattr(resultado, "suggested_price", None)
                or getattr(resultado, "calculated_price", None)
                or getattr(resultado, "final_price", None)
                or getattr(resultado, "price", None)
            )

            menor_conc = min(precos_concorrentes) if precos_concorrentes else None

            relatorio_comparativo.append(
                {
                    "sku": sku,
                    "nome": produto.name,
                    "custo_base": float(produto.cost_price),
                    "menor_concorrente": float(menor_conc)
                    if menor_conc is not None
                    else None,
                    "preco_sugerido": float(preco_sugerido)
                    if preco_sugerido is not None
                    else None,
                    "margem_minima": float(produto.min_margin),
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
