#### Creating Fake Blog Post Data
# pip install faker
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post

def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                username=fake.user_name(),
                password='password',
                confirmed=True,
                name=fake.name(),
                location=fake.city(),
                about_me=fake.text(),
                member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError: # In the unlikely event that a duplicate is generated
            db.session.rollback() # The exception is handled by rolling back the session to cancel that duplicate user

def posts(count=100):
    fake = Faker()
    user_count = User.query.count()  # how many users?
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first() # a different random user is obtained each time
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
