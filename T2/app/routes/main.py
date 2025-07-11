from flask import Blueprint, render_template, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user = session.get('user')
    return render_template('home/index.html', user=user)

@main_bp.route('/quemsomos')
def quemsomos():
    return render_template('home/quemsomos.html')

@main_bp.route('/comofunciona')
def comofunciona():
    return render_template('home/comofunciona.html')

@main_bp.route('/projetos')
def projetos():
    return render_template('home/projetos.html')

@main_bp.route('/depoimentos')
def depoimentos():
    return render_template('home/depoimentos.html')

@main_bp.route('/desafios')
def desafios():
    return render_template('home/desafios.html')

@main_bp.route('/espaco')
def espaco():
    return render_template('home/espaco.html')