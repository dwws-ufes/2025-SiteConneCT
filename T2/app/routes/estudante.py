from flask import Blueprint, render_template, session
from app.models import Estudante, Curso
from app.models.atividade import Visita, Workshop
from ..auth.decorators import estudante_required, login_required

estudante_bp = Blueprint('estudante', __name__)

@estudante_bp.route('/painel')
@login_required
@estudante_required
def painel():
    user_id = session['user']['id']
    estudante = Estudante.query.get(user_id)
    
    # Atividades disponíveis (não inscritas)
    cursos_disponiveis = Curso.query.filter(
        Curso.situacao == 'ABERTO',
        ~Curso.participantes.any(id=user_id)
    ).all()
    
    visitas_disponiveis = Visita.query.filter(
        Visita.status == 'CONFIRMADA',
        ~Visita.participantes.any(id=user_id)
    ).all()
    
    workshops_disponiveis = Workshop.query.filter(
        Workshop.status == 'ABERTO',
        ~Workshop.participantes.any(id=user_id)
    ).all()

    cursos_inscritos = estudante.cursos_inscritos
    visitas_inscritas = estudante.visitas_inscritas
    workshops_inscritos = estudante.workshops_inscritos

    return render_template(
        'estudante/painel.html',
        cursos_disponiveis=cursos_disponiveis,
        visitas_disponiveis=visitas_disponiveis,
        workshops_disponiveis=workshops_disponiveis,
        cursos_inscritos=cursos_inscritos,
        visitas_inscritas=visitas_inscritas,
        workshops_inscritos=workshops_inscritos
    )