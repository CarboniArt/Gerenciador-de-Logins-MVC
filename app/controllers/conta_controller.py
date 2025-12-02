from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.models.conta_model import ContaModel

conta_bp = Blueprint("conta_bp", __name__, template_folder="../templates")

db = ContaModel()

@conta_bp.route("/", methods=["GET", "POST"])
def index():
    search = request.form.get("search", "")
    contas = db.get_all(search_term=search)
    return render_template("index.html", contas=contas, search=search)

@conta_bp.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "senha_ubisoft": request.form.get("senha_ubisoft"),
            "senha_email": request.form.get("senha_email"),
            "provedor": request.form.get("provedor"),
            "observacoes": request.form.get("observacoes")
        }

        if not data["email"] or not data["senha_ubisoft"] or not data["senha_email"]:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("adicionar.html", data=data)

        db.create(data)
        flash("Conta adicionada com sucesso!", "success")
        return redirect(url_for("conta_bp.index"))

    return render_template("adicionar.html")

@conta_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conta = db.get_by_id(id)

    if not conta:
        flash("Conta não encontrada.", "error")
        return redirect(url_for("conta_bp.index"))

    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "senha_ubisoft": request.form.get("senha_ubisoft"),
            "senha_email": request.form.get("senha_email"),
            "provedor": request.form.get("provedor"),
            "observacoes": request.form.get("observacoes")
        }

        if not data["email"] or not data["senha_ubisoft"] or not data["senha_email"]:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("editar.html", conta=data)

        db.update(id, data)
        flash("Conta atualizada com sucesso!", "success")
        return redirect(url_for("conta_bp.index"))

    return render_template("editar.html", conta=conta)

@conta_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    db.delete(id)
    flash("Conta excluída com sucesso!", "success")
    return redirect(url_for("conta_bp.index"))

@conta_bp.route("/exportar")
def exportar():
    contas = db.get_all()
    txt = ""

    for c in contas:
        txt += (
            f"ID: {c['id']}\n"
            f"Email: {c['email']}\n"
            f"Senha Ubisoft: {c['senha_ubisoft']}\n"
            f"Senha Email: {c['senha_email']}\n"
            f"Provedor: {c.get('provedor') or 'N/A'}\n"
            f"Observações:\n{c.get('observacoes') or 'Nenhuma'}\n"
            + "-" * 40 + "\n\n"
        )

    return Response(
        txt,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=contas_ubisoft.txt"}
    )
