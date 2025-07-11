from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .associacoes import (visita_inscricao, curso_inscricao, workshop_inscricao)

class User(db.Model):
    __tablename__ = 'user'
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Campo único para login
    celular = db.Column(db.String(20), nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True)  # Opcional após mudança
    password_hash = db.Column(db.String(128), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='USER')
    email_confirmado = db.Column(db.Boolean, default=False)  # Novo campo

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