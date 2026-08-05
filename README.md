# Calculadora de Honorários Contábeis (FeeSync)

Esta é uma aplicação web Full-Stack desenvolvida para facilitar a precificação de honorários contábeis de escritórios. A ferramenta processa dados sobre os custos operacionais do escritório e o perfil tributário do cliente para fornecer o piso de custo, valor recomendado (com base em margem de lucro alvo) e uma referência de mercado.

## Estrutura de Tecnologias

- **Backend:** Python com Flask.
- **Banco de Dados:** SQLite (via SQLAlchemy).
- **Frontend:** HTML5, Vanilla CSS3 (estilo Bento Grid e Glassmorphism) e JavaScript para requisições via Fetch API.

## Pré-requisitos

Certifique-se de possuir o Python 3.8 ou superior instalado em sua máquina.

## Como executar localmente

1. Clone o repositório:
```bash
git clone https://github.com/[seu-usuario]/fee-sync-app.git
cd fee-sync-app
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

A aplicação iniciará em `http://localhost:5000`. Na primeira execução, o banco de dados `fee_sync.db` será criado automaticamente.

## Arquitetura e Modelagem de Dados

A persistência de dados conta com duas entidades principais:
- **ConfiguracaoEscritorio**: Armazena parâmetros base como custo fixo mensal, horas produtivas e margem de lucro.
- **PrecificacaoCliente**: Guarda o histórico de cálculos realizados e o regime tributário de cada cliente analisado.

Desenvolvido para entregar agilidade e precisão no fechamento de propostas de serviços contábeis.
