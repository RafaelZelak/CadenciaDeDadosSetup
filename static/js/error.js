    // Função para fazer a requisição assíncrona e tratar erros comuns
    async function fetchData() {
        try {
            const response = await fetch('/home?termo_busca=Setup+Tecnologia&estado=PR&cidade=Curitiba');

            // Verifica o código de status da resposta
            if (!response.ok) {
                const data = await response.json();

                // Exibe mensagem personalizada dependendo do código de status
                switch (response.status) {
                    case 400:
                        showError('Erro 400: ' + data.message);
                        break;
                    case 404:
                        showError('Erro 404: ' + data.message);
                        break;
                    case 429:
                        showError('Erro 429: ' + data.message);
                        break;
                    case 500:
                        showError('Erro 500: ' + data.message);
                        break;
                    default:
                        showError('Erro desconhecido: ' + data.message);
                }
            } else {
                // Processa a resposta normalmente
                const result = await response.text();
                console.log(result);
            }
        } catch (error) {
            console.error('Erro ao fazer a requisição:', error);
        }
    }

    // Função para exibir a mensagem de erro na tela
    function showError(message) {
        // Cria um elemento de notificação
        const notification = document.createElement('div');
        notification.innerText = message;
        notification.style.position = 'fixed';
        notification.style.top = '10px';
        notification.style.right = '10px';
        notification.style.backgroundColor = 'red';
        notification.style.color = 'white';
        notification.style.padding = '10px';
        notification.style.borderRadius = '5px';

        // Adiciona o elemento ao corpo da página
        document.body.appendChild(notification);

        // Remove a notificação após 5 segundos
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Chama a função fetchData quando a página for carregada
    window.onload = function() {
        fetchData();
    };
