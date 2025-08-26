from functools import wraps
from flask import abort, session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Você precisa estar logado para acessar esta página.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'ADMIN':
            flash('Acesso restrito: apenas administradores.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('type') != 'professor':
            flash('Acesso restrito: apenas professores.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def estudante_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('type') != 'estudante':
            flash('Acesso restrito: apenas estudantes.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function



def linked_data_required(f):
    """Decorator para endpoints de Linked Data que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            abort(401, description="Autenticação necessária para acessar dados semânticos")
        return f(*args, **kwargs)
    return decorated_function

def check_resource_access(user, resource, resource_type):
    """Verifica se usuário tem acesso ao recurso"""
    if user.role == 'ADMIN':
        return True
        
    if resource_type == 'curso':
        return resource in user.cursos_inscritos
    elif resource_type == 'visita':
        return resource in user.visitas_inscritas
    elif resource_type == 'workshop':
        return resource in user.workshops_inscritos
    elif resource_type == 'apresentacao':
        return resource in user.apresentacoes_inscritas
        
    return False