from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from sqlalchemy import Enum as PgEnum
from datetime import datetime
from sqlalchemy import JSON

visita_inscricao = db.Table('visita_inscricao',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('visita_id', db.Integer, db.ForeignKey('visita.id'), primary_key=True),
    db.Column('data_inscricao', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='confirmada')
)

curso_inscricao = db.Table('curso_inscricao',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('curso_id', db.Integer, db.ForeignKey('curso.id'), primary_key=True),
    db.Column('data_inscricao', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='confirmada')
)

workshop_inscricao = db.Table('workshop_inscricao',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.id'), primary_key=True),
    db.Column('data_inscricao', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='confirmada')
)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    celular = db.Column(db.String(20), nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  
    password_hash = db.Column(db.String(128), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='USER')

    type = db.Column(db.String(50)) 
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    visitas_inscritas = db.relationship(
        'Visita',
        secondary=visita_inscricao,
        backref=db.backref('participantes', lazy='dynamic')
    )
    
    cursos_inscritos = db.relationship(
        'Curso',
        secondary=curso_inscricao,
        backref=db.backref('participantes', lazy='dynamic')
    )
    
    workshops_inscritos = db.relationship(
        'Workshop',
        secondary=workshop_inscricao,
        backref=db.backref('participantes', lazy='dynamic')
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Estudante(User):
    __tablename__ = 'estudante'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    curso = db.Column(db.String(100), nullable=False)
    numero_matricula = db.Column(db.String(50), nullable=False)
    data_entrada_ufes = db.Column(db.Date, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'estudante',
    }


class Professor(User):
    __tablename__ = 'professor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    siape = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'professor',
    }


class StatusEnum(str, Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    REALIZADA = "REALIZADA"

class SituacaoCurso(str, Enum):
    ABERTO = "ABERTO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"

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