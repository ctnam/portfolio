from . import db
from datetime import datetime

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),   # id of fan
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),   # id of star
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
