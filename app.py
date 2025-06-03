import re
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from forms import SignupForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFProtect
from flask_wtf import RecaptchaField
import secrets
import json, os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LesDzkrAAAAAMlNVlhvYngUsM_IZIK6KphHx0KY'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LesDzkrAAAAAH0IljhLXvlSSPh-tqMiyYb5jSa4'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
recaptcha = RecaptchaField()

# User model
class User(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Favorite user_id={self.user_id} word_id={self.word_id}>'
    
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    word_id = db.Column(db.Integer)  # ✅ Changed from String to Integer


books = [
    {
        'title': 'HSK Student Book 1',
        'image': '/static/images/hsk_1_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1EQcRxCFDEdpUdErTQaifZ9TwqG5BJxW-/view?usp=drive_link',
    },
    {
        'title': 'HSK Workbook Book 1',
        'image': '/static/images/hsk1w.png',
        'pdf_url': 'https://drive.google.com/file/d/1e6DGpLpONl-nNsALhFIuKXOhBKzzgrSI/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 2',
        'image': '/static/images/hsk_2_s.png',
        'pdf_url': 'https://drive.google.com/file/d/13tKasmsbdV-GWsc2IqMU85jRI3TswfnB/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 2',
        'image': '/static/images/hsk_2_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1B8pF6Tc_KNAHUAGbJNfVnnhQH2ueBE2v/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 3',
        'image': '/static/images/hsk_3_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1zu0tDRu6I860lo3Qzpy_8Fa3moS_5_LB/view?usp=sharing',
    },
        {
        'title': 'HSK Workbook Book 3',
        'image': '/static/images/hsk_3_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1J8en9ny503ezV8yLyLo5HQ3U6DU4clPv/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 4上',
        'image': '/static/images/hsk_4上_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1lriFs9azVTgBv-CkQL3vlpHm-Ah3MC90/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 4上',
        'image': '/static/images/hsk_4上_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1UgpLCkCmEbpNf-yWcDrH5ePwRNO1M_Qk/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 4下',
        'image': '/static/images/hsk_4下_s.png',
        'pdf_url': 'https://drive.google.com/file/d/16iBnnwobQkteVWHpOhpnHElFK6xkiES0/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 4下',
        'image': '/static/images/hsk_4下_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1XA-nPpIKqKtyD1d2jybxVdQHnayJQ21M/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 5上',
        'image': '/static/images/hsk_5上_s.png',
        'pdf_url': 'https://drive.google.com/file/d/10X7Muo-Y4ZahjWbosbJ1EcMaPB65JvCX/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 5上',
        'image': '/static/images/hsk_5上_w.png',
        'pdf_url': 'https://drive.google.com/file/d/17feNW4FoaTF2NC3fUTAAXHJokAZ3J8P1/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 5下',
        'image': '/static/images/hsk_5下_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1xlDvllYhCVo_QMyITtgb-HYw0o46QJRp/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 5下',
        'image': '/static/images/hsk_5下_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1aWSAP0lkcnN7JRbO6BZsiM_UewMm_xDj/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 6上',
        'image': '/static/images/hsk_6上_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1cKwgQSWv3on8NKo0UkNgmTDYYQWtlnrn/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 6上',
        'image': '/static/images/hsk_6上_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1_7Sr8z4k9wpSJMMXs12M8nDdZ8yFd5Ry/view?usp=sharing',
    },
    {
        'title': 'HSK Student Book 6下',
        'image': '/static/images/hsk_6下_s.png',
        'pdf_url': 'https://drive.google.com/file/d/1uDvr1WHK8NCtThSKsjr4N0dPueW7yLPT/view?usp=sharing',
    },
    {
        'title': 'HSK Workbook Book 6下',
        'image': '/static/images/hsk_6下_w.png',
        'pdf_url': 'https://drive.google.com/file/d/1zSduWK_arElJ7pCuoUnEPabh9qJJ9jFH/view?usp=sharing',
    }
]
USER_FILE = 'users.json'

# Load users from file
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save users to file
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def load_vocab_from_csv():
    vocab = []
    with open('vocab.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["id"] = int(row["id"])
            vocab.append(row)
    return vocab

@app.route('/')
def home():
    username = session.get('user') 
    return render_template('index.html', username=username)

@app.route('/books')
def book_page():
    if not session.get('user'):
        return redirect(url_for('signup'))

    return render_template('books.html', books=books)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        # Check user already exists
        if User.query.filter_by(username=username).first():
            flash('Корбар аллакай вуҷуд дорад. Лутфан номи корбарро тағир диҳед.')
            return render_template('signup.html', form=form)
        
        hashed = generate_password_hash(password)

        role = 'admin' if User.query.count() == 0 else 'user'

        new_user = User(username=username, password_hash=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
      
        flash(f'Бақайдгирии муваффақ! Лутфан дароед.')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/signup/confirm', methods=['GET', 'POST'])
def signup_confirm():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        if User.query.filter_by(username=username).first():
            flash('Корбар аллакай вуҷуд дорад. Лутфан номи корбарро тағир диҳед.')
            return render_template('signup.html', form=form)
        
        hashed = generate_password_hash(password)

        new_user = User(username=username, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()

        flash('Бақайдгирии муваффақ! Лутфан дароед.')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user = User.query.filter_by(username=username).first()

        # Check if user exists
        if not user:
            flash('Номи корбари беэътибор.')
            return render_template('login.html', form=form)
        
        # Check password
        if not check_password_hash(user.password_hash, password):
            flash('Рамзи нодуруст.')
            return render_template('login.html', form=form )
        
        # Successful login
        session['user'] = user.username
        session['role'] = user.role
        flash(f'🎉Хуш омадед, {user.username}!🎉')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/vocabulary')
def vocabulary():
    if not session.get('user'):
        return redirect(url_for('signup'))

    show_favorites = request.args.get('favorites') == '1'

    vocab = []
    with open('vocab.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['id'] = int(row['id'])
            vocab.append(row)

    # Get current user
    user = User.query.filter_by(username=session['user']).first()
    favorite_word_ids = {int(fav.word_id) for fav in Favorite.query.filter_by(user_id=user.id)} if user else set()
    flashcard_words = {f.word_id for f in Flashcard.query.filter_by(user_id=user.id)} if user else set()

    # Filter vocab if showing favorites
    if show_favorites:
        vocab = [word for word in vocab if word['id'] in favorite_word_ids]

    return render_template('vocabulary.html', vocab=vocab, show_favorites=show_favorites, favorite_word_ids=favorite_word_ids, flashcard_words=flashcard_words)


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'user' not in session:
        return jsonify({'error': 'Беиҷозат'}), 401

    data = request.get_json()
    word_id = int(data.get('word_id'))

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    existing_fav = Favorite.query.filter_by(user_id=user.id, word_id=word_id).first()

    if existing_fav:
        db.session.delete(existing_fav)
        db.session.commit()
        return jsonify({'favorited': False})
    else:
        new_fav = Favorite(user_id=user.id, word_id=word_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'favorited': True})

@app.route('/toggle_flashcard', methods=['POST'])
def toggle_flashcard():
    if 'user' not in session:
        return jsonify({'error': 'Беиҷозат'}), 401
    
    data = request.get_json()
    word_id = int(data['word_id'])

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        return jsonify({'error': 'Корбар ёфт нашуд'}), 404
    
    # Check if the word is already in the flashcard list
    existing = Flashcard.query.filter_by(user_id=user.id, word_id=word_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'added': False})
    else:
        new_flashcard = Flashcard(user_id=user.id, word_id=word_id)
        db.session.add(new_flashcard)
        db.session.commit()
        return jsonify({'added': True})


@app.route('/flashcards')
def flashcard_study():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    vocab = load_vocab_from_csv()
    flashcard_ids = {f.word_id for f in Flashcard.query.filter_by(user_id=user.id)} if user else set()

    # DEBUG: print what's being sent
    print("Flashcard IDs:", flashcard_ids)

    flashcards = [w for w in vocab if w["id"] in flashcard_ids]
    return render_template("flashcards.html", flashcards=flashcards)


@app.route('/setuser/<username>')
def setuser(username):
    session['user'] = username
    session['role'] = 'user'
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('БАРОМАД БО МУВАФФАҚИЯТ АНҶОМ ЁФТ')
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return "Дастрасӣ манъ аст!", 403  # Only admin can view this page
    users = User.query.all()

    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
