// Obtém os elementos
const overlay = document.getElementById('overlay');
const highlight = document.getElementById('highlight');
const overlayButton = document.getElementById('overlayButton');
const nextStepButton = document.getElementById('nextStepButton');
const toggleButton = document.querySelector('.switch-container');
const tutorialText = document.getElementById('tutorial-text');
const arrow = document.getElementById('arrow');

// Variável para controlar o estado do tutorial
let currentStep = 0;

// Função para ativar o overlay
overlayButton.addEventListener('click', () => {
    overlay.style.display = 'flex';
    currentStep = 0; // Reiniciar o tutorial ao clicar no botão de ativação
    showStep(currentStep);
});

// Função para avançar o tutorial
nextStepButton.addEventListener('click', () => {
    currentStep++;
    const totalSteps = 6; // Número total de passos (0 a 3)

    if (currentStep < totalSteps) {
        showStep(currentStep);
    } else {
        // Fechar o tutorial ao fim
        overlay.style.display = 'none';
    }
});

function showStep(step) {
    let rect;

    if (step === 0) {
        rect = toggleButton.getBoundingClientRect();
        tutorialText.innerText = "Clique no botão de toggle no canto inferior para ligar ou desligar a funcionalidade Bitrix.";
    } else if (step === 1) {
        const filterContainer = document.querySelector('.estado-cidade-container');
        rect = filterContainer.getBoundingClientRect();
        tutorialText.innerText = "Agora selecione o Estado e a Cidade para filtrar os dados.";
    } else if (step === 2) {
        const searchInput = document.querySelector('.input-container');
        rect = searchInput.getBoundingClientRect();
        tutorialText.innerText = "Agora digite o termo de busca que deseja encontrar.";
    } else if (step === 3) {
        const searchButton = document.querySelector('.buscar');
        rect = searchButton.getBoundingClientRect();
        tutorialText.innerText = "Por fim, clique no botão de pesquisa para buscar os dados.";
    } else if (step === 4) {
        const anotherButton = document.querySelector('.dadosEmpresa');
        rect = anotherButton.getBoundingClientRect();
        tutorialText.innerText = "Clique aqui para ver mais detalhes sobre a empresa.";
    } else if (step === 5) {
        const finalElement = document.querySelector('.button-text');
        rect = finalElement.getBoundingClientRect();
        tutorialText.innerText = "Finalizamos o tutorial!";
    }

    const padding = 10;
    const left = rect.left - padding;
    const top = rect.top - padding;
    const right = rect.right + padding;
    const bottom = rect.bottom + padding;

    overlay.style.clipPath = `
        polygon(
            0 0, 100% 0, 100% 100%, 0 100%,
            0 ${top}px,
            ${left}px ${top}px,
            ${left}px ${bottom}px,
            ${right}px ${bottom}px,
            ${right}px ${top}px,
            0 ${top}px
        )`;

    highlight.style.width = `${rect.width}px`;
    highlight.style.height = `${rect.height}px`;
    highlight.style.top = `${rect.top}px`;
    highlight.style.left = `${rect.left}px`;
    highlight.style.borderRadius = '20px';

    // Posicionar a seta
    arrow.style.top = `${rect.top + rect.height / 2 - 20}px`; // Centraliza verticalmente
    arrow.style.left = `${rect.left - 60}px`; // Posição da seta à esquerda do elemento destacado

    // Ajustar o conteúdo do overlay
    const overlayContent = document.querySelector('.overlay-content');
    const arrowRect = arrow.getBoundingClientRect();

    // Definir a posição do conteúdo à esquerda da seta
    let overlayContentTop = arrowRect.top + (arrowRect.height / 2) - (overlayContent.offsetHeight / 2);
    let overlayContentLeft = arrowRect.left - overlayContent.offsetWidth - 10; // 10px de espaçamento à esquerda da seta

    // Ajustar limites da tela
    const windowHeight = window.innerHeight;
    const windowWidth = window.innerWidth;

    // Se o conteúdo sair pela esquerda, ajustar para manter na tela
    if (overlayContentLeft < 0) {
        overlayContentLeft = arrowRect.left + arrowRect.width + 10; // Mover para a direita se estiver fora da tela
    }

    // Ajustar o limite superior
    if (overlayContentTop < 0) {
        overlayContentTop = 10; // Margem superior
    }

    // Ajustar o limite inferior
    if (overlayContentTop + overlayContent.offsetHeight > windowHeight) {
        overlayContentTop = windowHeight - overlayContent.offsetHeight - 10; // Margem inferior
    }

    // Aplicar as posições calculadas
    overlayContent.style.position = 'absolute'; // Certifique-se de que o conteúdo seja absoluto
    overlayContent.style.top = `${overlayContentTop}px`;
    overlayContent.style.left = `${overlayContentLeft}px`;
}