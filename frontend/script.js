let dadosRelatorioAtual = [];

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");
    const resultsSection = document.getElementById("resultsSection");

    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    loading.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    try {
        const response = await fetch("/api/upload/excel", {
            method: "POST",
            body: formData,
        });

        const textResponse = await response.text();
        let result;

        try {
            result = JSON.parse(textResponse);
        } catch (jsonErr) {
            throw new Error(
                `Resposta inválida do servidor (Status ${response.status}). Conteúdo: "${textResponse}"`
            );
        }

        if (!response.ok) {
            throw new Error(
                result.detail || `Erro ${response.status} ao processar a planilha.`
            );
        }

        if (!result.data || !Array.isArray(result.data)) {
            throw new Error(
                "A resposta do servidor não contém a lista de dados esperada."
            );
        }

        // Armazena no estado global para permitir exportação posterior
        dadosRelatorioAtual = result.data;
        renderTable(dadosRelatorioAtual);
        resultsSection.classList.remove("hidden");
    } catch (err) {
        alert(`Falha no upload: ${err.message}`);
    } finally {
        loading.classList.add("hidden");
    }
});

function renderTable(data) {
    const tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = "";

    data.forEach((item) => {
        const tr = document.createElement("tr");

        const custo =
            item.custo_base !== null && item.custo_base !== undefined
                ? `R$ ${Number(item.custo_base).toFixed(2)}`
                : "N/A";

        const menorConc =
            item.menor_concorrente !== null && item.menor_concorrente !== undefined
                ? `R$ ${Number(item.menor_concorrente).toFixed(2)}`
                : "N/A";

        const precoSugerido =
            item.preco_sugerido !== null && item.preco_sugerido !== undefined
                ? `R$ ${Number(item.preco_sugerido).toFixed(2)}`
                : "N/A";

        let statusBadge = '<span class="badge badge-warning">Margem Protegida</span>';
        if (
            item.preco_sugerido &&
            item.menor_concorrente &&
            item.preco_sugerido < item.menor_concorrente
        ) {
            statusBadge = '<span class="badge badge-success">Mais Competitivo</span>';
        }

        tr.innerHTML = `
            <td><strong>${item.sku}</strong></td>
            <td>${item.nome}</td>
            <td>${custo}</td>
            <td>${menorConc}</td>
            <td class="highlight-price">${precoSugerido}</td>
            <td>${statusBadge}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// Lógica Genérica de Exportação (.docx e .xlsx)
async function exportarRelatorio(endpoint, nomeArquivo) {
    if (!dadosRelatorioAtual || dadosRelatorioAtual.length === 0) {
        alert("Processe uma planilha antes de exportar o relatório.");
        return;
    }

    try {
        const response = await fetch(`/api/upload/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dadosRelatorioAtual),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Erro ${response.status} ao gerar o arquivo.`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = nomeArquivo;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (err) {
        alert(`Falha na exportação: ${err.message}`);
    }
}

// Garante o vínculo dos botões
document.addEventListener("DOMContentLoaded", () => {
    const btnDocx = document.getElementById("btnExportDocx");
    const btnXlsx = document.getElementById("btnExportXlsx");

    if (btnDocx) {
        btnDocx.onclick = () => exportarRelatorio("export-docx", "Relatorio_Comparativo_Precos.docx");
    }

    if (btnXlsx) {
        btnXlsx.onclick = () => exportarRelatorio("export-xlsx", "Analise_Comparativa_Precos.xlsx");
    }
});