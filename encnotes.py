# -*- coding: utf-8 -*-
"""
   Encnotes - зашифрованные записки.

   Создание зашифрованных записок используя метод шифрования AES-128.
"""
import os
import random

from cryptography.fernet import Fernet
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    """Класс конфигурации для Flask

    Все настройки указывают в этом классе.

    SECRET_KEY - ключ для генерации подписей или токенов
    SQLALCHEMY_TRACK_MODIFICATIONS - отключение уведомлений о каждом изменении
    в базе данных
    SQLALCHEMY_DATABASE_URI - местоположение базы данных
    SITE_URL - полный адрес вашего сайта
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or '1FSHFI89FSDHKFH'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'app.db'))
    SITE_URL = 'http://localhost:5000'


# Создание объекта приложения как экземпляр класса Flask
# и инициализация модулей с Flask-ом
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)


class Note(db.Model):
    """Модель записки для базы данных

    number - случайная цифра, по которой мы будем находить нашу записку
    ciptext - зашифрованная записка
    """
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    ciptext = db.Column(db.Text)

    def __repr__(self):
        return f'<Note number: {self.number}'


class TextForm(FlaskForm):
    """Форма для ввода сообщения

    Максимальное количестве введенных символов - 1000
    """
    text = TextAreaField('Введите текст (максимум 1000 символов)',
                         validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField('Создать')

# Регистрация функции фукции как функцию контекста оболочки,
# что дает возможность работать с объектами базы данных не импортирую их
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Note': Note}


@app.route('/', methods=['GET', 'POST'])
def index():
    """Фукнция просмотра для главной страницы

    Получает сообщение от пользователя, шифрует его модулем cryptography
    и дает пользователю ссылку с ключом.
    """
    form = TextForm()
    if form.validate_on_submit():
        key = Fernet.generate_key()
        str_key = key.decode('ascii')
        f = Fernet(key)
        bin_string = form.text.data.encode('utf-8')
        cipher_text = f.encrypt(bin_string)
        str_cipher_text = cipher_text.decode('ascii')
        rnumber = random.randint(1000000, 9999999)
        while True:
            n = Note.query.filter_by(number=rnumber).first()
            if not n:
                break
            rnumber = random.randint(1000000, 9999999)
        cipher_note = Note(number=rnumber, ciptext=str_cipher_text)
        link = f'{app.config["SITE_URL"]}/{rnumber}/{str_key}'
        db.session.add(cipher_note)
        db.session.commit()
        return render_template('complete.html', link=link)
    return render_template('index.html', form=form)


@app.route('/<int:rnumber>/<str_key>')
def decrypt(rnumber, str_key):
    """Фукнция просмотра для расшифровки сообщения

    Расшифровывает сообщение использую ключ из ссылки. После сообщение
    удаляется из базы данных.
    """
    cipher_note = Note.query.filter_by(number=rnumber).first_or_404()
    cipher_text = cipher_note.ciptext.encode('ascii')
    key = str_key.encode('ascii')
    try:
        f = Fernet(key)
        text = f.decrypt(cipher_text)
    except ValueError:
        return render_template('error.html')
    text = text.decode('utf-8')
    db.session.delete(cipher_note)
    db.session.commit()
    return render_template('decrypt.html', text=text)