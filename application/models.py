from .database import db
import datetime
from flask_login import UserMixin
from flask_wtf import FlaskForm 
from wtforms.validators import InputRequired, Email, Length
from wtforms import StringField, PasswordField, BooleanField

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    tracks = db.relationship("Trackers", backref = 'user')

class Trackers(db.Model):
    tracker_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tracker_name = db.Column(db.String, unique=True)
    tracker_type = db.Column(db.String, nullable = False)
    tracker_question = db.Column(db.String, nullable = True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable = False)
    logged = db.relationship("Logger", backref = "trackers")

class Logger(db.Model):
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_value = db.Column(db.String, unique=True, nullable = False)
    track_tracker = db.Column(db.String, db.ForeignKey("trackers.tracker_id"), nullable = False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])