import random

from openpyxl import Workbook

random.seed(42)

# Cria a pasta de trabalho Excel
wb = Workbook()
# Remove a aba padrão inicial
import os

os.makedirs("tests/fixtures", exist_ok=True)

products = [
    {
        "sku": "PROD-001",
        "name": "Teclado Mecânico RGB",
        "cost": 120.00,
        "base_price": 250.00,
    },
    {
        "sku": "PROD-002",
        "name": "Mouse Gamer Wireless",
        "cost": 80.00,
        "base_price": 180.00,
    },
    {
        "sku": "PROD-003",
        "name": "Monitor UltraWide 29",
        "cost": 750.00,
        "base_price": 1200.00,
    },
    {
        "sku": "PROD-004",
        "name": "Cadeira Ergonômica",
        "cost": 450.00,
        "base_price": 890.00,
    },
    {
        "sku": "PROD-005",
        "name": "Headset 7.1 Surround",
        "cost": 150.00,
        "base_price": 320.00,
    },
]

for prod in products:
    ws = wb.create_sheet(title=prod["sku"])
    # Cabeçalho
    ws.append(["sku", "name", "cost_price", "competitor_price"])

    # 300 linhas de preços por produto
    for _ in range(300):
        if random.random() < 0.95:
            price = round(prod["base_price"] * (1 + random.uniform(-0.20, 0.20)), 2)
        else:
            price = round(prod["base_price"] * random.choice([0.1, 3.5]), 2)

        ws.append([prod["sku"], prod["name"], prod["cost"], price])

wb.save("tests/fixtures/precos_concorrentes.xlsx")
print("Planilha 'tests/fixtures/precos_concorrentes.xlsx' gerada com sucesso!")
