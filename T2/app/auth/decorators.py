from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Você precisa estar logado para acessar esta página.')
            return redirect(url_for('main.login'))
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