document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form'); // Formulário de busca
    const spinner = document.getElementById('loading-spinner');
    const paginationLinks = document.querySelectorAll('.pagination a'); // Links de paginação

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