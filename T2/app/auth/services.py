from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models import User, Estudante, Professor
from app import db

class AuthService:
    @staticmethod
    def login_user(email, password):
        """Autentica um usuário"""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password) and user.ativo:
            return user
        return None

    @staticmethod
    def register_student(form_data):
        """Registra um novo estudante"""
        if User.query.filter((User.email == form_data['email']) | (User.cpf == form_data['cpf'])).first():
            raise ValueError('E-mail ou CPF já cadastrado.')
       
        if not form_data['numero_matricula'].isdigit():
            raise ValueError('Número de matrícula deve conter apenas dígitos.')
       
        estudante = Estudante(
            name=form_data['name'],
            email=form_data['email'],
            celular=form_data['celular'],
            cpf=form_data['cpf'],
            role='STUDENT',
            curso=form_data['curso'],
            numero_matricula=form_data['numero_matricula'],
            data_entrada_ufes=datetime.strptime(form_data['data_entrada_ufes'], '%Y-%m-%d'),
        )
        estudante.set_password(form_data['password'])
        return estudante

    @staticmethod
    def register_professor(form_data):
        """Registra um novo professor"""
        if User.query.filter((User.email == form_data['email']) | (User.cpf == form_data['cpf'])).first():
            raise ValueError('E-mail ou CPF já cadastrado.')
       
        professor = Professor(
            name=form_data['name'],
            email=form_data['email'],
            celular=form_data['celular'],
            cpf=form_data['cpf'],
            role='PROFESSOR',
            siape=form_data['siape'],
        )
        professor.set_password(form_data['password'])
        return professor

    @staticmethod
    def get_current_user():
        """Retorna o usuário atual baseado na sessão"""
        from flask import session
        if 'user' in session:
            return User.query.get(session['user']['id'])
        return None

    @staticmethod
    def is_authenticated():
        """Verifica se o usuário está autenticado"""
        return 'user' in session

    @staticmethod
    def is_admin():
        """Verifica se o usuário é admin"""
        return session.get('user', {}).get('role') == 'ADMIN'