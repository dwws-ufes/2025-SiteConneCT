from flask import redirect, url_for

def redirecionar_painel(user):
    if user.type == 'estudante':
        return redirect(url_for('estudante.painel'))
    elif user.type == 'professor':
        return redirect(url_for('professor.painel'))
    else:
        return redirect(url_for('main.index'))
