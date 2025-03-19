from flask import Blueprint, redirect, request, url_for, session, render_template

account_bp = Blueprint('account', __name__)

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html', error=None)

@account_bp.route('/accesso', methods=['GET', 'POST'])
def accesso():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Credenziali non valide.")
    return render_template('login.html', error=None)