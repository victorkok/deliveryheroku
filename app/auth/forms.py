from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Consumer


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Mantenha-me logado')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Nome do usuário', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'O nome do usuário deve apenas conter underline, pontos'
               ' letras e números.')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Senhas devem coincidir')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    address = StringField('Endereço', validators=[DataRequired()])
    number = StringField('Número', validators=[DataRequired()])
    zipcode = StringField('Cep', validators=[DataRequired()])
    submit = SubmitField('Register')
    def validate_email(self, field):
        if Consumer.query.filter_by(email=field.data).first():
            raise ValidationError('Esse email já foi cadastrado.')

    def validate_username(self, field):
        if Consumer.query.filter_by(username=field.data).first():
            raise ValidationError('Um usuário já está usando este nome.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Velha senha', validators=[DataRequired()])
    password = PasswordField('Nova senha', validators=[
        DataRequired(), EqualTo('password2', message='Senhas devem coincidir.')])
    password2 = PasswordField('Confirme a nova senha',
                              validators=[DataRequired()])
    submit = SubmitField('Atualizar senha')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Renovar Senha')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[
        DataRequired(), EqualTo('password2', message='Senhas devem coincidir')])
    password2 = PasswordField('Confirmar senha', validators=[DataRequired()])
    submit = SubmitField('Renovar Senha')


class ChangeEmailForm(FlaskForm):
    email = StringField('Novo email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if Consumer.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Esse email já está registrado.')