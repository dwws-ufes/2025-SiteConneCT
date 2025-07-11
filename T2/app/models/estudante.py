from .user import User
from .. import db

class Estudante(User):
    __tablename__ = 'estudante'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    curso = db.Column(db.String(100), nullable=False)
    numero_matricula = db.Column(db.String(50), nullable=False)
    data_entrada_ufes = db.Column(db.Date, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'estudante',
    }