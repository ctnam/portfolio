from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()   #  initialized in the blueprint package, and not in the application package
from . import api


# improved authentication verification with token support
from ..models import User
@auth.verify_password    ## see LINE 2
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


from .errors import unauthorized
@auth.error_handler    ## see LINE 2
def auth_error():
    return unauthorized('Invalid credentials')


from .errors import forbidden
from flask_login import login_required
@api.before_request
@login_required          #@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


# authentication token generation
@api.before_request
@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
