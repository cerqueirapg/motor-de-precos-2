import os
import sys
from pathlib import Path

import pytest

# Adiciona a raiz do projeto ao sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture
def excel_fixture_path():
    path = "tests/fixtures/motor_precos_fixtures.xlsx"
    assert os.path.exists(path), "A planilha de testes nao foi encontrada."
    return path
