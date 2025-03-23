from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

#Commit di amine relativo alla visualizzazione playlist di un utente
class Playlist(db.Model):
    #ID della playlist
    id = db.Column(db.Integer, primary_key=True)
    #ID dell'user come chiave esterna dalla tabella User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #ID della playlist su spotify
    playlist_id = db.Column(db.String(80), nullable=False)
    user = db.relationship('User', backref="playlist", lazy=True)