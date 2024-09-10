document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form'); // Formulário de busca
    const spinner = document.getElementById('loading-spinner');

    // Captura todos os links de paginação
    const paginationLinks = document.querySelectorAll('.pagination a, .pagination-container a'); // Inclui a nova div de paginação

    // Captura o botão de "Enviar Todas as Empresas"
    const enviarTodasEmpresasBtn = document.getElementById('enviarTodasEmpresas');

    // Mostra o spinner ao submeter o formulário
    form.addEventListener('submit', function() {
        spinner.style.display = 'block'; // Exibe o spinner
    });

    // Mostra o spinner ao clicar nos links de paginação
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            spinner.style.display = 'block'; // Exibe o spinner ao clicar no link
        });
    });

    // Mostra o spinner ao clicar no botão "Enviar Todas as Empresas"
    enviarTodasEmpresasBtn.addEventListener('click', function() {
        spinner.style.display = 'block'; // Exibe o spinner
    });

    // Mostra o spinner ao recarregar ou sair da página
    window.addEventListener('beforeunload', function() {
        spinner.style.display = 'block'; // Exibe o spinner ao recarregar a página
    });

    // Esconde o spinner após o carregamento da página
    window.addEventListener('load', function() {
        spinner.style.display = 'none'; // Oculta o spinner após a página ser carregada
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const togglePassword = document.querySelector('#toggle-password');
    const passwordField = document.querySelector('#password');
    const eyeIcon = document.querySelector('#eye-icon');

    if (togglePassword && passwordField && eyeIcon) {
        togglePassword.addEventListener('click', () => {
            const isPassword = passwordField.getAttribute('type') === 'password';
            passwordField.setAttribute('type', isPassword ? 'text' : 'password');

            // Alterar opacidade do ícone ao clicar
            eyeIcon.style.opacity = isPassword ? '0.5' : '1';
        });
    } else {
        console.error('Elementos não encontrados: Verifique os IDs dos elementos HTML.');
    }

    // Remover alertas após 3 segundos com animação
    const alertContainer = document.querySelector('#alert-container');
    if (alertContainer) {
        setTimeout(() => {
            alertContainer.classList.add('opacity-0', 'transition-opacity');
            setTimeout(() => alertContainer.remove(), 500);
        }, 3000);
    }
});

let isImageStyle = false; // Declara a variável no escopo global

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'y') {
        event.preventDefault(); // Evita a ação padrão do navegador

        if (isImageStyle) {
            // Voltar ao estilo original (só a cor de fundo)
            document.body.style.backgroundColor = '#0a192f';
            document.body.style.backgroundImage = 'none'; // Remove a imagem de fundo
        } else {
            // Mudar para o estilo com a imagem de fundo
            document.body.style.backgroundColor = 'transparent'; // Remove a cor de fundo
            document.body.style.backgroundImage = 'url("../static/img/thiago.png")';
        }

        // Alterna o estado
        isImageStyle = !isImageStyle;
    }
});

document.querySelectorAll('.ver-mais').forEach(button => {
    button.addEventListener('click', function() {
        const detalhes = this.previousElementSibling;
        detalhes.classList.toggle('hidden');
        this.textContent = detalhes.classList.contains('hidden') ? 'Ver mais' : 'Ver menos';
    });
});

document.querySelectorAll('.ver-mais-socios').forEach(button => {
    button.addEventListener('click', function() {
        const socioExtras = this.previousElementSibling.querySelectorAll('.socio-extra');

        // Alternar a exibição dos sócios extras
        socioExtras.forEach(socio => {
            socio.classList.toggle('hidden');
        });

        // Alterar o texto do botão
        if (this.textContent === 'Ver mais sócios') {
            this.textContent = 'Ver menos sócios';
        } else {
            this.textContent = 'Ver mais sócios';
        }
    });
});

// Preencher a lista de estados
fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
    .then(response => response.json())
    .then(estados => {
        const estadoDatalist = document.getElementById('estados');
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado.sigla;
            option.textContent = estado.nome;
            estadoDatalist.appendChild(option);
        });
    })
    .catch(error => console.error('Erro ao carregar estados:', error));

// Atualizar a lista de cidades com base no estado selecionado
document.getElementById('estado').addEventListener('input', function() {
    const estadoSigla = this.value.toUpperCase();
    const cidadeDatalist = document.getElementById('cidades');

    // Limpa as cidades anteriores
    cidadeDatalist.innerHTML = '';

    if (estadoSigla) {
        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estadoSigla}/municipios`)
            .then(response => response.json())
            .then(cidades => {
                cidades.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.nome;
                    cidadeDatalist.appendChild(option);
                });
            })
            .catch(error => console.error('Erro ao carregar cidades:', error));
    }
});

// Preencher campos do formulário com valores da URL
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const termoBusca = urlParams.get('termo_busca') || '';
    const estado = urlParams.get('estado') || '';
    const cidade = urlParams.get('cidade') || '';

    document.querySelector('input[name="termo_busca"]').value = termoBusca;
    document.querySelector('input[name="estado"]').value = estado;
    document.querySelector('input[name="cidade"]').value = cidade;

    // Atualiza a lista de cidades com base no estado selecionado
    if (estado) {
        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`)
            .then(response => response.json())
            .then(cidades => {
                const cidadeDatalist = document.getElementById('cidades');
                cidadeDatalist.innerHTML = ''; // Limpa as cidades anteriores

                cidades.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.nome;
                    cidadeDatalist.appendChild(option);
                });
            })
            .catch(error => console.error('Erro ao carregar cidades:', error));
    }
});
