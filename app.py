from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from models import db, User
import requests
#pip install -r requirements.txt
app = Flask(__name__)
app.secret_key = 'chiavesessione'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

#collego i blueprint all'app per poter accedere alle loro route
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)





if __name__ == "__main__":
    app.run(debug=True)