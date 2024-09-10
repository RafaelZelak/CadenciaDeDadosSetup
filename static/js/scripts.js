document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const spinner = document.getElementById('loading-spinner');

    const paginationLinks = document.querySelectorAll('.pagination a, .pagination-container a');

    const enviarTodasEmpresasBtn = document.getElementById('enviarTodasEmpresas');

    form.addEventListener('submit', function() {
        spinner.style.display = 'block';
    });

    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            spinner.style.display = 'block';
        });
    });

    enviarTodasEmpresasBtn.addEventListener('click', function() {
        spinner.style.display = 'block';
    });

    window.addEventListener('beforeunload', function() {
        spinner.style.display = 'block';
    });

    window.addEventListener('load', function() {
        spinner.style.display = 'none';
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

        socioExtras.forEach(socio => {
            socio.classList.toggle('hidden');
        });

        if (this.textContent === 'Ver mais sócios') {
            this.textContent = 'Ver menos sócios';
        } else {
            this.textContent = 'Ver mais sócios';
        }
    });
});

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

document.getElementById('estado').addEventListener('input', function() {
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

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const termoBusca = urlParams.get('termo_busca') || '';
    const estado = urlParams.get('estado') || '';
    const cidade = urlParams.get('cidade') || '';

    document.querySelector('input[name="termo_busca"]').value = termoBusca;
    document.querySelector('input[name="estado"]').value = estado;
    document.querySelector('input[name="cidade"]').value = cidade;

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
