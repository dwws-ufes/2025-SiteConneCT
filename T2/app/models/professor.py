from .user import User
from .. import db

class Professor(User):
    __tablename__ = 'professor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    siape = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'professor',
    }