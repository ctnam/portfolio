
# MANAGE.PY, remember?

import os

from app import create_app, db   # folder 'app'/__init__.py (lines 15,13)
from app.models import User, Role   # still missing
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default') # Default = DevelopmentConfig = (DEBUG = True, data-dev.sqlite)
## folder 'app'/__init__.py line 13
## config.py line 38
migrate = Migrate(app, db)





from app import fake
def create_db100mems():
    fake.users(count=100)

from app.models import Comment
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    print(comment)
    db.session.delete(comment)
    db.session.commit()
    print('Done')

from app.models import Namstask,Tasktype
def add_tasktypes():
    for u in ["Work", "Study", "Healthcare", "Relationships", "Leisure"]:
        typ = Tasktype(name=u)
        db.session.add(typ)
        db.session.commit()
    print('All done.')
def del_alltasks():
    for t in Namstask.query.all():
        db.session.delete(t)
        db.session.commit()
    print('All done.')

from app.models import NamsInsulin, Insulin
def del_allinsulins():
    for i1 in NamsInsulin.query.all():
        db.session.delete(i1)
        db.session.commit()
    for i2 in Insulin.query.all():
        db.session.delete(i2)
        db.session.commit()
    print('ALL done.')

from app.models import DeadLine
def del_alldeadlines():
    for d in DeadLine.query.all():
        db.session.delete(d)
        db.session.commit()
    print('ALL done.')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, create_db100mems=create_db100mems, delete_comment=delete_comment,
                add_tasktypes=add_tasktypes,
                del_alltasks=del_alltasks, del_allinsulins=del_allinsulins, del_alldeadlines=del_alldeadlines)
### (venv) $ flask shell   db User Role test123()

@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
@app.cli.command()
def manualtest():
    print(os.environ.get('MAIL_USERNAME'))
### (venv) $ flask test
### (venv) $ flask manualtest


import os
import sys
import click

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
# ...
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        print(basedir)
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
# set FLASK_COVERAGE=1
## flask test --coverage
## flask test --no-coverage


## Running the application under the request profiler
# To watch a running application and records the functions that are called and how long each takes to run
@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run(debug=False)




# DEPLOYMENT
from flask_migrate import upgrade
from app.models import Role, User

#@manager.command
@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    User.add_self_follows()

# Importing the environment from the .env file
# the .env file can define the FLASK_CONFIG variable that selects the configuration to use, the DATABASE_URL connection, the email server credentials, etc
#import os
#from dotenv import load_dotenv

#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#if os.path.exists(dotenv_path):
#    load_dotenv(dotenv_path)
