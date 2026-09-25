import io
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/excel")
async def upload_excel(file: Annotated[UploadFile, File()]):
    # Garante verificação para tipagem e validação de extensão
    filename = file.filename or ""
    if not filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo inválido. Envie um arquivo Excel.",
        )

    contents = await file.read()
    xls = pd.ExcelFile(io.BytesIO(contents))

    # Valida as abas obrigatórias no arquivo enviado
    required_sheets = ["produtos", "concorrentes"]
    for sheet in required_sheets:
        if sheet not in xls.sheet_names:
            raise HTTPException(
                status_code=400, detail=f"Aba obrigatória ausente: {sheet}"
            )

    return {"message": "Planilha validada e carregada com sucesso!"}
