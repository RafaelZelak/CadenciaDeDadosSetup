function loadingScreen() {
    return {
          messages: [
              "Procurando Informações",
              "Refinando Informações da Empresa",
              "Verificando Detalhes Importantes",
              "Organizando Informações",
              "Ajustando Formato",
              "Aplicando Filtros Especiais",
              "Reunindo Informações",
              "Buscando Novos Registros",
              "Avaliando Coletados",
              "Organizando Resultados",
              "Refinando Resultados",
              "Verificando Fontes",
              "Estruturando Informações",
              "Atualizando Registros",
              "Preparando Resultados",
              "Filtrando Informações Valiosas",
              "Conferindo Precisão",
              "Extraindo Informações",
              "Conectando aos Servidores"
          ],
      currentMessage: "Procurando Dados",
      fading: false,
      previousIndex: -1,
      startLoading() {
        setInterval(() => {
          this.fading = true;
          setTimeout(() => {
            let newIndex;
            do {
              newIndex = Math.floor(Math.random() * this.messages.length);
            } while (newIndex === this.previousIndex);

            this.currentMessage = this.messages[newIndex];
            this.previousIndex = newIndex;
            this.fading = false;
          }, 700);
        }, 6500);
      }
    };
  }