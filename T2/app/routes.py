from flask import Blueprint, abort, render_template, request, redirect, session, url_for, flash
from .models import Curso, SituacaoCurso, User, Workshop
from . import db
from .models import Visita, StatusEnum, Estudante, Professor
from datetime import datetime
from .auth import estudante_required, login_required, admin_required, professor_required
from .util import redirecionar_painel, validar_cpf, validar_email_ufes

main = Blueprint('main', __name__)

@main.route('/')
def index():
    user = session.get('user')
    return render_template('home/index.html', user=user)

@main.route('/quemsomos')
def quemsomos():
    return render_template('home/quemsomos.html')

@main.route('/comofunciona')
def comofunciona():
    return render_template('home/comofunciona.html')

@main.route('/projetos')
def projetos():
    return render_template('home/projetos.html')

@main.route('/depoimentos')
def depoimentos():
    return render_template('home/depoimentos.html')

@main.route('/desafios')
def desafios():
    return render_template('home/desafios.html')

@main.route('/espaco')
def espaco():
    return render_template('home/espaco.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']
        user = User.query.filter_by(cpf=cpf).first()
        if user and user.check_password(password) and user.ativo:
            session['user'] = {
                'id': user.id,
                'name': user.name,
                'role': user.role,
                'type': user.type  # aqui é o que permite os novos decoradores funcionarem
            }
            print("login realizado com sucesso!")
            return redirect(url_for('main.index'))
        flash('Credenciais inválidas ou conta desativada.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Se o formulário for submetido com a escolha do tipo de usuário
        user_type = request.form.get('user_type')
        if user_type == 'student':
            return redirect(url_for('main.register_estudante'))
        elif user_type == 'professor':
            return redirect(url_for('main.register_professor'))
    
    # Se for GET ou nenhuma opção selecionada ainda
    return render_template('register.html')

@main.route('/register/estudante', methods=['GET', 'POST'])
def register_estudante():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        celular = request.form['celular']
        cpf = request.form['cpf']
        password = request.form['password']
        curso = request.form['curso']
        numero_matricula = request.form['numero_matricula']
        data_entrada = request.form['data_entrada_ufes']

        if not validar_cpf(cpf):
            flash('CPF inválido.', 'error')
            return redirect(url_for('main.register_estudante'))

        if not validar_email_ufes(email):
            flash('Você precisa usar o e-mail institucional da UFES.', 'error')
            return redirect(url_for('main.register_estudante'))
        
        if not numero_matricula.isdigit():
            flash('Número de matrícula deve conter apenas dígitos.', 'error')
            return redirect(url_for('main.register_estudante'))

        if User.query.filter((User.email == email) | (User.cpf == cpf)).first():
            flash('E-mail ou CPF já cadastrado.', 'error')
            return redirect(url_for('main.register_estudante'))

        estudante = Estudante(
            name=name,
            email=email,
            celular=celular,
            cpf=cpf,
            role='STUDENT',
            curso=curso,
            numero_matricula=numero_matricula,
            data_entrada_ufes=datetime.strptime(data_entrada, '%Y-%m-%d'),
        )
        estudante.set_password(password)
        db.session.add(estudante)
        db.session.commit()
        flash('Cadastro de estudante realizado com sucesso!', 'success')
        return redirect(url_for('main.login'))

    return render_template('registro/register_estudante.html')

@main.route('/register/professor', methods=['GET', 'POST'])
def register_professor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        celular = request.form['celular']
        cpf = request.form['cpf']
        password = request.form['password']
        siape = request.form['siape']

        if not validar_cpf(cpf):
            flash('CPF inválido.', 'error')
            return redirect(url_for('main.register_professor'))

        if not validar_email_ufes(email):
            flash('Você precisa usar o e-mail institucional da UFES.', 'error')
            return redirect(url_for('main.register_professor'))

        if User.query.filter((User.email == email) | (User.cpf == cpf)).first():
            flash('E-mail ou CPF já cadastrado.', 'error')
            return redirect(url_for('main.register_professor'))

        professor = Professor(
            name=name,
            email=email,
            celular=celular,
            cpf=cpf,
            role='PROFESSOR',
            siape=siape,
        )
        professor.set_password(password)
        db.session.add(professor)
        db.session.commit()
        flash('Cadastro de professor realizado com sucesso!', 'success')
        return redirect(url_for('main.login'))

    return render_template('registro/register_professor.html')

@main.route('/admin/visitas')
@login_required
@admin_required
def list_visitas():
    visitas = Visita.query.all()
    # Adiciona a contagem de participantes para cada visita
    for visita in visitas:
        visita.num_inscritos = len(visita.participantes.all())
    return render_template('visitas/list.html', visitas=visitas)

@main.route('/admin/visitas/<int:visita_id>/inscritos')
@login_required
@admin_required
def ver_inscritos(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    participantes = visita.participantes.all()
    return render_template('visitas/inscritos.html', visita=visita, participantes=participantes)

@main.route('/admin/visitas/new', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_visitas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar visita: {str(e)}', 'danger')
    
    status_options = [status.value for status in StatusEnum]
    return render_template('visitas/form.html', status_options=status_options)

@main.route('/admin/visitas/<int:id>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_visitas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar visita: {str(e)}', 'danger')
    
    status_options = [status.value for status in StatusEnum]
    return render_template('visitas/form.html', visita=visita, status_options=status_options)

@main.route('/admin/visitas/<int:id>/delete', methods=['POST'])
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
    
    return redirect(url_for('main.list_visitas'))

@main.route('/admin/cursos')
@login_required
@admin_required
def list_cursos():
    cursos = Curso.query.all()
    # Adiciona a contagem de participantes para cada curso
    for curso in cursos:
        curso.num_inscritos = len(curso.participantes.all())
    return render_template('cursos/list.html', cursos=cursos)

@main.route('/admin/cursos/<int:curso_id>/inscritos')
@login_required
@admin_required
def ver_inscritos_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    participantes = curso.participantes.all()
    return render_template('cursos/inscritos.html', curso=curso, participantes=participantes)

@main.route('/admin/cursos/new', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_cursos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar curso: {str(e)}', 'danger')
    
    situacao_options = [situacao.value for situacao in SituacaoCurso]
    return render_template('cursos/form.html', situacao_options=situacao_options)

@main.route('/admin/cursos/<int:id>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_cursos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar curso: {str(e)}', 'danger')
    
    situacao_options = [situacao.value for situacao in SituacaoCurso]
    return render_template('cursos/form.html', curso=curso, situacao_options=situacao_options)

@main.route('/admin/cursos/<int:id>/delete', methods=['POST'])
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
    
    return redirect(url_for('main.list_cursos'))

@main.route('/admin/workshops')
@login_required
@admin_required
def list_workshops():
    workshops = Workshop.query.all()
    # Adiciona a contagem de participantes para cada workshop
    for workshop in workshops:
        workshop.num_inscritos = len(workshop.participantes.all())
    return render_template('workshops/list.html', workshops=workshops)

@main.route('/admin/workshops/<int:workshop_id>/inscritos')
@login_required
@admin_required
def ver_inscritos_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    participantes = workshop.participantes.all()
    return render_template('workshops/inscritos.html', workshop=workshop, participantes=participantes)

@main.route('/admin/workshops/new', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_workshops'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar workshop: {str(e)}', 'danger')
    
    status_options = [status.value for status in SituacaoCurso]
    return render_template('workshops/form.html', status_options=status_options)

@main.route('/admin/workshops/<int:id>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('main.list_workshops'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar workshop: {str(e)}', 'danger')
    
    status_options = [status.value for status in SituacaoCurso]
    return render_template('workshops/form.html', workshop=workshop, status_options=status_options)

@main.route('/admin/workshops/<int:id>/delete', methods=['POST'])
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
    
    return redirect(url_for('main.list_workshops'))

@main.route('/painel_estudante')
@login_required
@estudante_required
def painel_estudante():
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
    
    # Atividades já inscritas
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

@main.route('/painel_professor')
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


# Rotas para inscrição
@main.route('/inscrever/curso/<int:curso_id>', methods=['POST'])
@login_required
def inscrever_curso(curso_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    curso = Curso.query.get_or_404(curso_id)
    
    if curso.situacao != 'ABERTO':
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

@main.route('/cancelar/curso/<int:curso_id>', methods=['POST'])
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

@main.route('/inscrever/visita/<int:visita_id>', methods=['POST'])
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

@main.route('/cancelar/visita/<int:visita_id>', methods=['POST'])
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
@main.route('/inscrever/workshop/<int:workshop_id>', methods=['POST'])
@login_required
def inscrever_workshop(workshop_id):
    user_id = session['user']['id']
    user = User.query.get(user_id)
    workshop = Workshop.query.get_or_404(workshop_id)
    
    if workshop.status != 'ABERTO':
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
@main.route('/cancelar/workshop/<int:workshop_id>', methods=['POST'])
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

@main.route('/admin')
@login_required
@admin_required
def painel_admin():
    return render_template('admin/painel.html')