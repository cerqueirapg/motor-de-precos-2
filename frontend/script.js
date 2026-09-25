document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('resultsSection');
    const tableBody = document.getElementById('tableBody');

    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Exibe loader e oculta resultados antigos
    loading.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    tableBody.innerHTML = '';

    try {
        const response = await fetch('/api/upload/excel', {
            method: 'POST',
            body: formData
        });

        const textResponse = await response.text();
        let result;

        try {
            result = JSON.parse(textResponse);
        } catch (jsonErr) {
            throw new Error(`Resposta inválida do servidor (Status ${response.status}). Conteúdo: "${textResponse}"`);
        }

        if (!response.ok) {
            throw new Error(result.detail || `Erro ${response.status} ao processar a planilha.`);
        }

        if (!result.data || !Array.isArray(result.data)) {
            throw new Error("A resposta do servidor não contém a lista de dados esperada.");
        }

        // Renderiza as linhas na tabela
        result.data.forEach(item => {
            const tr = document.createElement('tr');
            
            const custo = item.custo_base !== null && item.custo_base !== undefined 
                ? `R$ ${Number(item.custo_base).toFixed(2)}` 
                : 'N/A';
                
            const menorConc = item.menor_concorrente !== null && item.menor_concorrente !== undefined 
                ? `R$ ${Number(item.menor_concorrente).toFixed(2)}` 
                : 'N/A';
                
            const precoSugerido = item.preco_sugerido !== null && item.preco_sugerido !== undefined 
                ? `R$ ${Number(item.preco_sugerido).toFixed(2)}` 
                : 'N/A';
            
            // Badge visual de status
            let statusBadge = '<span class="badge badge-warning">Margem Protegida</span>';
            if (item.preco_sugerido && item.menor_concorrente && item.preco_sugerido < item.menor_concorrente) {
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

        resultsSection.classList.remove('hidden');
    } catch (err) {
        alert(`Falha no upload: ${err.message}`);
    } finally {
        loading.classList.add('hidden');
    }
});