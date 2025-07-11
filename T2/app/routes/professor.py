from flask import Blueprint, render_template, session
from app.models import Professor
from app.models.atividade import Curso, Visita, Workshop
from ..auth.decorators import login_required, professor_required

professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/painel')
@login_required
@professor_required
def painel_professor():
    user_id = session['user']['id']
    professor = Professor.query.get(user_id)
    
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
    
    # Atividades já inscritas
    cursos_inscritos = professor.cursos_inscritos
    visitas_inscritas = professor.visitas_inscritas
    workshops_inscritos = professor.workshops_inscritos

    return render_template(
        'professor/painel.html',
        cursos_disponiveis=cursos_disponiveis,
        visitas_disponiveis=visitas_disponiveis,
        workshops_disponiveis=workshops_disponiveis,
        cursos_inscritos=cursos_inscritos,
        visitas_inscritas=visitas_inscritas,
        workshops_inscritos=workshops_inscritos
    )
