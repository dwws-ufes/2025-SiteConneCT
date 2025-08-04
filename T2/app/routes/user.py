from app.models.user import User
from ..util import redirecionar_painel
from flask import Blueprint, flash, session
from app.models import SituacaoCurso, StatusEnum, Visita, Curso, Workshop, Apresentacao
from ..auth.decorators import login_required
from .. import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/inscrever/curso/<int:curso_id>', methods=['POST'])
@login_required
def inscrever_curso(curso_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    curso = Curso.query.get_or_404(curso_id)
    
    if curso.situacao != SituacaoCurso.ABERTO:
        flash('Este curso não está aberto para inscrições.', 'error')
        return redirecionar_painel(user)

    if curso in user.cursos_inscritos:
        flash('Você já está inscrito neste curso.', 'warning')
        return redirecionar_painel(user)

    if curso.vagas_disponiveis <= curso.participantes.count():
        flash('Vagas esgotadas para este curso.', 'error')
        return redirecionar_painel(user)

    user.cursos_inscritos.append(curso)
    db.session.commit()
    
    flash('Inscrição no curso realizada com sucesso!', 'success')
    return redirecionar_painel(user)

@user_bp.route('/cancelar/curso/<int:curso_id>', methods=['POST'])
@login_required
def cancelar_inscricao_curso(curso_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    curso = Curso.query.get_or_404(curso_id)

    if curso not in user.cursos_inscritos:
        flash('Você não está inscrito neste curso.', 'error')
        return redirecionar_painel(user)

    user.cursos_inscritos.remove(curso)
    db.session.commit()

    flash('Inscrição cancelada com sucesso.', 'success')
    return redirecionar_painel(user)

@user_bp.route('/inscrever/visita/<int:visita_id>', methods=['POST'])
@login_required
def inscrever_visita(visita_id):
    user_id = session['user']['id']
    user = User.query.get(user_id) 
    visita = Visita.query.get_or_404(visita_id)
    
    if visita.status != StatusEnum.CONFIRMADA:
        flash('Esta visita não está disponível para inscrições.', 'error')
        return redirecionar_painel(user)
    
    if visita in user.visitas_inscritas: 
        flash('Você já está inscrito nesta visita.', 'warning')
        return redirecionar_painel(user)
    
    # Verifica vagas
    if visita.vagas_disponiveis <= len(visita.participantes.all()):
        flash('Vagas esgotadas para esta visita.', 'error')
        return redirecionar_painel(user)
    
    # Realiza inscrição
    user.visitas_inscritas.append(visita)
    db.session.commit()
    
    flash('Inscrição na visita realizada com sucesso!', 'success')
    return redirecionar_painel(user)

@user_bp.route('/cancelar/visita/<int:visita_id>', methods=['POST'])
@login_required
def cancelar_inscricao_visita(visita_id):
    user_id = session['user']['id']
    visita = Visita.query.get_or_404(visita_id)
    user = User.query.get(user_id)
    
    if visita not in user.visitas_inscritas:
        flash('Você não está inscrito nesta visita.', 'error')
        return redirecionar_painel(user)
    
    user.visitas_inscritas.remove(visita)
    db.session.commit()
    
    flash('Inscrição na visita cancelada com sucesso.', 'success')
    return redirecionar_painel(user)

# Rotas para inscrição em workshop
@user_bp.route('/inscrever/workshop/<int:workshop_id>', methods=['POST'])
@login_required
def inscrever_workshop(workshop_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    workshop = Workshop.query.get_or_404(workshop_id)
    
    if workshop.status != SituacaoCurso.ABERTO:
        flash('Este workshop não está aberto para inscrições.', 'error')
        return redirecionar_painel(user)

    if workshop in user.workshops_inscritos:
        flash('Você já está inscrito neste workshop.', 'warning')
        return redirecionar_painel(user)

    if workshop.vagas_disponiveis <= workshop.participantes.count():
        flash('Vagas esgotadas para este workshop.', 'error')
        return redirecionar_painel(user)

    user.workshops_inscritos.append(workshop)
    db.session.commit()
    
    flash('Inscrição no workshop realizada com sucesso!', 'success')
    return redirecionar_painel(user)

# Rota para cancelamento de inscrição em workshop
@user_bp.route('/cancelar/workshop/<int:workshop_id>', methods=['POST'])
@login_required
def cancelar_inscricao_workshop(workshop_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    workshop = Workshop.query.get_or_404(workshop_id)

    if workshop not in user.workshops_inscritos:
        flash('Você não está inscrito neste workshop.', 'error')
        return redirecionar_painel(user)

    user.workshops_inscritos.remove(workshop)
    db.session.commit()

    flash('Inscrição no workshop cancelada com sucesso.', 'success')
    return redirecionar_painel(user)

@user_bp.route('/inscrever/apresentacao/<int:apresentacao_id>', methods=['POST'])
@login_required
def inscrever_apresentacao(apresentacao_id):
    user_id = session['user']['id']
    user = User.query.get(user_id) 
    apresentacao = Apresentacao.query.get_or_404(apresentacao_id)
    
    if apresentacao.status != StatusEnum.CONFIRMADA:
        flash('Esta apresentação não está disponível para inscrições.', 'error')
        return redirecionar_painel(user)
    
    if apresentacao in user.apresentacoes_inscritas: 
        flash('Você já está inscrito nesta apresentação.', 'warning')
        return redirecionar_painel(user)
    
    # Verifica vagas
    if apresentacao.vagas_disponiveis <= len(apresentacao.participantes.all()):
        flash('Vagas esgotadas para esta apresentação.', 'error')
        return redirecionar_painel(user)
    
    # Realiza inscrição
    user.apresentacoes_inscritas.append(apresentacao)
    db.session.commit()
    
    flash('Inscrição na apresentação realizada com sucesso!', 'success')
    return redirecionar_painel(user)

@user_bp.route('/cancelar/apresentacao/<int:apresentacao_id>', methods=['POST'])
@login_required
def cancelar_inscricao_apresentacao(apresentacao_id):
    user_id = session['user']['id']
    apresentacao = Apresentacao.query.get_or_404(apresentacao_id)
    user = User.query.get(user_id)
    
    if apresentacao not in user.apresentacao_inscritas:
        flash('Você não está inscrito nesta apresentação.', 'error')
        return redirecionar_painel(user)
    
    user.apresentacoes_inscritas.remove(apresentacao)
    db.session.commit()
    
    flash('Inscrição na apresentação cancelada com sucesso.', 'success')
    return redirecionar_painel(user)