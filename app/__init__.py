from flask import Flask
from .models.conta_model import ContaModel
from .models.usuario_model import UsuarioModel 

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='quinaia',
    )

    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 

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