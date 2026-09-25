import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import pricing, upload

app = FastAPI(
    title="Motor de Preços 2.0",
    description="Engine de precificação inteligente baseada em dados de concorrentes e margens de segurança.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Registra os roteadores da API PRIMEIRO (Garante prioridade sobre os estáticos)
app.include_router(pricing.router, prefix="/api/pricing", tags=["Pricing"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

# 2. Servir a página principal do Frontend explicitamente na raiz
frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "API do Motor de Preços 2.0 ativa. Frontend não encontrado."}


# 3. Monta os arquivos estáticos (CSS, JS) após a definição das rotas de API
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path), name="frontend")
