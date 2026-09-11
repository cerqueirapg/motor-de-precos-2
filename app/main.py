from fastapi import FastAPI

from app.routers import pricing

app = FastAPI(
    title="Motor de Preços 2.0",
    version="0,.1.0",
    description="API de precificação dinâmica com inteligência de mercado anãlise de margem e precisão financeira.",
)

app.include_router(pricing.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
