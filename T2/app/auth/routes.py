from flask import render_template, request, redirect, url_for, session, flash
from .services import AuthService
from flask import Blueprint
from app import db
from app.models import Estudante, Professor
from .utils import validar_cpf, validar_email_ufes
from .decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AuthService.login_user(
            request.form['email'],
            request.form['password']
        )
       
        if user:
            session['user'] = {
                'id': user.id,
                'name': user.name,
                'role': user.role,
                'type': user.type
            }
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
       
        flash('Credenciais inválidas ou conta desativada.', 'danger')
   
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'student':
            return redirect(url_for('auth.register_estudante'))
        elif user_type == 'professor':
            return redirect(url_for('auth.register_professor'))
   
    return render_template('auth/register.html')

@auth_bp.route('/register/estudante', methods=['GET', 'POST'])
def register_estudante():
    if request.method == 'POST':
        if not validar_cpf(request.form['cpf']):
            flash('CPF inválido.', 'error')
            return redirect(url_for('auth.register_estudante'))

        if not validar_email_ufes(request.form['email']):
            flash('Você precisa usar o e-mail institucional da UFES.', 'error')
            return redirect(url_for('auth.register_estudante'))
       
        try:
            estudante = AuthService.register_student(request.form)
            db.session.add(estudante)
            db.session.commit()
            flash('Cadastro de estudante realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro: {str(e)}', 'danger')
   
    return render_template('auth/register_estudante.html')

@auth_bp.route('/register/professor', methods=['GET', 'POST'])
def register_professor():
    if request.method == 'POST':
        if not validar_cpf(request.form['cpf']):
            flash('CPF inválido.', 'error')
            return redirect(url_for('auth.register_professor'))

        if not validar_email_ufes(request.form['email']):
            flash('Você precisa usar o e-mail institucional da UFES.', 'error')
            return redirect(url_for('auth.register_professor'))
       
        try:
            professor = AuthService.register_professor(request.form)
            db.session.add(professor)
            db.session.commit()
            flash('Cadastro de professor realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro: {str(e)}', 'danger')
   
    return render_template('auth/register_professor.html')