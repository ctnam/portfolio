from flask import Blueprint

main = Blueprint('main', __name__)
### the name of the blueprint = the first argument to the Blueprint constructor = 'main' / and the module or package where the blueprint is located '__name__'
# dormant state until the blueprint is registered with an application, then they become part of it
# to register at folder 'app'/__init__.py
from . import views, errors


from ..models import Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
    ### ^^^ Context processors make variables available to all templates during rendering
    ## dict(Permission=Permission)

@main.app_context_processor
def inject_abc():
    abc = "ABC is shown here!"
    return dict(abc=abc)

@main.app_context_processor
def inject_commentid():
    try:
        with open('commentid', 'r') as f:
            commentid = f.read()
    except FileNotFoundError:
        commentid = ''
    return dict(commentid=commentid)
