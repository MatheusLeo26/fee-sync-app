from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class ConfiguracaoEscritorio(db.Model):
    """
    Armazena os parametros base do escritorio de contabilidade.
    Esses dados sao usados para calcular o custo por hora.
    """
    __tablename__ = 'configuracao_escritorio'

    id = db.Column(db.Integer, primary_key=True)
    custo_fixo_mensal = db.Column(db.Float, nullable=False)
    horas_produtivas_mes = db.Column(db.Integer, nullable=False)
    margem_lucro_alvo = db.Column(db.Float, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ConfiguracaoEscritorio {self.id}>"


class PrecificacaoCliente(db.Model):
    """
    Armazena o historico de calculos feitos para os clientes,
    guardando os parametros de entrada e os resultados para referencia futura.
    """
    __tablename__ = 'precificacao_cliente'

    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(150), nullable=False)
    regime_tributario = db.Column(db.String(50), nullable=False)
    ramo_atividade = db.Column(db.String(50), nullable=False)
    volume_nfe = db.Column(db.String(20), nullable=False)
    num_funcionarios_socios = db.Column(db.Integer, nullable=False)
    horas_estimadas_cliente = db.Column(db.Float, nullable=False)
    valor_custo = db.Column(db.Float, nullable=False)
    valor_recomendado = db.Column(db.Float, nullable=False)
    mercado_min = db.Column(db.Float, nullable=False)
    mercado_max = db.Column(db.Float, nullable=False)
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PrecificacaoCliente {self.nome_cliente}>"
