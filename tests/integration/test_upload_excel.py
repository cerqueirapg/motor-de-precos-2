from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_upload_excel_success():
    # Aponta para a nova planilha com as abas 'produtos' e 'concorrentes'
    fixture_path = Path("tests/fixtures/motor_precos_fixtures.xlsx")
    assert fixture_path.exists(), (
        "A fixture motor_precos_fixtures.xlsx não foi encontrada."
    )

    file_bytes = fixture_path.read_bytes()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/upload/excel",
            files={
                "file": (
                    "motor_precos_fixtures.xlsx",
                    file_bytes,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Planilha validada e carregada com sucesso!"}


@pytest.mark.asyncio
async def test_upload_excel_invalid_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/upload/excel",
            files={"file": ("documento.pdf", b"conteudo falso", "application/pdf")},
        )

    assert response.status_code == 400
    assert "Formato de arquivo inválido" in response.json()["detail"]
