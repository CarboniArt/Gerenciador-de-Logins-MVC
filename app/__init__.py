from flask import Flask
from .models.conta_model import ContaModel

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='quinaia',
    )

    with app.app_context():
        model = ContaModel()
        model.init_db()
        model.migrate_to_encrypted()

    from .controllers import conta_controller
    app.register_blueprint(conta_controller.conta_bp)

    return app