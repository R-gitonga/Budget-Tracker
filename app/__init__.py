from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError

# from app.models import User



db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login' #redirects users who arent logged in
login_manager.login_message_category = 'info'



def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)  # every POST must carry a valid CSRF token

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash('Your form expired or was invalid. Please try again.', 'danger')
        return redirect(url_for('main.home'))

    # with app.app_context():
    #     db.create_all()

    # login_manager.init_app(app)

    return app