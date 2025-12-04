from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from itsdangerous import Serializer
from app.models.usuario_model import UsuarioModel 
from werkzeug.security import generate_password_hash

usuario_bp = Blueprint("usuario_bp", __name__, template_folder="../templates")

db_user = UsuarioModel()

mail = Mail()

@usuario_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email") # 
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password or not confirm_password:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("registrar.html", username=username, email=email) 
        
        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template("registrar.html", username=username, email=email) 

        if db_user.create_user(username, email, password): 
            flash("Conta criada com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("usuario_bp.login"))
        else:
            flash("Nome de usuário ou e-mail já existe. Escolha outro.", "error") 
            return render_template("registrar.html", username=username, email=email) 
    return render_template("registrar.html")

@usuario_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db_user.get_user_by_username_or_email(username)
        
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

def send_reset_email(user):
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')
    token = s.dumps({'user_id': user['id']})

    reset_url = url_for('usuario_bp.reset_password', token=token, _external=True)

    msg = Message('Redefinição de Senha',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user['email']])
    msg.body = f"""Para redefinir sua senha, visite o seguinte link:
{reset_url}

Se você não solicitou esta redefinição, simplesmente ignore este e-mail.
"""
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar e-mail: {e}")
        return False


@usuario_bp.route("/esqueci-senha", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = db_user.get_user_by_email(email)
        
        if user:
            if send_reset_email(user):
                flash("Um link de redefinição de senha foi enviado para seu e-mail.", "info")
                return redirect(url_for("usuario_bp.login"))
            else:
                flash("Houve um erro ao enviar o e-mail de redefinição. Tente novamente.", "error")
        else:
            flash("Um link de redefinição de senha foi enviado para seu e-mail (se a conta existir).", "info")
            return redirect(url_for("usuario_bp.login"))

    return render_template("forgot_password.html")

@usuario_bp.route("/resetar-senha/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')
    try:
        data = s.loads(token, max_age=1800) 
        user_id = data.get('user_id')
    except:
        flash("O link de redefinição é inválido ou expirou.", "error")
        return redirect(url_for("usuario_bp.forgot_password"))

    conn = db_user._get_db_connection()
    user = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("usuario_bp.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template("reset_password.html", token=token)

        hashed_password = generate_password_hash(new_password)
        conn = db_user._get_db_connection()
        conn.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        conn.close()

        flash("Sua senha foi redefinida com sucesso! Faça login.", "success")
        return redirect(url_for("usuario_bp.login"))

    return render_template("reset_password.html", token=token)