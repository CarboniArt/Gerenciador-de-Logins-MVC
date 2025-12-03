from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.usuario_model import UsuarioModel 

usuario_bp = Blueprint("usuario_bp", __name__, template_folder="../templates")

db_user = UsuarioModel()

@usuario_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("registrar.html")
        
        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template("registrar.html", username=username)

        if db_user.create_user(username, password):
            flash("Conta criada com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("usuario_bp.login"))
        else:
            flash("Nome de usuário já existe. Escolha outro.", "error")
            return render_template("registrar.html", username=username)
    
    return render_template("registrar.html")

@usuario_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db_user.get_user_by_username(username)
        
        if user and db_user.check_password(user, password):
            session['username'] = user['username']
            flash(f"Bem-vindo, {user['username']}!", "success")
            return redirect(url_for("conta_bp.index"))
        else:
            flash("Credenciais inválidas. Tente novamente.", "error")
            return render_template("login.html", username=username)
    
    return render_template("login.html")

@usuario_bp.route("/logout")
def logout():
    session.pop('username', None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("conta_bp.index"))