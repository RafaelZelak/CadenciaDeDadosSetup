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