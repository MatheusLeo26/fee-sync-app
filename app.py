import os
from flask import Flask, render_template, request, jsonify
from models import db, ConfiguracaoEscritorio, PrecificacaoCliente

app = Flask(__name__)

# Configuração do banco de dados (SQLite local para facilitar)
base_dir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "fee_sync.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Cria as tabelas antes da primeira requisição
with app.app_context():
    db.create_all()

# Lógica estática para estimativas de horas e valor de mercado baseados no regime
DADOS_REGIME = {
    'mei': {
        'horas_estimadas': 2.0,
        'mercado_min': 150.0,
        'mercado_max': 300.0,
        'label_mercado': 'R$ 150 - R$ 300'
    },
    'simples': {
        'horas_estimadas': 5.0,
        'mercado_min': 500.0,
        'mercado_max': 1500.0,
        'label_mercado': 'R$ 500 - R$ 1.500'
    },
    'presumido': {
        'horas_estimadas': 10.0,
        'mercado_min': 1500.0,
        'mercado_max': 3000.0,
        'label_mercado': 'R$ 1.500 - R$ 3.000'
    },
    'real': {
        'horas_estimadas': 20.0,
        'mercado_min': 3000.0,
        'mercado_max': 10000.0,
        'label_mercado': 'R$ 3.000 - R$ 10.000'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calcular', methods=['POST'])
def calcular():
    data = request.json
    
    try:
        custo_fixo = float(data.get('custo_fixo', 0))
        horas_produtivas = int(data.get('horas_produtivas', 0))
        margem_lucro = float(data.get('margem_lucro', 0))
        nome_cliente = data.get('nome_cliente', 'Cliente Padrão')
        regime = data.get('regime', 'simples')
        
        if horas_produtivas <= 0:
            return jsonify({'error': 'Horas produtivas devem ser maiores que zero.'}), 400
        if margem_lucro >= 100:
            return jsonify({'error': 'Margem de lucro deve ser menor que 100%.'}), 400
            
        dados_regime = DADOS_REGIME.get(regime)
        if not dados_regime:
            return jsonify({'error': 'Regime tributário inválido.'}), 400
            
        horas_estimadas = dados_regime['horas_estimadas']
        
        # Lógica de cálculo
        custo_por_hora = custo_fixo / horas_produtivas
        piso_custo = custo_por_hora * horas_estimadas
        valor_recomendado = piso_custo / (1 - (margem_lucro / 100))
        
        # Salvar configuração do escritório no histórico (opcional para rastreabilidade)
        config = ConfiguracaoEscritorio(
            custo_fixo_mensal=custo_fixo,
            horas_produtivas_mes=horas_produtivas,
            margem_lucro_alvo=margem_lucro
        )
        db.session.add(config)
        db.session.commit() # Commit para gerar ID
        
        # Salvar cálculo do cliente
        precificacao = PrecificacaoCliente(
            nome_cliente=nome_cliente,
            regime_tributario=regime,
            horas_estimadas_cliente=horas_estimadas,
            valor_custo=piso_custo,
            valor_recomendado=valor_recomendado
        )
        db.session.add(precificacao)
        db.session.commit()
        
        return jsonify({
            'piso_custo': round(piso_custo, 2),
            'valor_recomendado': round(valor_recomendado, 2),
            'referencia_mercado': dados_regime['label_mercado']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
