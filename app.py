import os
from flask import Flask, render_template, request, jsonify
from models import db, ConfiguracaoEscritorio, PrecificacaoCliente

app = Flask(__name__)

# Configuracao do banco de dados SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "fee_sync.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Tabelas de referencia para o motor de calculo
# ---------------------------------------------------------------------------

# Horas base por regime tributario
HORAS_BASE_REGIME = {
    'mei': 2.0,
    'simples': 5.0,
    'presumido': 10.0,
    'real': 20.0,
}

# Horas adicionais por volume mensal de NFe
HORAS_VOLUME_NFE = {
    'ate_20': 1.0,
    '21_a_80': 3.0,
    '81_a_200': 6.0,
    '200_mais': 10.0,
}

# Horas adicionais por ramo de atividade (peso de complexidade)
HORAS_RAMO = {
    'servico': 0.0,
    'comercio': 2.0,
    'industria': 5.0,
}

# Referencia de mercado (regime, ramo) -> (min, max) em R$
REF_MERCADO = {
    ('mei', 'servico'):       (150, 300),
    ('mei', 'comercio'):      (200, 400),
    ('mei', 'industria'):     (250, 500),
    ('simples', 'servico'):   (500, 1200),
    ('simples', 'comercio'):  (700, 1500),
    ('simples', 'industria'): (900, 2000),
    ('presumido', 'servico'):   (1500, 2500),
    ('presumido', 'comercio'):  (1800, 3000),
    ('presumido', 'industria'): (2200, 4000),
    ('real', 'servico'):   (3000, 6000),
    ('real', 'comercio'):  (3500, 8000),
    ('real', 'industria'): (4500, 10000),
}


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/calcular', methods=['POST'])
def calcular():
    data = request.json

    try:
        # --- Campos do Escritorio ---
        custo_fixo = float(data.get('custo_fixo_mensal', 0))
        horas_produtivas = int(data.get('horas_produtivas_mes', 0))
        margem_lucro = float(data.get('margem_lucro_alvo', 0))

        # --- Campos do Cliente ---
        nome_empresa = data.get('nome_empresa', '').strip()
        regime = data.get('regime_tributario', '')
        ramo = data.get('ramo_atividade', '')
        volume_nfe = data.get('volume_nfe', '')
        num_func = int(data.get('num_funcionarios_socios', 0))

        # --- Validacoes ---
        if horas_produtivas <= 0:
            return jsonify({'error': 'Horas produtivas devem ser maiores que zero.'}), 400
        if margem_lucro >= 100:
            return jsonify({'error': 'Margem de lucro deve ser menor que 100%.'}), 400
        if margem_lucro < 0:
            return jsonify({'error': 'Margem de lucro nao pode ser negativa.'}), 400
        if not nome_empresa:
            return jsonify({'error': 'Nome da empresa e obrigatorio.'}), 400
        if regime not in HORAS_BASE_REGIME:
            return jsonify({'error': 'Regime tributario invalido.'}), 400
        if ramo not in HORAS_RAMO:
            return jsonify({'error': 'Ramo de atividade invalido.'}), 400
        if volume_nfe not in HORAS_VOLUME_NFE:
            return jsonify({'error': 'Volume de NFe invalido.'}), 400
        if num_func < 0:
            return jsonify({'error': 'Numero de funcionarios/socios nao pode ser negativo.'}), 400

        # --- Motor de Calculo ---
        custo_por_hora = custo_fixo / horas_produtivas

        horas_cliente = (
            HORAS_BASE_REGIME[regime]
            + HORAS_VOLUME_NFE[volume_nfe]
            + (num_func * 0.5)
            + HORAS_RAMO[ramo]
        )

        piso_custo = horas_cliente * custo_por_hora
        valor_recomendado = piso_custo / (1 - (margem_lucro / 100))

        mercado_min, mercado_max = REF_MERCADO.get(
            (regime, ramo), (0, 0)
        )

        # --- Persistencia ---
        config = ConfiguracaoEscritorio(
            custo_fixo_mensal=custo_fixo,
            horas_produtivas_mes=horas_produtivas,
            margem_lucro_alvo=margem_lucro,
        )
        db.session.add(config)
        db.session.commit()

        precificacao = PrecificacaoCliente(
            nome_cliente=nome_empresa,
            regime_tributario=regime,
            ramo_atividade=ramo,
            volume_nfe=volume_nfe,
            num_funcionarios_socios=num_func,
            horas_estimadas_cliente=horas_cliente,
            valor_custo=piso_custo,
            valor_recomendado=valor_recomendado,
            mercado_min=mercado_min,
            mercado_max=mercado_max,
        )
        db.session.add(precificacao)
        db.session.commit()

        return jsonify({
            'piso_custo': round(piso_custo, 2),
            'valor_recomendado': round(valor_recomendado, 2),
            'mercado_min': round(mercado_min, 2),
            'mercado_max': round(mercado_max, 2),
            'horas_estimadas': round(horas_cliente, 1),
        })

    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Dados invalidos: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
