document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const spinner = document.getElementById('loading-spinner');
    const paginationLinks = document.querySelectorAll('.pagination a, .pagination-container a');
    const enviarTodasEmpresasBtn = document.getElementById('enviarTodasEmpresas');
    const estadoInput = document.getElementById('estado');
    const cidadeInput = document.getElementById('cidade');
    const termoBuscaInput = document.querySelector('input[name="termo_busca"]');
    const urlParams = new URLSearchParams(window.location.search);

    // Função para carregar filtros do localStorage
    const loadFilters = () => {
        estadoInput.value = localStorage.getItem('estado') || '';
        cidadeInput.value = localStorage.getItem('cidade') || '';
        termoBuscaInput.value = localStorage.getItem('termo_busca') || '';
    };

    // Função para salvar filtros no localStorage
    const saveFilters = () => {
        localStorage.setItem('estado', estadoInput.value);
        localStorage.setItem('cidade', cidadeInput.value);
        localStorage.setItem('termo_busca', termoBuscaInput.value);
    };

    // Adicionar parâmetros de filtro aos links de paginação
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Evitar navegação padrão
            const pageUrl = new URL(link.href);

            // Adicionar filtros aos parâmetros da URL
            pageUrl.searchParams.set('termo_busca', termoBuscaInput.value);
            pageUrl.searchParams.set('estado', estadoInput.value);
            pageUrl.searchParams.set('cidade', cidadeInput.value);

            // Redirecionar para a URL com filtros preservados
            window.location.href = pageUrl.toString();
            spinner.style.display = 'block';
        });
    });

    form.addEventListener('submit', function() {
        saveFilters();
        spinner.style.display = 'block';
    });

    enviarTodasEmpresasBtn.addEventListener('click', function() {
        spinner.style.display = 'block';
    });

    window.addEventListener('beforeunload', function() {
        spinner.style.display = 'block';
    });

    window.addEventListener('load', function() {
        spinner.style.display = 'none';
        loadFilters();
    });

    // Alternar visibilidade de senha
    document.addEventListener('DOMContentLoaded', () => {
        const togglePassword = document.querySelector('#toggle-password');
        const passwordField = document.querySelector('#password');
        const eyeIcon = document.querySelector('#eye-icon');

        if (togglePassword && passwordField && eyeIcon) {
            togglePassword.addEventListener('click', () => {
                const isPassword = passwordField.getAttribute('type') === 'password';
                passwordField.setAttribute('type', isPassword ? 'text' : 'password');

                eyeIcon.style.opacity = isPassword ? '0.5' : '1';
            });
        } else {
            console.error('Elementos não encontrados: Verifique os IDs dos elementos HTML.');
        }

        const alertContainer = document.querySelector('#alert-container');
        if (alertContainer) {
            setTimeout(() => {
                alertContainer.classList.add('opacity-0', 'transition-opacity');
                setTimeout(() => alertContainer.remove(), 500);
            }, 3000);
        }
    });

    // Alternar estilo de fundo
    let isImageStyle = false;

    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'y') {
            event.preventDefault();

            if (isImageStyle) {
                document.body.style.backgroundColor = '#0a192f';
                document.body.style.backgroundImage = 'none'; // Remove a imagem de fundo
            } else {
                document.body.style.backgroundColor = 'transparent'; // Remove a cor de fundo
                document.body.style.backgroundImage = 'url("../static/img/thiago.png")';
            }

            isImageStyle = !isImageStyle;
        }
    });

    // Alternar visibilidade de detalhes
    document.querySelectorAll('.ver-mais').forEach(button => {
        button.addEventListener('click', function() {
            const detalhes = this.previousElementSibling;
            detalhes.classList.toggle('expanded');
            this.textContent = detalhes.classList.contains('expanded') ? 'Ver menos' : 'Ver mais';
        });
    });

    document.querySelectorAll('.ver-mais-socios').forEach(button => {
        button.addEventListener('click', function() {
            const socioExtras = this.previousElementSibling.querySelectorAll('.socio-extra');

            socioExtras.forEach(socio => {
                socio.classList.toggle('visible');
            });

            if (this.textContent === 'Ver mais sócios') {
                this.textContent = 'Ver menos sócios';
            } else {
                this.textContent = 'Ver mais sócios';
            }
        });
    });

    // Carregar estados
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

    // Carregar cidades com base no estado selecionado
    estadoInput.addEventListener('input', function() {
        const estadoSigla = this.value.toUpperCase();
        const cidadeDatalist = document.getElementById('cidades');

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

    // Preencher campos com parâmetros da URL
    const termoBusca = urlParams.get('termo_busca') || '';
    const estado = urlParams.get('estado') || '';
    const cidade = urlParams.get('cidade') || '';

    termoBuscaInput.value = termoBusca;
    estadoInput.value = estado;
    cidadeInput.value = cidade;

    if (estado) {
        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`)
            .then(response => response.json())
            .then(cidades => {
                const cidadeDatalist = document.getElementById('cidades');
                cidadeDatalist.innerHTML = '';

                cidades.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.nome;
                    cidadeDatalist.appendChild(option);
                });
            })
            .catch(error => console.error('Erro ao carregar cidades:', error));
    }
});
