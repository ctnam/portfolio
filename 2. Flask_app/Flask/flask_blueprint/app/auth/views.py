from flask import render_template, redirect, request, url_for, flash, session
from . import auth   # 'auth' blueprint

from flask_login import login_user #
from ..models import User
from .forms import LoginForm,RegistrationForm,ResendActivationForm

from .. import db
from ..email import send_confirmationmail
from ..email import resend_confirmationmail

from flask_login import current_user ###

from sqlalchemy.exc import IntegrityError


# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == False:
        form = LoginForm()
        if form.validate_on_submit():   # always
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data) # login_user imported from flask_login
                user.recordlogintimepoint() # models.py line 158-161
                next = request.args.get('next') ### the original URL in the next query string argument
                if next is None or not next.startswith('/'):
                    next = url_for('main.index') ### If the next query string argument is not available, a redirect to the home page is issued
                return redirect(next)
            flash('Invalid username or password.')
        return render_template('auth/login.html', form=form)   # app/templates/auth/login.html
    else:
        return redirect(url_for('main.index'))


# Logout
from flask_login import logout_user, login_required

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


# Sign up
@auth.route('/register', methods=['GET', 'POST'])
async def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        user.recordsignuptimepoint()
        token = user.generate_confirmation_token()
        await send_confirmationmail(user.email, _template_body={"user": user, "token": token})
        flash('A confirmation email has been sent to you.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


# Confirm new user
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:   # if current_user.confirmed == True
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


# Filtering unconfirmed accounts with the before_app_request handler
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))   ### line 94: return render_template('auth/resendconfirmation.html', form=form)
                                # below is url_for('auth.unconfirmed')
@auth.route('/unconfirmed', methods=['GET', 'POST'])
@login_required
async def unconfirmed():
    form = ResendActivationForm()
    try:
        form.email.data = current_user.email
    except AttributeError:
        pass
    if form.validate_on_submit():
        token = current_user.generate_confirmation_token()
        await resend_confirmationmail(current_user.email, _template_body={"current_user": current_user, "token": token})
        flash('A new confirmation email has been sent to you.')
        return redirect(url_for('main.index'))
    return render_template('auth/resendconfirmation.html', form=form)


# Pinging the logged-in user
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
