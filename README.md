# FeeSync — Calculadora de Honorarios Contabeis

Aplicacao web Full-Stack para precificacao inteligente de honorarios contabeis. Processa dados operacionais do escritorio e o perfil completo do cliente para calcular o **piso de custo**, **valor recomendado** (com margem de lucro) e uma **referencia de mercado** baseada em regime tributario e ramo de atividade.

## Tecnologias

| Camada    | Tecnologia                                  |
|-----------|---------------------------------------------|
| Backend   | Python 3.8+ / Flask                         |
| Banco     | SQLite (SQLAlchemy ORM)                      |
| Frontend  | HTML5, Vanilla CSS, JavaScript (Fetch API)   |

## Estrutura de Arquivos

```
fee-sync-app/
+-- app.py                    # Servidor Flask + motor de calculo
+-- models.py                 # Modelos SQLAlchemy
+-- requirements.txt          # Dependencias Python
+-- templates/
!   +-- index.html            # Template principal
+-- static/
    +-- css/
    !   +-- style.css         # Design system SaaS com contraste premium e sombras "glow"
    +-- js/
        +-- main.js           # Mascara moeda, fetch, animacoes
```

## Motor de Calculo

### Entradas

**Escritorio:**
- `custo_fixo_mensal` (R$) — soma de aluguel, folha, utilidades e licencas
- `horas_produtivas_mes` — total de horas produtivas da equipe
- `margem_lucro_alvo` (%) — margem pretendida

**Cliente:**
- `nome_empresa`
- `regime_tributario` — MEI, Simples Nacional, Lucro Presumido, Lucro Real
- `ramo_atividade` — Servico, Comercio, Industria (peso de complexidade: Industria > Comercio > Servico)
- `volume_nfe` — faixa mensal de documentos fiscais (Ate 20, 21-80, 81-200, 200+)
- `num_funcionarios_socios` — quantidade para apuracao de folha/pro-labore

### Formula

```
Custo/Hora = custo_fixo_mensal / horas_produtivas_mes

Horas do Cliente = Horas Base (regime)
                 + Horas NFe (volume)
                 + num_funcionarios * 0.5h
                 + Adicional (ramo)

Piso de Custo      = Horas do Cliente x Custo/Hora
Valor Recomendado  = Piso de Custo / (1 - margem/100)
Ref. Mercado       = Faixa (Min, Max) baseada em regime x ramo
```

## Como Executar

1. Clone o repositorio:
```bash
git clone https://github.com/MatheusLeo26/fee-sync-app.git
cd fee-sync-app
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependencias:
```bash
pip install -r requirements.txt
```

4. Execute:
```bash
python app.py
```

Acesse `http://localhost:5000`. O banco `fee_sync.db` sera criado automaticamente na primeira execucao.

## API

### POST /api/calcular

**Request body (JSON):**
```json
{
  "custo_fixo_mensal": 15000,
  "horas_produtivas_mes": 160,
  "margem_lucro_alvo": 30,
  "nome_empresa": "Tech Solutions Ltda",
  "regime_tributario": "simples",
  "ramo_atividade": "comercio",
  "volume_nfe": "21_a_80",
  "num_funcionarios_socios": 5
}
```

**Response (JSON):**
```json
{
  "piso_custo": 1312.5,
  "valor_recomendado": 1875.0,
  "mercado_min": 700,
  "mercado_max": 1500,
  "horas_estimadas": 14.0
}
```

## Modelagem de Dados

- **ConfiguracaoEscritorio**: Parametros base do escritorio (custo fixo, horas, margem).
- **PrecificacaoCliente**: Historico de calculos com todos os campos do cliente e resultados.

---

Desenvolvido para entregar agilidade e precisao no fechamento de propostas de servicos contabeis.
