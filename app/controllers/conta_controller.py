from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, session
from app.models.conta_model import ContaModel
from functools import wraps 

conta_bp = Blueprint("conta_bp", __name__, template_folder="../templates")

db = ContaModel()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')

            return redirect(url_for('usuario_bp.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@conta_bp.route("/", methods=["GET", "POST"])
@login_required 
def index():
    username = session['username'] 
    search = request.form.get("search", "")
    contas = db.get_all(username=username, search_term=search) 
    return render_template("index.html", contas=contas, search=search)

@conta_bp.route("/adicionar", methods=["GET", "POST"])
@login_required 
def adicionar():
    username = session['username'] 
    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "senha_login": request.form.get("senha_login"),
            "senha_email": request.form.get("senha_email"),
            "provedor": request.form.get("provedor"),
            "observacoes": request.form.get("observacoes")
        }

        if not data["email"] or not data["senha_login"] or not data["senha_email"]:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("adicionar.html", data=data)

        db.create(data, username) 
        flash("Conta adicionada com sucesso!", "success")
        return redirect(url_for("conta_bp.index"))

    return render_template("adicionar.html")

@conta_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required 
def editar(id):
    username = session['username'] 
    conta = db.get_by_id(id, username) 

    if not conta:
        flash("Conta não encontrada ou você não tem permissão para editar.", "error") 
        return redirect(url_for("conta_bp.index"))

    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "senha_login": request.form.get("senha_login"),
            "senha_email": request.form.get("senha_email"),
            "provedor": request.form.get("provedor"),
            "observacoes": request.form.get("observacoes")
        }

        if not data["email"] or not data["senha_login"] or not data["senha_email"]:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("editar.html", conta=data)

        db.update(id, data, username) 
        flash("Conta atualizada com sucesso!", "success")
        return redirect(url_for("conta_bp.index"))

    return render_template("editar.html", conta=conta)

@conta_bp.route("/excluir/<int:id>", methods=["POST"])
@login_required 
def excluir(id):
    username = session['username'] 
    db.delete(id, username) 
    flash("Conta excluída com sucesso!", "success")
    return redirect(url_for("conta_bp.index"))

@conta_bp.route("/exportar")
@login_required 
def exportar():
    username = session['username'] 
    contas = db.get_all(username=username) 
    txt = ""

    for c in contas:
        txt += (
            f"ID: {c['id']}\n"
            f"Email: {c['email']}\n"
            f"Senha Login: {c['senha_login']}\n"
            f"Senha Email: {c['senha_email']}\n"
            f"Provedor: {c.get('provedor') or 'N/A'}\n"
            f"Observações:\n{c.get('observacoes') or 'Nenhuma'}\n"
            + "-" * 40 + "\n\n"
        )

    return Response(
        txt,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=contas.txt"}
    )