from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ConfiguracaoEscritorio(db.Model):
    """
    Armazena os parâmetros base do escritório de contabilidade.
    Esses dados são usados para calcular o custo por hora.
    """
    __tablename__ = 'configuracao_escritorio'
    
    id = db.Column(db.Integer, primary_key=True)
    custo_fixo_mensal = db.Column(db.Float, nullable=False)
    horas_produtivas_mes = db.Column(db.Integer, nullable=False)
    margem_lucro_alvo = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<ConfiguracaoEscritorio {self.id}>"


class PrecificacaoCliente(db.Model):
    """
    Armazena o histórico de cálculos feitos para os clientes,
    guardando também os resultados para referência futura.
    """
    __tablename__ = 'precificacao_cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(150), nullable=False)
    regime_tributario = db.Column(db.String(50), nullable=False)
    horas_estimadas_cliente = db.Column(db.Float, nullable=False)
    valor_custo = db.Column(db.Float, nullable=False)
    valor_recomendado = db.Column(db.Float, nullable=False)
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PrecificacaoCliente {self.nome_cliente}>"
