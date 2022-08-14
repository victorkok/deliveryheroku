from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import ChangeEmailForm, LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm
from ..models import Consumer, Destiny
from .. import db
from ..email import send_email

# codigo abaixo eh um quebra-galho. O certo é usar javascript (que faz tempo que não uso...)
def validador_cadastro(username, password, email, number,
                       address, zipcode, neighborhood,
                       city, state):
        print('>>> username: ', username)
        if not username:
            flash('Campo nome não pode ficar vazio!')
            return True
        elif not password:
            flash('Campo senha não pode ficar vazio!')
            return True
        elif not email:
            flash('Campo email não pode ficar vazio!')
            return True
        elif not number:
            flash('Campo numero não pode ficar vazio!')
            return True
        elif not address:
            flash('Campo endereço não pode ficar vazio!')
            return True
        elif not zipcode:
            flash('Campo CEP não pode ficar vazio!')
            return True
        elif not neighborhood:
            flash('Campo bairro não pode ficar vazio!')
            return True
        elif not city:
            flash('Campo cidade não pode ficar vazio!')
            return True
        elif not state:
            flash('Campo estado não pode ficar vazio!')
            return True
        else:
            return False

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         consumer = Consumer.query.filter_by(email=request.form['email']).first()
#         if consumer is not None and consumer.verify_password(request.form['password']):
#             # login_user(user, request.form['remember'])
#             login_user(consumer)
#             next = request.args.get('next')
#             if next is None or not next.startswith('/'):
#                 print('>>>banana<<<')
#                 print("is_authenticated: ", current_user.is_authenticated)
#                 print("is_confirmed: ", current_user.confirmed)
#                 next = url_for('main.index')
#             return redirect(next)
#         flash('Invalid username or password. ')
#     return render_template('auth/login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        consumer = Consumer.query.filter_by(email=form.email.data.lower()).first()
        if consumer is not None and consumer.verify_password(request.form['password']):
            login_user(consumer, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                print('>>>banana<<<')
                print("is_authenticated: ", current_user.is_authenticated)
                print("is_confirmed: ", current_user.confirmed)
                next = url_for('tables.index')
            return redirect(next)
        flash('Invalid username or password. ')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você fez logout.')
    return redirect(url_for('tables.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # esse validate_flag é um quebra-galho. Tentar fazer com javascript
        validate_flag = validador_cadastro(request.form['username'],
                                           request.form['password'],
                                           request.form['email'],
                                           request.form['number'],
                                           request.form['address'],
                                           request.form['zipcode'],
                                           request.form['neighborhood'],
                                           request.form['city'],
                                           request.form['state'])
        if validate_flag:
            print(">>> redirect to register")
            return redirect(url_for('auth.register'))
        # código abaixo é o original. Cuidado para não apaga-lo!
        destiny = Destiny(address=request.form['address'],
                          number=request.form['number'],
                          zipcode=request.form['zipcode'],
                          neighborhood=request.form['neighborhood'],
                          complement=request.form['complement'],
                          city=request.form['city'],
                          state=request.form['state'])
        consumer = Consumer(email=request.form['email'],
                            username=request.form['username'],
                            password=request.form['password'],
                            destiny=destiny)
        db.session.add(consumer)
        db.session.commit()
        token = consumer.generate_confirmation_token()
        send_email(consumer.email, 'Confirm Your Account',
                   'auth/email/confirm', consumer=consumer, token=token)
        flash('Um email de confirmação foi enviado para você!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         destiny = Destiny(address=form.address.data,
#                           number=form.number.data,
#                           zipcode=form.zipcode.data)
#         consumer = Consumer(email=form.email.data.lower(),
#                             username=form.username.data,
#                             password=form.password.data,
#                             destiny=destiny)
#         db.session.add(consumer)
#         db.session.commit()
#         token = consumer.generate_confirmation_token()
#         send_email(consumer.email, 'Confirm Your Account',
#                    'auth/email/confirm', user=consumer, token=token)
#         flash('A confirmation email has been sent to you by email.')
#         return redirect(url_for('main.index'))
#     return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required  # isto está me fud#%ˆ
def confirm(token):
    print('>>>entrou na sala!')
    if current_user.confirmed:
        print('>>>Entrou <<<')
        return redirect(url_for('tables.index'))
    if current_user.confirm(token):
        db.session.commit()
        print('>>>Também entrou')
        flash('Você confirmou sua conta. Obrigado!')
    else:
        flash('O link de confirmação expirou.')
    return redirect(url_for('tables.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
                print('>>>Sakura<<<')
                return redirect('auth.unconfirmed')


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('tables.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirmando a sua conta',
               'auth/email/confirm', user=current_user,
               token=token)
    flash('Um novo e-mail de confirmação foi enviada para a sua caixa de e-mails.')
    return redirect(url_for('tables.index'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form =ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Sua senha foi trocada.')
            return redirect(url_for('tables.index'))
        else:
            flash('Senha inválida')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('tables.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        consumer = Consumer.query.filter_by(email=form.email.data.lower()).first()
        if consumer:
            token = consumer.generate_reset_token()
            send_email(consumer.email, 'Renovando a sua senha.',
                       'auth/email/reset_password', consumer=consumer, token=token)
            flash('Um email com instruções para renovar a sua senha foi'
                  'enviado para você')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('tables.index'))
    form =  PasswordResetForm()
    if form.validate_on_submit():
        if Consumer.reset_password(token, form.password.data):
            db.session.commit()
            flash('Sua senha foi renovada!')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('tables.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirme o seu endereço de email',
                       'auth/email/change_email', consumer=current_user,
                       token=token)
            flash('Um email com as instruções para confirmar seu novo email'
                  'Foi enviado para você.')
            return redirect(url_for('tables.index'))
        else:
            flash('Email ou senha inválida.')
    return render_template('auth/change_email.html', form=form)

@auth.route('/change_email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Seu endereço de email foi atualizado!')
    else:
        flash('Requerimento invalido.')
    return redirect(url_for('tables.index'))