from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.models.conta_model import ContaModel

conta_bp = Blueprint('conta_bp', __name__, template_folder='../templates')

db_model = ContaModel()

@conta_bp.route("/", methods=["GET", "POST"])
def index():
    search = request.form.get("search", "")
    contas = db_model.get_all(search_term=search)
    return render_template("index.html", contas=contas, search=search)

@conta_bp.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        if not request.form['email'] or not request.form['senha_ubisoft'] or not request.form['senha_email']:
            flash('Email e ambas as senhas são obrigatórios!', 'error')
        else:
            nova_conta_data = {k: v for k, v in request.form.items()}
            db_model.create(nova_conta_data)
            flash('Conta adicionada com sucesso!', 'success')
            return redirect(url_for('conta_bp.index'))
    return render_template("adicionar.html")

@conta_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        if not request.form['email'] or not request.form['senha_ubisoft'] or not request.form['senha_email']:
            flash('Email e ambas as senhas são obrigatórios!', 'error')
        else:
            conta_data = {k: v for k, v in request.form.items()}
            db_model.update(id, conta_data)
            flash('Conta atualizada com sucesso!', 'success')
            return redirect(url_for('conta_bp.index'))

    conta = db_model.get_by_id(id)
    if conta is None:
        flash('Conta não encontrada!', 'error')
        return redirect(url_for('conta_bp.index'))
    return render_template("editar.html", conta=conta)

@conta_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    db_model.delete(id)
    flash('Conta excluída com sucesso!', 'success')
    return redirect(url_for('conta_bp.index'))

@conta_bp.route("/exportar")
def exportar():
    contas = db_model.get_all()
    txt_content = ""
    for conta in contas:
        txt_content += f"ID: {conta['id']}\n"
        txt_content += f"Email: {conta['email']}\n"
        txt_content += f"Senha Ubisoft: {conta['senha_ubisoft']}\n"
        txt_content += f"Senha Email: {conta['senha_email']}\n"
        txt_content += f"Provedor: {conta.get('provedor') or 'N/A'}\n"
        txt_content += f"Jogos:\n{conta.get('jogos') or 'Nenhum'}\n"
        txt_content += f"Observações:\n{conta.get('observacoes') or 'Nenhuma'}\n"
        txt_content += "-" * 40 + "\n\n"
    
    return Response(
        txt_content,
        mimetype='text/plain',
        headers={'Content-disposition': 'attachment; filename=contas_ubisoft.txt'}
    )