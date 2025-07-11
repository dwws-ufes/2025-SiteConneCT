from .routes import auth_bp
from .decorators import login_required, admin_required, estudante_required, professor_required
from .utils import validar_email_ufes

def init_app(app):
    app.register_blueprint(auth_bp)

__all__ = [
    'auth_bp',
    'login_required',
    'admin_required',
    'estudante_required',
    'professor_required',
    'validar_email_ufes'  # Substitui o validar_cpf que não será mais usado no login
]