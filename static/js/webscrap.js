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
                const route = toggleState === 'Planilha' ? '/salvar_csv' : '/enviar_empresa';

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

            const socios = [];
            const socios_nome = formData.getAll('socios_nome[]');
            const socios_faixa_etaria = formData.getAll('socios_faixa_etaria[]');
            const socios_qualificacao = formData.getAll('socios_qualificacao[]');
            const socios_data_entrada = formData.getAll('socios_data_entrada[]');

            for (let i = 0; i < socios_nome.length; i++) {
                if (socios_nome[i] && socios_faixa_etaria[i] && socios_qualificacao[i] && socios_data_entrada[i]) {
                    socios.push({
                        nome: socios_nome[i],
                        faixa_etaria: socios_faixa_etaria[i],
                        qualificacao: socios_qualificacao[i],
                        data_entrada: socios_data_entrada[i]
                    });
                }
            }

            const empresa = {
                "razao_social": formData.get('razao_social'),
                "nome_fantasia": formData.get('nome_fantasia'),
                "logradouro": formData.get('logradouro'),
                "municipio": formData.get('municipio'),
                "uf": formData.get('uf'),
                "cep": formData.get('cep'),
                "telefone_1": formData.get('telefone_1'),
                "telefone_2": formData.get('telefone_2'),
                "email": formData.get('email'),
                "porte": formData.get('porte'),
                "cnpj": formData.get('cnpj'),
                "socios": socios
            };

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
    console.log('toggleSwitch() function called');

    const toggle = document.getElementById('toggle');
    const text = document.getElementById('text');
    const submitButtons = document.querySelectorAll('.checkmark-btn');

    if (toggle.classList.toggle('on')) {
        console.log('Switched to Planilha');
        text.innerText = 'Planilha';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');  // Encontra o span dentro do botão
            textSpan.textContent = 'Enviar para Planilha';  // Altera apenas o texto dentro do span
        });
        localStorage.setItem('toggleState', 'Planilha');
    } else {
        console.log('Switched to Bitrix');
        text.innerText = 'Bitrix';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');  // Encontra o span dentro do botão
            textSpan.textContent = 'Enviar para Bitrix24';  // Altera apenas o texto dentro do span
        });
        localStorage.setItem('toggleState', 'Bitrix');
    }
}

window.onload = function() {
    console.log('Page loaded');

    const toggleState = localStorage.getItem('toggleState');
    const toggle = document.getElementById('toggle');
    const text = document.getElementById('text');
    const submitButtons = document.querySelectorAll('.checkmark-btn');

    if (toggleState === 'Planilha') {
        console.log('Restoring Planilha state');
        toggle.classList.add('on');
        text.innerText = 'Planilha';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');
            textSpan.textContent = 'Enviar para Planilha';
        });
    } else {
        console.log('Restoring Bitrix state');
        toggle.classList.remove('on');
        text.innerText = 'Bitrix';
        submitButtons.forEach((button) => {
            const textSpan = button.querySelector('.button-text');
            textSpan.textContent = 'Enviar para Bitrix24';
        });
    }
}

// Carrega o estado salvo ao inicializar
window.onload = function() {
    const savedState = localStorage.getItem('toggleState');
    const toggle = document.getElementById('toggle');
    const text = document.getElementById('text');

    if (savedState === 'Planilha') {
        toggle.classList.add('on');
        text.innerText = 'Planilha';
        textSpan.textContent = 'Enviar para Planilha';

    } else {
        text.innerText = 'Bitrix';
        textSpan.textContent = 'Enviar para Bitrix24';

    }
};

document.getElementById('salvarTodasCsv').addEventListener('click', function (e) {
    e.preventDefault();

    const empresas = [];

    // Percorre todas as empresas renderizadas na página
    document.querySelectorAll('.dadosEmpresa').forEach((empresaDiv) => {
        const empresa = {
            razao_social: empresaDiv.querySelector('.empresa-info p.font-bold').textContent.trim(),
            cnpj: empresaDiv.querySelector('.empresa-info p.font-semibold').textContent.trim().replace('CNPJ: ', ''),
            nome_fantasia: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(1)').textContent.trim().replace('Nome Fantasia: ', ''),
            logradouro: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(2)').textContent.trim().replace('Endereço: ', ''),
            municipio: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(3)').textContent.trim().replace('Cidade: ', ''),
            uf: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(4)').textContent.trim().replace('Estado: ', ''),
            cep: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(5)').textContent.trim().replace('CEP: ', ''),
            email: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(6)').textContent.trim().replace('Email: ', ''),
            telefone_1: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(7)').textContent.trim().replace('Telefone 1: ', ''),
            telefone_2: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(8)').textContent.trim().replace('Telefone 2: ', ''),
            porte: empresaDiv.querySelector('.detalhes-empresa p:nth-of-type(9)').textContent.trim().replace('Porte: ', ''),
            socios: []
        };

        // Percorre todos os sócios da empresa
        empresaDiv.querySelectorAll('.ul_socios .socio').forEach((socioLi) => {
            const socio = {
                nome: socioLi.querySelector('strong:nth-of-type(1)').textContent.trim().replace('Nome: ', ''),
                faixa_etaria: socioLi.querySelector('strong:nth-of-type(2)').textContent.trim().replace('Faixa Etária: ', ''),
                qualificacao: socioLi.querySelector('strong:nth-of-type(3)').textContent.trim().replace('Qualificação: ', ''),
                data_entrada: socioLi.querySelector('strong:nth-of-type(4)').textContent.trim().replace('Data de Entrada: ', ''),
            };
            empresa.socios.push(socio);
        });

        empresas.push(empresa);
    });

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
            alert(data.message);
        } else {
            alert('Erro ao salvar as empresas.');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro na requisição.');
    });
});

document.getElementById('baixarCSV').addEventListener('click', function() {
    window.location.href = '/baixar_csv';
});