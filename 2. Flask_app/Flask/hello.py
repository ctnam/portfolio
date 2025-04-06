

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import os
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
import sqlite3
def syncdata():
    for i in range(len(Role.query.all())):
        try:
            cur.execute('''SELECT name FROM roles WHERE id=?''', (i+1,))
            rolename_value = cur.fetchone()[0]   ### not 'cur.fetchone()'
            if Role.query.all()[i].rolename != rolename_value:
                Role.query.all()[i].rolename = rolename_value
                db.session.commit()
                print('Successfully synchronised ' + rolename_value)
        except TypeError:
            break
    print('Synchronisation done.')




app = Flask(__name__)
app.config['SECRET_KEY'] = 'pN,9)]l^IO9K70-KZ#^5dAjw8462fmY0hz75;+@VVzsTayuX3d0"!?Z%mgI?lghCA7{$}Uw'
bootstrap = Bootstrap(app)
moment = Moment(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
con = sqlite3.connect('data.sqlite')
cur = con.cursor()

from flask_mail import Mail
mail = Mail(app)
from flask_mail import Message

import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
from threading import Thread






def test123():
    print('One, two, three... Already worked.')
    print(User.query.all()[0].username)
    print(app.config['MAIL_SERVER'])
    print(app.config['MAIL_USERNAME'])
    print(app.config['FLASK_BOSS'])
    for i in range(3):
        cur.execute('''SELECT username FROM users WHERE id=?''', (i+1,))
        username_value = cur.fetchone()[0]
        print(username_value)
@app.shell_context_processor
def make_shell_context():
    #print('Flask Shell')
    return dict(db=db, User=User, Role=Role, test123=test123, syncdata=syncdata, sendmail=sendmail)   ### type 'test123()' in the shell

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow(), dirdb=dir(app))

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)

@app.route('/renderuser/<name>')
def renderuser(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    #email = StringField('What is your email address?', validators=[Email()])
    submit = SubmitField('Submit')

@app.route('/form',methods=['GET', 'POST'])
def formfunc():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('formfunc'))
    return render_template('form.html', form = form, name = session.get('name'))




###### SQL ######
###### SQLAlchemy column boolean options: primary_key, unique, index, nullable, default
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), unique=True) ### name -> rolename

    def __repr__(self):   # for debugging and testing
        return '<Role %r>' % self.rolename ### self.name -> self.rolename
    # relationships in the database models
    users = db.relationship('User', backref='role', lazy='dynamic')
    # users = db.relationship('User', backref='role') # 'users' attribute returns the list of users associated with the role
###### SQLAlchemy relationship options: backref, primaryjoin, lazy, uselist, order_by, secondary, secondaryjoin


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username
    # role_id column added to the User model, defined as a foreign key, and that establishes the relationship
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # table 'roles' / column 'id'


@app.route('/index', methods=['GET', 'POST'])
def index2():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index2'))
    return render_template('index2.html',
        form=form, name=session.get('name'),
        known=session.get('known', False))




###### EMAIL ######
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') ### (venv) $ set MAIL_USERNAME=webdev.tnam@gmail.com
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') ### (venv) $ set MAIL_PASSWORD=Gmailpassword
def sendmail():
    msg = Message('test email', sender='webdev.tnam@gmail.com', recipients=['namcaocomebackp66@gmail.com'])
    msg.body = 'This is the plain text body'
    msg.html = 'This is the <b>HTML</b> body'
    with app.app_context():
        mail.send(msg)

app.config['FLASK_MAIL_SUBJECT_PREFIX'] = '[Flask FW]'
app.config['FLASK_MAIL_SENDER'] = 'WebdevTnam Admin <webdev.tnam@gmail.com>'
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
# ......
app.config['FLASK_BOSS'] = 'namcaocomebackp66@gmail.com' # os.environ.get('FLASK_BOSS')
@app.route('/indexnoticenewuser', methods=['GET', 'POST'])
def index_noticenewuser():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_BOSS']:
                send_email(app.config['FLASK_BOSS'], 'Notification about New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index_noticenewuser'))
    return render_template('index2.html', form=form, name=session.get('name'),
                           known=session.get('known', False))
