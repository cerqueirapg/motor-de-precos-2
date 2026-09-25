import os

import pytest


@pytest.fixture
def excel_fixture_path():
    path = "tests/fixtures/motor_precos_fixtures.xlsx"
    assert os.path.exists(path), "A planilha de testes nao foi encontrada."
    return path
