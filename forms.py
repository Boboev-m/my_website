from ast import Sub
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.validators import EqualTo
from wtforms.validators import Regexp

class SignupForm(FlaskForm):
    username = StringField('Номи корбар', validators=[
        DataRequired(), 
        Length(min=4, max=25),
        Regexp('^\w+$', message="Номи корбар бояд танҳо ҳарфҳо, рақамҳо ё зерхатро дар бар гирад.")])
    password = PasswordField('Рамз', validators=[
        DataRequired(message="Ин бахш ҳатмист."), Length(min=6, max=35, message="Рамз бояд на камтар аз 6 аломат бошад.")])
    confirm_password = PasswordField('Тасдиқи рамз', validators=[
        DataRequired(), EqualTo('password', message='Рамзҳо бояд ба ҳамдигар мувофиқ ояд.')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Бақайдгирӣ 🚀')

class LoginForm(FlaskForm):
    username = StringField('Номи корбар', validators=[DataRequired()])
    password = PasswordField('Рамз', validators=[DataRequired()])
    submit = SubmitField('Даромадан 🔓')