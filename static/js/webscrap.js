document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.checkmark-btn');
    const enviarTodasButton = document.getElementById('enviarTodasEmpresas');
    const forms = document.querySelectorAll('.enviar-empresa-form');

    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            button.classList.add('loading');
            button.disabled = true;

            const form = button.closest('form');
            if (form) {
                const formData = new FormData(form);

                // Verifica o estado do toggle
                const toggleState = localStorage.getItem('toggleState');

                // Seleciona a rota com base no estado do toggle
                const route = toggleState === 'Planilha' ? '/salvar_csv' : '/salvar_csv';

                fetch(route, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.lead_existente) {
                            window.open(data.lead_link, '_blank');
                        }
                    } else {
                        alert('Erro ao enviar a empresa.');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro na requisição.');
                })
                .finally(() => {
                    button.disabled = false;
                    setTimeout(() => {
                        button.classList.remove('loading');
                    }, 1000);
                });
            }
        });
    });

    enviarTodasButton.addEventListener('click', function () {
        const empresas = [];

        forms.forEach(form => {
            const formData = new FormData(form);

            // Array para armazenar os sócios
            const socios = [];
            const socios_nome = formData.getAll('socios_nome[]');
            const socios_qualificacao = formData.getAll('socios_qualificacao[]');

            // Como os campos 'faixa_etaria' e 'data_entrada' não estão mais presentes,
            // vamos removê-los do laço e da verificação.
            for (let i = 0; i < socios_nome.length; i++) {
                if (socios_nome[i] && socios_qualificacao[i]) {
                    socios.push({
                        nome: socios_nome[i],
                        qualificacao: socios_qualificacao[i]
                    });
                }
            }

            // Monta o objeto da empresa com os dados atualizados do form
            const empresa = {
                "razao_social": formData.get('razao_social'),
                "nome_fantasia": formData.get('nome_fantasia'),
                "logradouro": formData.get('logradouro'),
                "telefone_1": formData.get('telefone_1'),
                "telefone_2": formData.get('telefone_2'),
                "email": formData.get('email'),
                "capital_social": formData.get('capital_social'), // Campo adicionado conforme a nova estrutura
                "cnpj": formData.get('cnpj'),
                "socios": socios
            };

            // Adiciona a empresa ao array de empresas
            empresas.push(empresa);
        });

        fetch('/enviar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(empresas)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Todas as empresas foram enviadas com sucesso!');
            } else {
                alert('Erro ao enviar as empresas.');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro na requisição.');
        });
    });
});

function toggleSwitch() {

    const toggle = document.getElementById('toggle');
    const text = document.getElementById('text');
    const submitButtons = document.querySelectorAll('.checkmark-btn');

    if (toggle.classList.toggle('on')) {
        text.innerText = 'Planilha';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');  // Encontra o span dentro do botão
            textSpan.textContent = 'Enviar para Planilha';  // Altera apenas o texto dentro do span
        });
        localStorage.setItem('toggleState', 'Planilha');
    } else {
        text.innerText = 'Bitrix';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');  // Encontra o span dentro do botão
            textSpan.textContent = 'Enviar para Bitrix24';  // Altera apenas o texto dentro do span
        });
        localStorage.setItem('toggleState', 'Bitrix');
    }
}

window.onload = function() {

    const toggleState = localStorage.getItem('toggleState');
    const toggle = document.getElementById('toggle');
    const text = document.getElementById('text');
    const submitButtons = document.querySelectorAll('.checkmark-btn');

    if (toggleState === 'Planilha') {
        toggle.classList.add('on');
        text.innerText = 'Planilha';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');
            textSpan.textContent = 'Enviar para Planilha';
        });
    } else {
        toggle.classList.remove('on');
        text.innerText = 'Bitrix';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');
            textSpan.textContent = 'Enviar para Bitrix24';
        });
    }
}

document.getElementById('salvarTodasCsv').addEventListener('click', function (e) {
    e.preventDefault();

    const spinner = document.getElementById('loading-spinner');
    const notificationError = document.getElementById('notification-error');
    const notificationErrorMessage = document.getElementById('notificationErrorMessage');
    const notificationSucessMessage = document.getElementById('notificationSucessMessage');
    const notificationSucess = document.getElementById('notification-sucess'); // ID da notificação de sucesso

    spinner.style.display = 'block'; // Exibe o spinner

    const empresas = [];

    // Percorre todas as empresas renderizadas na página
    document.querySelectorAll('.enviar-empresa-form').forEach((form) => {
        const empresa = {
            razao_social: form.querySelector('input[name="razao_social"]').value.trim(),
            cnpj: form.querySelector('input[name="cnpj"]').value.trim(),
            nome_fantasia: form.querySelector('input[name="nome_fantasia"]').value.trim(),
            logradouro: form.querySelector('input[name="logradouro"]').value.trim(),
            email: form.querySelector('input[name="email"]').value.trim(),
            telefone_1: form.querySelector('input[name="telefone_1"]').value.trim(),
            telefone_2: form.querySelector('input[name="telefone_2"]').value.trim(),
            capital_social: form.querySelector('input[name="capital_social"]').value.trim(),
            socios: []
        };

        // Percorre todos os sócios da empresa
        form.querySelectorAll('input[name="socios_nome[]"]').forEach((socioNomeInput, index) => {
            const socio = {
                nome: socioNomeInput.value.trim(),
                qualificacao: form.querySelectorAll('input[name="socios_qualificacao[]"]')[index].value.trim()
            };
            empresa.socios.push(socio);
        });


        empresas.push(empresa);
    });

    // Verifica se há empresas para salvar
    if (empresas.length === 0) {
        // Exibe notificação de erro
        notificationErrorMessage.textContent = "Nenhum dado para ser salvo.";
        notificationError.classList.remove('hidden');

        // Aplica a transição corretamente
        setTimeout(() => {
            notificationError.classList.add('show');
        }, 10);

        // Esconde a notificação após 3 segundos
        setTimeout(() => {
            notificationError.classList.remove('show');
            setTimeout(() => {
                notificationError.classList.add('hidden');
            }, 500);
        }, 3000);

        spinner.style.display = 'none'; // Esconde o spinner
        return;
    }

    // Envia todas as empresas para o backend
    fetch('/salvar_todas_csv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ empresas })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            notificationSucessMessage.textContent = data.message;
            notificationSucess.classList.remove('hidden');

            // Aplica a transição corretamente
            setTimeout(() => {
                notificationSucess.classList.add('show');
            }, 10);

            // Esconde a notificação após 3 segundos
            setTimeout(() => {
                notificationSucess.classList.remove('show');
                setTimeout(() => {
                    notificationSucess.classList.add('hidden');
                }, 500);
            }, 3000);
        } else {
            throw new Error('Erro ao salvar as empresas.');
        }
    })
    .catch(error => {
        // Exibe notificação de erro
        notificationErrorMessage.textContent = error.message;
        notificationError.classList.remove('hidden');

        // Aplica a transição corretamente
        setTimeout(() => {
            notificationError.classList.add('show');
        }, 10);

        // Esconde a notificação após 3 segundos
        setTimeout(() => {
            notificationError.classList.remove('show');
            setTimeout(() => {
                notificationError.classList.add('hidden');
            }, 500);
        }, 3000);
    })
    .finally(() => {
        spinner.style.display = 'none'; // Esconde o spinner após o download ou erro
    });
});

document.getElementById('baixarCSV').addEventListener('click', function() {
    const spinner = document.getElementById('loading-spinner');
    const notificationError = document.getElementById('notification-error');
    const notificationErrorMessage = document.getElementById('notificationErrorMessage');
    const notificationSucess = document.getElementById('notification-sucess'); // Verifique se esse ID está correto
    const notificationSucessMessage = document.getElementById('notificationSucessMessage');

    spinner.style.display = 'block'; // Exibe o spinner

    fetch('/baixar_csv')
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    throw new Error('Nenhuma empresa disponível para download.');
                } else {
                    throw new Error('Erro ao baixar o arquivo.');
                }
            }
            return response.blob(); // Transforma a resposta em um blob (arquivo)
        })
        .then(blob => {
            // Cria uma URL temporária para baixar o arquivo
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'empresas.xlsx'; // Nome do arquivo baixado, agora com extensão .xlsx
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url); // Libera a URL temporária

            // Exibe notificação de sucesso
            notificationSucessMessage.textContent = "Arquivo baixado com sucesso!";
            notificationSucess.classList.remove('hidden');

            // Aplica a transição corretamente
            setTimeout(() => {
                notificationSucess.classList.add('show');
            }, 10);

            // Esconde a notificação após 3 segundos
            setTimeout(() => {
                notificationSucess.classList.remove('show');
                setTimeout(() => {
                    notificationSucess.classList.add('hidden');
                }, 500);
            }, 3000);
        })
        .catch(error => {
            // Exibe a notificação de erro
            notificationErrorMessage.textContent = error.message;
            notificationError.classList.remove('hidden');

            // Força o navegador a aplicar a transição corretamente
            setTimeout(() => {
                notificationError.classList.add('show');
            }, 10); // Pequeno delay para processar o estado "hidden"

            // Esconde a notificação após 3 segundos
            setTimeout(() => {
                notificationError.classList.remove('show');
                setTimeout(() => {
                    notificationError.classList.add('hidden');
                }, 500); // Delay para dar tempo à animação de sumir
            }, 3000);
        })
        .finally(() => {
            spinner.style.display = 'none'; // Esconde o spinner após o download ou erro
        });
});

document.getElementById('EnviarBitrix').addEventListener('click', function () {
    const spinner = document.getElementById('loading-spinner');
    const notificationError = document.getElementById('notification-error');
    const notificationErrorMessage = document.getElementById('notificationErrorMessage');

    // Exibe o spinner para indicar o processamento
    spinner.style.display = 'block';

    // Faz a requisição para a rota /criar_negocio
    fetch('/criar_negocio')
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    throw new Error('Nenhuma empresa disponível para criar negócio.');
                } else {
                    throw new Error('Erro ao enviar para o Bitrix.');
                }
            }
            return response.json(); // Converte a resposta para JSON
        })
        .then(data => {
            // Loga o retorno do Python para depuração

            // Verifica se a resposta geral é de sucesso
            if (data.message === "Negócios criados com sucesso!") {
                createSuccessNotification("Negócios criados com sucesso!", "Os negócios foram cadastrados com êxito.");
            }

            // Verifica se os links específicos existem
            if (data.links && data.links.length > 0) {
                data.links.forEach((link, index) => {
                    const razaoSocial = data.razoes_sociais[index]; // Pega a razão social correspondente
                    createNotification(link, razaoSocial, index);
                });
            } else {
                // Se não houver links, exibe a mensagem de erro retornada
                createNotification(data.message || "Nenhum negócio foi criado.", '', 0, true);
            }
        })
        .catch(error => {
            // Exibe a notificação de erro
            notificationErrorMessage.textContent = error.message;
            notificationError.classList.remove('hidden');

            // Loga o erro
            console.error('Erro na requisição:', error);

            // Força o navegador a aplicar a transição corretamente
            setTimeout(() => {
                notificationError.classList.add('show');
            }, 10);
        })
        .finally(() => {
            // Esconde o spinner após o término da requisição
            spinner.style.display = 'none';
        });
});

// Função para criar a notificação flutuante
function createNotification(link, razaoSocial, index, isError = false) {
    const notification = document.createElement('div');
    notification.classList.add(isError ? 'notification-error' : 'notification-success', 'hidden');

    // Conteúdo da notificação com link, razão social e botão de fechar
    notification.innerHTML = `
        <button class="close-btn" aria-label="Fechar notificação">X</button>
        <p>
            <strong>${isError ? 'Erro: ' : 'Empresa já cadastrada: '}</strong><br><br>
            ${razaoSocial ? `Razão Social: <strong>${razaoSocial}</strong><br><br>` : ''}
            <a href="${link}" target="_blank">${link}</a>
        </p>
    `;

    // Adiciona a notificação ao body
    document.body.appendChild(notification);

    // Mostra a notificação com atraso para cada item
    setTimeout(() => {
        notification.classList.remove('hidden');
        notification.classList.add('show');
    }, 100 * index);

    // Adiciona o evento de fechar para o botão 'X'
    const closeBtn = notification.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.classList.add('hidden');
            notification.remove(); // Remove do DOM após ocultar
        }, 500); // Tempo para desaparecer
    });
}

// Função para notificação de sucesso geral
function createSuccessNotification(message, details) {
    const notification = document.createElement('div');
    notification.classList.add('notification-success', 'hidden');

    // Conteúdo da notificação de sucesso geral
    notification.innerHTML = `
        <button class="close-btn" aria-label="Fechar notificação">X</button>
        <p>
            <strong>${message}</strong><br><br>
            ${details ? `<em>${details}</em>` : ''}
        </p>
    `;

    // Adiciona a notificação ao body
    document.body.appendChild(notification);

    // Mostra a notificação imediatamente
    setTimeout(() => {
        notification.classList.remove('hidden');
        notification.classList.add('show');
    }, 10);

    // Adiciona o evento de fechar para o botão 'X'
    const closeBtn = notification.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.classList.add('hidden');
            notification.remove(); // Remove do DOM após ocultar
        }, 500); // Tempo para desaparecer
    });
}
