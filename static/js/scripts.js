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
        pass
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

document.querySelectorAll('.ver-mais-socios').forEach(button => {
    button.addEventListener('click', function() {
        const socioExtras = this.previousElementSibling.querySelectorAll('.socio-extra');
        let isVisible = socioExtras[0].style.display === 'block';

        // Alternar visibilidade dos sócios extras
        socioExtras.forEach(socio => {
            socio.style.display = isVisible ? 'none' : 'block';
        });

        // Atualizar o texto do botão
        this.textContent = isVisible ? 'Ver mais sócios' : 'Ver menos sócios';
    });
});

});

document.addEventListener("DOMContentLoaded", function () {
    const notifications = document.querySelectorAll('.notification');
    const dismissedNotifications = []; // Armazena as notificações que sumiram
    const notificationCounter = document.getElementById('notification-counter');
    const notificationLink = document.getElementById('notification-link');
    let visibleNotificationsCount = 0; // Controla quantas notificações estão visíveis

    // Atualiza o contador de notificações
    function updateNotificationCounter() {
        notificationCounter.textContent = dismissedNotifications.length;
        notificationCounter.style.display = dismissedNotifications.length > 0 ? 'inline' : 'none';
    }

    function showNotification(notification, index) {
        if (visibleNotificationsCount >= 3) return; // Limita para no máximo 3 notificações visíveis
        visibleNotificationsCount++; // Incrementa o contador de notificações visíveis

        setTimeout(() => {
            notification.classList.remove('opacity-0', 'translate-y-4');
            notification.classList.add('opacity-100', 'translate-y-0');

            // Inicia a redução da barra de progresso
            const progressBar = notification.querySelector('.progress-bar');
            progressBar.style.width = '0%';

            // Remove a notificação após 10 segundos
            setTimeout(() => {
                notification.classList.add('disappearing');
                dismissedNotifications.push(notification.outerHTML); // Salva a notificação
                updateNotificationCounter(); // Atualiza o contador

                setTimeout(() => {
                    notification.remove();
                    visibleNotificationsCount--; // Diminui o contador quando a notificação some
                }, 500); // Tempo da animação de desaparecer
            }, 10000); // 10 segundos de espera
        }, 100 * index); // Cada notificação aparece com um pequeno atraso
    }

    notifications.forEach((notification, index) => {
        showNotification(notification, index);
    });

    // Função para exibir notificações quando o link é clicado
    notificationLink.addEventListener('click', function (event) {
        event.preventDefault();
        const notificationList = document.getElementById('notification-list');

        // Reinsere as notificações que sumiram
        dismissedNotifications.forEach((notificationHTML, index) => {
            notificationList.insertAdjacentHTML('beforeend', notificationHTML);

            const reinsertedNotification = notificationList.lastElementChild;
            reinsertedNotification.classList.remove('disappearing');

            // Aplica novamente o efeito de desaparecimento após 10 segundos
            setTimeout(() => {
                reinsertedNotification.classList.add('disappearing');
                setTimeout(() => {
                    reinsertedNotification.remove();
                    visibleNotificationsCount--; // Diminui o contador quando a notificação some
                }, 500);
            }, 10000);
        });

        // Limpa as notificações armazenadas
        dismissedNotifications.length = 0;
        updateNotificationCounter(); // Atualiza o contador
    });
});

function dismissNotification(notificationId, accepted) {
    const formData = new FormData();
    formData.append('notification_id', notificationId);
    formData.append('accepted', accepted);

    fetch('/dismiss_notification', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.getElementById(`notification-${notificationId}`);
            if (notificationElement) {
                notificationElement.classList.add('disappearing');
                setTimeout(() => {
                    notificationElement.remove();
                    visibleNotificationsCount--; // Diminui o contador quando a notificação é removida manualmente
                }, 500); // 500ms é o tempo da animação de desaparecimento
            }
        } else {
            console.error('Erro ao processar a notificação:', data.error);
        }
    }).catch(error => {
        console.error('Erro na requisição:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const verMaisButtons = document.querySelectorAll('.ver-mais');

    verMaisButtons.forEach(button => {
        button.addEventListener('click', function() {
            const detalhesEmpresa = this.closest('.dadosEmpresa').querySelector('.detalhes-empresa');

            if (detalhesEmpresa.style.maxHeight && detalhesEmpresa.classList.contains('expanded')) {
                // Recolher
                detalhesEmpresa.style.maxHeight = null;
                detalhesEmpresa.classList.remove('expanded');
                this.textContent = 'Ver mais';
            } else {
                // Expandir com altura dinâmica
                detalhesEmpresa.style.maxHeight = detalhesEmpresa.scrollHeight + "px";
                detalhesEmpresa.classList.add('expanded');
                this.textContent = 'Ver menos';
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Carregar estados
    fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(estados => {
            console.log('Estados carregados:', estados); // Verifica se os estados estão sendo carregados
            const estadoDatalist = document.getElementById('estados');
            estados.forEach(estado => {
                const option = document.createElement('option');
                option.value = estado.sigla; // Sigla do estado
                option.textContent = estado.nome; // Nome do estado
                estadoDatalist.appendChild(option);
            });
        })
        .catch(error => console.error('Erro ao carregar estados:', error));

    const estadoInput = document.getElementById('estado');
    const cidadeInput = document.getElementById('cidade');
    const cidadeDatalist = document.getElementById('cidades');

    // Carregar cidades com base no estado selecionado
    estadoInput.addEventListener('input', function() {
        const estadoSigla = this.value.toUpperCase();
        cidadeDatalist.innerHTML = ''; // Limpa as cidades ao mudar o estado

        if (estadoSigla) {
            fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estadoSigla}/municipios`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(cidades => {
                    console.log('Cidades carregadas:', cidades); // Verifica se as cidades estão sendo carregadas
                    cidades.forEach(cidade => {
                        const option = document.createElement('option');
                        option.value = cidade.nome; // Nome da cidade
                        cidadeDatalist.appendChild(option);
                    });
                })
                .catch(error => console.error('Erro ao carregar cidades:', error));
        }
    });

    // Preencher campos com parâmetros da URL
    const urlParams = new URLSearchParams(window.location.search);
    const termoBusca = urlParams.get('termo_busca') || '';
    const estado = urlParams.get('estado') || '';
    const cidade = urlParams.get('cidade') || '';

    const termoBuscaInput = document.querySelector('input[name="termo_busca"]');
    termoBuscaInput.value = termoBusca; // Preenche o campo de busca
    estadoInput.value = estado; // Preenche o campo do estado
    cidadeInput.value = cidade; // Preenche o campo da cidade

    // Carregar cidades se o estado estiver preenchido
    if (estado) {
        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(cidades => {
                cidadeDatalist.innerHTML = ''; // Limpa as cidades antes de carregar
                cidades.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.nome; // Nome da cidade
                    cidadeDatalist.appendChild(option);
                });
            })
            .catch(error => console.error('Erro ao carregar cidades:', error));
    }
});