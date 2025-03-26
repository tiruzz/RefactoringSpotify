from flask import Blueprint, redirect, request, url_for, session, render_template
from models import User, Playlist, db
from flask_login import login_user, logout_user

account_bp = Blueprint('account', __name__)

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('registrazione.html', error="Questo username è già in uso.")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('registrazione.html', error=None)

@account_bp.route('/accesso', methods=['GET', 'POST'])
def accesso():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id  # Memorizza l'ID dell'utente nella sessione
            return redirect(url_for('home.home_page'))
        return render_template('login.html', error="Credenziali non valide.")
    return render_template('login.html', error=None)

@account_bp.route('/logout')
def logout():
    print("Session prima del logout:", dict(session))  # Mostra i dati attuali della sessione
    session.clear()  # Svuota la sessione
    print("Session dopo il logout:", dict(session))  # Dovrebbe essere vuota
    return redirect(url_for('home.home_page'))


# Route per la pagina 'myaccount'
@account_bp.route('/myaccount')
def my_account():
    # Verifica se l'utente è loggato (tramite session)
    if 'user_id' not in session:
        return redirect(url_for('account.accesso'))  # Se non è loggato, reindirizza alla pagina di login
    
    # Ottieni l'utente dalla sessione
    user_id = session['user_id']
    user = User.query.get(user_id)  # Ottieni i dati dell'utente dal DB
    
    # Ottieni le playlist salvate dall'utente
    playlists = Playlist.query.filter_by(user_id=user.id).all()
    
    return render_template('myaccount.html', user=user, playlists=playlists)
    