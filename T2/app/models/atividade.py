from .. import db
from .enums import StatusEnum, SituacaoCurso
from sqlalchemy import Enum as PgEnum

class Visita(db.Model):
    __tablename__ = 'visita'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    link_inscricao = db.Column(db.String(255), nullable=False)
    vagas_disponiveis = db.Column(db.Integer, nullable=False)
    status = db.Column(PgEnum(StatusEnum), nullable=False, default=StatusEnum.CONFIRMADA)

class Curso(db.Model):
    __tablename__ = 'curso'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    carga_horaria = db.Column(db.String(50), nullable=False)
    local = db.Column(db.String(120), nullable=False)
    vagas_disponiveis = db.Column(db.Integer, nullable=False)
    situacao = db.Column(PgEnum(SituacaoCurso), nullable=False, default=SituacaoCurso.ABERTO)

class Workshop(db.Model):
    __tablename__ = 'workshop'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    duracao = db.Column(db.String(20), nullable=False)
    local = db.Column(db.String(100), nullable=False)
    vagas_disponiveis = db.Column(db.Integer, nullable=False)
    status = db.Column(PgEnum(SituacaoCurso), nullable=False, default=SituacaoCurso.ABERTO)

class Apresentacao(db.Model):
    __tablename__ = 'apresentacao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    link_inscricao = db.Column(db.String(255), nullable=False)
    vagas_disponiveis = db.Column(db.Integer, nullable=False)
    status = db.Column(PgEnum(StatusEnum), nullable=False, default=StatusEnum.CONFIRMADA) 