from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.models import SituacaoCurso, StatusEnum, Visita, Curso, Workshop
from ..auth.decorators import admin_required, login_required
from .. import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def painel_admin():
    return render_template('admin/painel.html')

@admin_bp.route('/visitas')
@login_required
@admin_required
def list_visitas():
    visitas = Visita.query.all()
    # Adiciona a contagem de participantes para cada visita
    for visita in visitas:
        visita.num_inscritos = len(visita.participantes.all())
    return render_template('visitas/list.html', visitas=visitas)

@admin_bp.route('/visitas/<int:visita_id>/inscritos')
@login_required
@admin_required
def ver_inscritos(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    participantes = visita.participantes.all()
    return render_template('visitas/inscritos.html', visita=visita, participantes=participantes)

@admin_bp.route('/visitas/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_visita():
    if request.method == 'POST':
        try:
            visita = Visita(
                nome=request.form.get('nome'),
                descricao=request.form.get('descricao'),
                data=datetime.strptime(request.form.get('data'), '%Y-%m-%d').date(),
                horario=datetime.strptime(request.form.get('horario'), '%H:%M').time(),
                link_inscricao=request.form.get('link_inscricao'),
                vagas_disponiveis=int(request.form.get('vagas_disponiveis')),
                status=StatusEnum[request.form.get('status').upper()]
            )
            
            db.session.add(visita)
            db.session.commit()
            flash('Visita criada com sucesso!', 'success')
            return redirect(url_for('admin.list_visitas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar visita: {str(e)}', 'danger')
    
    status_options = [status.value for status in StatusEnum]
    return render_template('visitas/form.html', status_options=status_options)

@admin_bp.route('/visitas/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_visita(id):
    visita = Visita.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            visita.nome = request.form.get('nome')
            visita.descricao = request.form.get('descricao')
            visita.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
            visita.horario = datetime.strptime(request.form.get('horario'), '%H:%M').time()
            visita.link_inscricao = request.form.get('link_inscricao')
            visita.vagas_disponiveis = int(request.form.get('vagas_disponiveis'))
            visita.status = StatusEnum[request.form.get('status').upper()]
            
            db.session.commit()
            flash('Visita atualizada com sucesso!', 'success')
            return redirect(url_for('admin.list_visitas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar visita: {str(e)}', 'danger')
    
    status_options = [status.value for status in StatusEnum]
    return render_template('visitas/form.html', visita=visita, status_options=status_options)

@admin_bp.route('/visitas/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_visita(id):
    visita = Visita.query.get_or_404(id)
    try:
        db.session.delete(visita)
        db.session.commit()
        flash('Visita excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir visita: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_visitas'))

@admin_bp.route('/cursos')
@login_required
@admin_required
def list_cursos():
    cursos = Curso.query.all()
    # Adiciona a contagem de participantes para cada curso
    for curso in cursos:
        curso.num_inscritos = len(curso.participantes.all())
    return render_template('cursos/list.html', cursos=cursos)

@admin_bp.route('/cursos/<int:curso_id>/inscritos')
@login_required
@admin_required
def ver_inscritos_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    participantes = curso.participantes.all()
    return render_template('cursos/inscritos.html', curso=curso, participantes=participantes)

@admin_bp.route('/cursos/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_curso():
    if request.method == 'POST':
        try:
            curso = Curso(
                nome=request.form.get('nome'),
                descricao=request.form.get('descricao'),
                data_inicio=datetime.strptime(request.form.get('data_inicio'), '%Y-%m-%d').date(),
                data_fim=datetime.strptime(request.form.get('data_fim'), '%Y-%m-%d').date(),
                horario=request.form.get('horario'),
                carga_horaria=request.form.get('carga_horaria'),
                local=request.form.get('local'),
                vagas_disponiveis=int(request.form.get('vagas_disponiveis')),
                situacao=SituacaoCurso[request.form.get('situacao').upper()]
            )
            
            db.session.add(curso)
            db.session.commit()
            flash('Curso criado com sucesso!', 'success')
            return redirect(url_for('admin.list_cursos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar curso: {str(e)}', 'danger')
    
    situacao_options = [situacao.value for situacao in SituacaoCurso]
    return render_template('cursos/form.html', situacao_options=situacao_options)

@admin_bp.route('/cursos/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_curso(id):
    curso = Curso.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            curso.nome = request.form.get('nome')
            curso.descricao = request.form.get('descricao')
            curso.data_inicio = datetime.strptime(request.form.get('data_inicio'), '%Y-%m-%d').date()
            curso.data_fim = datetime.strptime(request.form.get('data_fim'), '%Y-%m-%d').date()
            curso.horario = request.form.get('horario')
            curso.carga_horaria = request.form.get('carga_horaria')
            curso.local = request.form.get('local')
            curso.vagas_disponiveis = int(request.form.get('vagas_disponiveis'))
            curso.situacao = SituacaoCurso[request.form.get('situacao').upper()]
            
            db.session.commit()
            flash('Curso atualizado com sucesso!', 'success')
            return redirect(url_for('admin.list_cursos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar curso: {str(e)}', 'danger')
    
    situacao_options = [situacao.value for situacao in SituacaoCurso]
    return render_template('cursos/form.html', curso=curso, situacao_options=situacao_options)

@admin_bp.route('/cursos/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_curso(id):
    curso = Curso.query.get_or_404(id)
    try:
        db.session.delete(curso)
        db.session.commit()
        flash('Curso excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir curso: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_cursos'))

@admin_bp.route('/workshops')
@login_required
@admin_required
def list_workshops():
    workshops = Workshop.query.all()
    # Adiciona a contagem de participantes para cada workshop
    for workshop in workshops:
        workshop.num_inscritos = len(workshop.participantes.all())
    return render_template('workshops/list.html', workshops=workshops)

@admin_bp.route('/workshops/<int:workshop_id>/inscritos')
@login_required
@admin_required
def ver_inscritos_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    participantes = workshop.participantes.all()
    return render_template('workshops/inscritos.html', workshop=workshop, participantes=participantes)

@admin_bp.route('/workshops/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_workshop():
    if request.method == 'POST':
        try:
            workshop = Workshop(
                nome=request.form.get('nome'),
                descricao=request.form.get('descricao'),
                data=datetime.strptime(request.form.get('data'), '%Y-%m-%d').date(),
                horario=request.form.get('horario'),
                duracao=request.form.get('duracao'),
                local=request.form.get('local'),
                vagas_disponiveis=int(request.form.get('vagas_disponiveis')),
                status=SituacaoCurso[request.form.get('status').upper()]
            )
            
            db.session.add(workshop)
            db.session.commit()
            flash('Workshop criado com sucesso!', 'success')
            return redirect(url_for('admin.list_workshops'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar workshop: {str(e)}', 'danger')
    
    status_options = [status.value for status in SituacaoCurso]
    return render_template('workshops/form.html', status_options=status_options)

@admin_bp.route('/workshops/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_workshop(id):
    workshop = Workshop.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            workshop.nome = request.form.get('nome')
            workshop.descricao = request.form.get('descricao')
            workshop.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
            workshop.horario = request.form.get('horario')
            workshop.duracao = request.form.get('duracao')
            workshop.local = request.form.get('local')
            workshop.vagas_disponiveis = int(request.form.get('vagas_disponiveis'))
            workshop.status = SituacaoCurso[request.form.get('status').upper()]
            
            db.session.commit()
            flash('Workshop atualizado com sucesso!', 'success')
            return redirect(url_for('admin.list_workshops'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar workshop: {str(e)}', 'danger')
    
    status_options = [status.value for status in SituacaoCurso]
    return render_template('workshops/form.html', workshop=workshop, status_options=status_options)

@admin_bp.route('/workshops/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_workshop(id):
    workshop = Workshop.query.get_or_404(id)
    try:
        db.session.delete(workshop)
        db.session.commit()
        flash('Workshop excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir workshop: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_workshops'))