from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# If Inside a blueprint, the 'errorhandler' decorator is used
### To install Application-level error handlers, the 'app_errorhandler' decorator is used
