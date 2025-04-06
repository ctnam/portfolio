from . import db

from flask_login import UserMixin

from . import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from werkzeug import security as werkzeugsecurity

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   # create token
from flask import current_app

from flask_login import UserMixin, AnonymousUserMixin

from datetime import datetime

import hashlib   # Gravatar.com
from flask import request

from .model_Follow import Follow


from app.exceptions import ValidationError # Creating a blog post from JSON (Deserialization)




class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), unique=True) ### name -> rolename

    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):   # for debugging and testing
        return '<Role %r>' % self.rolename ### self.name -> self.rolename
    # relationships in the database models
    users = db.relationship('User', backref='role', lazy='dynamic')
    # users = db.relationship('User', backref='role') # 'users' attribute returns the list of users associated with the role
###### SQLAlchemy relationship options: backref, primaryjoin, lazy, uselist, order_by, secondary, secondaryjoin


    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    # perm = permission
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):   ######
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():   # run right after db.create_all()
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(rolename=r).first()
            # role = ^^
            if role is None:
                role = Role(rolename=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.rolename == default_role)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username
    # role_id column added to the User model, defined as a foreign key, and that establishes the relationship
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # table 'roles' / column 'id'

    # Role Assignment
    # If mail of that user = 'FLASKE_ADMIN', then that user role = object with rolename 'Administrator'
    # If mail of that user != 'FLASKE_ADMIN' and still unset, then that user role = object with default=True
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.follow(self)   ### self-follow to see also our own posts
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

        if self.role is None:
            if self.email == 'namcaocomebackp66@gmail.com': ### current_app.config['FLASKE_ADMIN'] <<-- BE CAREFUL
                self.role = Role.query.filter_by(rolename='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()   # class 'Role' / field 'default'

    # Role Verification
    # evaluating whether a user has a given permission
    from flask_login import UserMixin, AnonymousUserMixin
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # Passwords
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    @password.setter
    def password(self, password):
        self.password_hash = werkzeugsecurity.generate_password_hash(password)
    def verify_password(self, password):
        return werkzeugsecurity.check_password_hash(self.password_hash, password)


    # User Registration confirmed via email
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)   # db.session.commit() at folder 'auth'/views.py line 64 def confirm(token)
        return True


    ## User profile information fields
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text()) # string that does not need a maximum length
    member_since = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    def recordsignuptimepoint(self):
        self.member_since = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    def recordlogintimepoint(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


    ## Avatar using https://gravatar.com/
    avatar_hash = db.Column(db.String(32))


    def change_email(self, token):
        # ...
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    posts = db.relationship('Post', backref='author', lazy='dynamic')   ####§§ Line 195 <=> Line 267






    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None
    followed = db.relationship('Follow',                            # stars relating to this fan
                               foreign_keys=[Follow.follower_id],   # fan
                               backref=db.backref('follower', lazy='joined'),   # .follower
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',                            # fans relating to this star
                                foreign_keys=[Follow.followed_id],   # star
                                backref=db.backref('followed', lazy='joined'),   # .followed
                                lazy='dynamic',
                                cascade='all, delete-orphan')
## If a user is following 100 other users, calling user.followed.all() will return a list of 100 Follow instances
    @property   #### method defined as a property => no () needed
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(self.id == Follow.follower_id)   # join at Join table "follows" / author_id belongs to Postclass # posts filtered: user id = follower id
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
#### User.add_self_follows()  => New update for the whole user database

    comments = db.relationship('Comment', backref='author', lazy='dynamic')



    ## token-based authentication support
    # ... expiration in 2 hours
    def generate_auth_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])



## Converting a user to a JSON serializable dictionary
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user



class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser



class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16



from markdown import markdown
import bleach
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))   ####§§ Line 195 <=> Line 267
    # ...
    body_html = db.Column(db.Text)
    # ...
    toquery_authornamestartswitha = db.Column(db.Boolean, default=False, index=True)
    @staticmethod
    def updatevalues_toqueryauthornamestartswitha():
        for p in Post.query.all():
            if p.author.username.startswith('a'):
                p.toquery_authornamestartswitha = True
            else:
                p.toquery_authornamestartswitha = False
            db.session.add(p)
            db.session.commit()
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))   ####

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    ## Converting a post to a JSON serializable dictionary
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        return json_post
    ## Creating a blog post from JSON
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

db.event.listen(Post.body, 'set', Post.on_changed_body)   ###***
# on_changed_body() function will be automatically invoked whenever the body field is set to a new value
# This function renders the HTML version of the body and stores it in body_html
# Step1: The markdown() function does an initial conversion to HTML   markdown(value, output_format='html')
# Step2: The result is passed to clean(), along with the list of approved HTML tags
# Step3: linkify() converts any URLs written in plain text into proper <a>



class Comment(db.Model):
    __tablename__ = 'commentsss'  # :)) NOT WORKS for 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))   ## tablename.id
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))   ## tablename.id

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)   ###***



class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.Text, index=True)
    searchtime = db.Column(db.DateTime, default=datetime.utcnow())

class Namstask(db.Model):
    __tablename__ = 'namstasks'

    id = db.Column(db.Integer, primary_key=True)
    taskname = db.Column(db.Text, index=True)
    runtime = db.Column(db.DateTime, index=True)
    runtime_todayed = db.Column(db.Boolean, index=True)####
    finished = db.Column(db.Boolean, default=False, index=True)

    info = db.Column(db.Text)
    info_show = db.Column(db.Text)
    desc = db.Column(db.Text)
    result = db.Column(db.Text)
    priority = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('tasktypes.id'))   # db.ForeignKey('table_name.attr')
    thisinfo_creationtime = db.Column(db.DateTime, default=datetime.utcnow())
    thisinfo_lastupdatetime = db.Column(db.DateTime, default=datetime.utcnow())

    est_endtime = db.Column(db.DateTime)  ## New 20 Oct 2021
    overlapping = db.Column(db.Boolean) ## New 20 Oct 2021

    matching_searchrequest = db.Column(db.Boolean, default=False, index=True)

    alive = db.Column(db.Boolean, default=False, index=True)
    trashed = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def on_changed_info(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3'] ################
        target.info_show = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Namstask.info, 'set', Namstask.on_changed_info)

class Tasktype(db.Model):
    __tablename__ = 'tasktypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True)

    tasks = db.relationship('Namstask', backref='Tasktype', lazy='dynamic')  ## all the tasks of some task type
                                                                            ## Namstask().id => Namstask().Tasktype

class NamsInsulin(db.Model):
    __tablename__ = "namsinsulins"

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('insulins.id'))
    insulin_name = db.Column(db.Text, index=True, unique=True)

    info = db.Column(db.Text)  #### predescription info; notes about personal usage, dosage
    info_show = db.Column(db.Text)

    last_purchasetime = db.Column(db.DateTime)
    lastpurchasetime_info = db.Column(db.Text)
    avgamount_perday = db.Column(db.Integer)  ## current level injected every day
    avgamount_pertime = db.Column(db.Integer) ## current level injected every time
    current_amount = db.Column(db.Integer)    #### CURRENT BALANCE AMOUNT

    currently_inuse = db.Column(db.Boolean, index=True)
    startusing_since = db.Column(db.DateTime)
    stopusing_since = db.Column(db.DateTime)

    lasttime_pumpchange_timestamp = db.Column(db.DateTime) #### NEW NEW (last time of the change in the level injected)
    lasttime_pumpchange_info = db.Column(db.Text) ## NEW NEW

    lasttimepoint_updatebalance = db.Column(db.DateTime)
    numberofdays_enoughinsulin = db.Column(db.Integer)

    alerted = db.Column(db.Boolean, index=True)

    @staticmethod
    def on_changed_info(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.info_show = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(NamsInsulin.info, 'set', NamsInsulin.on_changed_info)


class Insulin(db.Model):
    __tablename__ = "insulins"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.Text, index=True, unique=True)
    full_description = db.Column(db.Text)  #### identity colors, general dosage
    manufacturer = db.Column(db.Text)
    origin = db.Column(db.Text)

    storing_unit = db.Column(db.Text)  ## flexpen, box....
    amount_perstoringunit = db.Column(db.Text) ## 250, 300ml / 100 pills....

    NamisUsing = db.Column(db.Boolean, index=True)
    NamsInsulinss = db.relationship('NamsInsulin', backref='Insulin', lazy='dynamic')

    full_descriptionshow = db.Column(db.Text)
    @staticmethod
    def on_changed_info(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.full_descriptionshow = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Insulin.full_description, 'set', Insulin.on_changed_info)


class DeadLine(db.Model):
    __tablename__ = "deadlines"

    id = db.Column(db.Integer, primary_key=True)
    duty = db.Column(db.Text, index=True, unique=True)
    remember_info = db.Column(db.Text)
    rememberinfo_show = db.Column(db.Text)

    deadline_time = db.Column(db.DateTime)

    todayed = db.Column(db.Boolean, index=True) ## static attribute
    overdrafted = db.Column(db.Boolean, index=True) ## static attribute

    image_url = db.Column(db.Text)
    attachmentfile_info = db.Column(db.Text)

    @staticmethod
    def on_changed_info(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.rememberinfo_show = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(DeadLine.remember_info, 'set', DeadLine.on_changed_info)
