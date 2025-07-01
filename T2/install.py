from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()
with app.app_context():
    if not User.query.filter_by(cpf='000.000.000-00').first():
        admin = User(
            name="Admin",
            email="admin@ufes.br",  # Use um email válido do seu domínio
            cpf="000.000.000-00",  # CPF sem pontuação para consistência
            celular="27999999999",
            data_cadastro=datetime.utcnow(),
            ativo=True,
            role="ADMIN"
        )
        admin.set_password("SenhaAdmin123")  # Use uma senha mais segura
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso.")
    else:
        print("Admin já existente.")
