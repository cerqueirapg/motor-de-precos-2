# 🚀 Motor de Preços 2.0

API e aplicação web para cálculo dinâmico de preços, parsing e processamento em lote de planilhas Excel, e geração de relatórios dinâmicos (`.xlsx` e `.docx`).

---

## 📌 Visão Geral do Projeto

O **Motor de Preços 2.0** foi construído utilizando **FastAPI** e uma arquitetura em camadas bem definida (Clean Architecture / Layered Architecture). O sistema permite:
- **Cálculo em Tempo Real:** Processamento de regras de precificação via endpoints HTTP.
- **Processamento em Lote:** Importação, validação e interpretação de planilhas Excel (`.xlsx`).
- **Geração de Documentos:** Exportação automática de relatórios formatados em Word (`.docx`) e Excel (`.xlsx`).
- **Interface Web Simples (Frontend):** Dashboard estático (`HTML/JS/CSS`) para interação direta com os serviços.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.14+
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/)
- **Testes:** [pytest](https://docs.pytest.org/)
- **Manipulação de Planilhas/Dados:** `openpyxl`, `pandas`
- **Geração de Documentos:** `python-docx`
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

---

## 🌐 Frontend
A interface web para testes interativos e manipulação de uploads fica localizada no diretório frontend/. Ela comunica-se diretamente com os endpoints da API para enviar planilhas Excel e visualizar cálculos de preços em tempo real.

---

## 📂 Estrutura do Projeto

```text
motor-de-precos-2/
├── app/
│   ├── core/
│   │   └── config.py             # Configurações globais da aplicação
│   ├── models/
│   │   └── domain_models.py      # Modelos de domínio (Pydantic / Entidades)
│   ├── repositories/
│   │   ├── excel_repository.py   # Manipulação e acesso aos dados de arquivos Excel
│   │   └── product_repository.py # Repositório e persistência de produtos
│   ├── routers/
│   │   ├── deps.py               # Injeção de dependências das rotas
│   │   ├── pricing.py            # Endpoints de cálculo de preços
│   │   └── upload.py             # Endpoints de upload e parsing de planilhas
│   ├── schemas/                  # Schemas de entrada e saída (DTOs)
│   ├── services/
│   │   ├── calculator.py         # Regras de negócio e motor de cálculo
│   │   ├── docx_generator.py     # Gerador de relatórios em Word (.docx)
│   │   ├── excel_generator.py    # Gerador de planilhas (.xlsx)
│   │   ├── excel_parser.py       # Leitura e parsing de planilhas enviadas
│   │   └── product_bulk.py       # Processamento em lote de produtos
│   └── main.py                   # Ponto de entrada da aplicação FastAPI
├── frontend/
│   ├── index.html                # Interface de usuário
│   ├── script.js                 # Lógica de integração com a API
│   └── styles.css                # Estilização da interface
├── scripts/
│   ├── generate_test_data.py     # Script para geração de dados fictícios
│   └── motor_precos_template.xlsx # Template base para uploads
├── tests/
│   ├── fixtures/                 # Arquivos de teste e planilhas de exemplo
│   ├── integration/              # Testes de integração (Endpoints / API)
│   │   ├── test_pricing_api.py
│   │   └── test_upload_excel.py
│   ├── unit/                     # Testes unitários de serviços e repositórios
│   │   ├── test_calculator.py
│   │   ├── test_health.py
│   │   ├── test_product_repository.py
│   │   └── test_schemas.py
│   └── conftest.py               # Configurações e fixtures globais do Pytest
├── .gitignore
├── pytest.ini                    # Configurações do ambiente de testes
├── README.md
├── requirements.txt              # Dependências do projeto
└── run_engine.py                 # Script de execução/inicialização rápida
```
---
## ⚙️ Configuração e Instalação
1. **Clonar o Repositório**
```Bash
git clone https://github.com/cerqueirapg/motor-de-precos-2.git
cd motor-de-precos-2
```

2. **Criar e Ativar o Ambiente Virtual (venv)**
```Bash
# Windows
python -m venv venv
.\venv\Scripts\activate
# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar Dependências**
```Bash
pip install -r requirements.txt
```

## 🚀 Executando a Aplicação
Você pode inicializar o servidor de duas maneiras:

* Opção 1: Via script de execução rápido
```Bash
python run_engine.py
```
* Opção 2: Via Uvicorn diretamente
```Bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa da API em:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

---

## 🧪 Executando os Testes
O projeto possui cobertura de testes unitários e de integração utilizando pytest.

* Executar todos os testes:

```Bash
pytest
```
* Executar apenas testes unitários:

```Bash
pytest tests/unit
```
* Executar apenas testes de integração:

```Bash
pytest tests/integration
```
