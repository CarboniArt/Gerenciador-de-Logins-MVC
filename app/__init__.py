from flask import Flask
from .models.conta_model import ContaModel
from .models.usuario_model import UsuarioModel 
from flask_mail import Mail  


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='quinaia',
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 

    app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
    app.config['MAIL_PORT'] = 587 
    app.config['MAIL_USE_TLS'] = True 
    app.config['MAIL_USERNAME'] = 'mimicofirebasez@gmail.com' 
    app.config['MAIL_PASSWORD'] = 'edus thoi cylg azcz' 
    app.config['MAIL_DEFAULT_SENDER'] = 'gerenciadordecontas@gmail.com' 

    from .controllers.usuario_controller import mail as user_mail
    user_mail.init_app(app) 

    with app.app_context():
        conta_model = ContaModel()
        conta_model.init_db()
        conta_model.migrate_to_encrypted()

        usuario_model = UsuarioModel()
        usuario_model.init_db() 
        
    from .controllers import conta_controller
    from .controllers import usuario_controller 

    app.register_blueprint(conta_controller.conta_bp)
    app.register_blueprint(usuario_controller.usuario_bp)

    return app