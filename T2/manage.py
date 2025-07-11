from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
import click

app = create_app()
migrate = Migrate(app, db)

<<<<<<< HEAD
# Comandos personalizados atualizados
=======
>>>>>>> 8e478d7ad4ba7b5f7ba993a30ee57d6a48b4935e
@app.cli.command("db-init")
def db_init():
    """Inicializa a pasta de migração"""
    from flask_migrate import init
    init()

@app.cli.command("db-migrate")
@click.argument("message")
def db_migrate(message):
    """Cria uma migração com mensagem"""
    from flask_migrate import migrate as _migrate
    _migrate(message=message)

@app.cli.command("db-upgrade")
def db_upgrade():
    """Aplica as migrações"""
    from flask_migrate import upgrade
    upgrade()