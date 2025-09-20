from flask import Flask
from config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models sebelum migration jalan
    from app import models

    # Register blueprint DI DALAM create_app agar terhindar dari circular import
    # from app.routes import routes as main
    from app.routes import main
    app.register_blueprint(main)

    return app
