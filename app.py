from flask import Flask
from blueprints.auth import auth_bp
from blueprints.home import home_bp
#pip install -r requirements.txt
app = Flask(__name__)
app.secret_key = 'chiavesessione'

#collego i blueprint all'app per poter accedere alle loro route
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)

if __name__ == "__main__":
    app.run(debug=True)