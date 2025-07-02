from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
import click

app = create_app()
migrate = Migrate(app, db)

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
