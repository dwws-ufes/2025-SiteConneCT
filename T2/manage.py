from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask.cli import with_appcontext
from app import create_app, db
import click

app = create_app()
migrate = Migrate(app, db)

# Expor o comando flask db corretamente
@app.cli.command("db-init")
@with_appcontext
def db_init():
    """Inicializa a pasta de migração"""
    from flask_migrate import init
    init()

@app.cli.command("db-migrate")
@with_appcontext
@click.argument("message")
def db_migrate(message):
    """Cria uma migração com mensagem"""
    from flask_migrate import migrate
    migrate(message=message)

@app.cli.command("db-upgrade")
@with_appcontext
def db_upgrade():
    """Aplica as migrações"""
    from flask_migrate import upgrade
    upgrade()
