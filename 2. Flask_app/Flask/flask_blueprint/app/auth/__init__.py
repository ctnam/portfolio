from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views

from flask_login import login_required
