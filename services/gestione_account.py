from models import User, db
from flask_login import login_user

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return False
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return True

def authenticate_user(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        return True
    return False