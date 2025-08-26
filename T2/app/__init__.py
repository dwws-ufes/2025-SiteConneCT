from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializa extensões
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Registra blueprints
    register_blueprints(app)

    return app

def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    from app.routes import main_bp, admin_bp, estudante_bp, professor_bp, user_bp, semantic_bp
    from app.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(estudante_bp, url_prefix='/estudante')
    app.register_blueprint(professor_bp, url_prefix='/professor')
    
    app.register_blueprint(semantic_bp, url_prefix='/semantic')