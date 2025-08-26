from flask import Blueprint
from .admin import admin_bp
from .estudante import estudante_bp
from .professor import professor_bp
from .main import main_bp
from .user import user_bp

from .linked_data import semantic_bp

def init_app(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(estudante_bp, url_prefix='/estudante')
    app.register_blueprint(professor_bp, url_prefix='/professor')
    
    app.register_blueprint(semantic_bp, url_prefix='/semantic')