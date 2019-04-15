# -*- coding:utf-8 -*-
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()
db_Received_flag = False


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash=generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)



class Send(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    body = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)


class Received(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    body = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)
