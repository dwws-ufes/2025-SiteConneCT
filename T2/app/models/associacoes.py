from .. import db
from datetime import datetime

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

apresentacao_inscricao = db.Table('apresentacao_inscricao',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('apresentacao_id', db.Integer, db.ForeignKey('apresentacao.id'), primary_key=True),
    db.Column('data_inscricao', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='confirmada')
)