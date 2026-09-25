from typing import Annotated

from fastapi import Depends

from app.repositories.excel_repository import ExcelRepository
from app.repositories.product_repository import ProductRepository


def get_excel_repository() -> ExcelRepository:
    # Instancia o repositório de Excel (apontando para o caminho padrão da planilha)
    return ExcelRepository()


def get_product_repository(
    excel_repo: Annotated[ExcelRepository, Depends(get_excel_repository)],
) -> ProductRepository:
    # Injeta o ExcelRepository no ProductRepository se houver essa camada
    return ProductRepository(excel_repo=excel_repo)


# Alias de injeções de dependência para uso nas rotas
ExcelRepoDep = Annotated[ExcelRepository, Depends(get_excel_repository)]
ProductRepoDep = Annotated[ProductRepository, Depends(get_product_repository)]
