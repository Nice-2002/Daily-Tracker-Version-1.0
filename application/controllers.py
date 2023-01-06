from flask import request, redirect, render_template
from flask_security import LoginForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from .database import db
from .models import Trackers, Logger, User, LoginForm, RegisterForm
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import numpy as np
import matplotlib.pyplot as plt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#index page

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    tracker = Trackers.query.filter_by(user_id = current_user.id).all()
    return render_template("index.html", tracker = tracker)

#Controllers related to trackers

@app.route("/tracker/create", methods = ["GET", "POST"])
def create_tracker():
    if request.method == "POST":
        track_name = request.form['tracker_name']
        track_question = request.form['tracker_question']
        track_type = request.form['track_type']
        user_id = current_user.id
        
        tr = Trackers.query.all()
        for t in tr:
            if t.tracker_name == track_name:
                return render_template("tracker_already_exist.html")

        track = Trackers(
            tracker_name = track_name,
            tracker_question = track_question,
            tracker_type = track_type,
            user_id = user_id
        )
        db.session.add(track)
        db.session.commit()
        return redirect('/')
    return render_template("create_tracker.html")


@app.route("/tracker/<int:tracker_id>/delete", methods = ["GET", "POST"])
def delete_tracker(tracker_id):
    track = Trackers.query.get(tracker_id)
    logs = track.logged
    for log in logs:
        db.session.delete(log)
    db.session.delete(track)
    db.session.commit()    
    return redirect('/')



@app.route("/tracker/<int:tracker_id>/update", methods = ["GET", "POST"])
def update_tracker(tracker_id):
    if request.method == 'POST':
        track = Trackers.query.get(tracker_id)
        track_name = request.form['tracker_name']
        track_ques = request.form['tracker_question']
        track_type = request.form['track_type']
        
        track.tracker_name = track_name
        track.tracker_question = track_ques
        track.tracker_type = track_type
        
        db.session.commit()
        return redirect('/')
    tracker = Trackers.query.get(tracker_id)
    return render_template('update_tracker.html', tracker = tracker)

@app.route("/tracker/<int:tracker_id>", methods = ["GET"])
def view_all_logs(tracker_id):
    tracker = Trackers.query.get(tracker_id)
    logs = tracker.logged
    data = {}
    #generating bar graph for log numeric log values
    if tracker.tracker_type == 'number':
        for log in logs:
            data[log.timestamp.strftime("%Y%m%d%H%M%S")] = int(log.log_value)
        times = list(data.keys())
        times = ['-'.join(s[i:i+2] for i in range(0, len(s), 2) if i != 0) for s in times]
        values = list(data.values())
        fig = plt.figure()
        plt.bar(times, values, color ='maroon', width = 0.4)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Timeline")
        plt.ylabel("Log value")
        fig.savefig('static/my_plot.png')

    return render_template("tracker_details.html", logs = logs, tracker = tracker)

@app.route("/tracker/<int:tracker_id>/log", methods = ["GET", "POST"])
def log_data(tracker_id):
    if request.method == "POST":
        tracker = Trackers.query.get(tracker_id)
        log_value = request.form['input_val']
        track = Logger(
            log_value = log_value
        )
        tracker.logged.append(track)
        db.session.commit()
        return redirect('/')
    track = Trackers.query.get(tracker_id)
    return render_template("log_data_into_tracker.html", tracker = track)

#Controllers related to log

@app.route("/logger/<int:tracker_id>/delete/<int:log_id>", methods = ["GET", "POST"])
def delete_log(tracker_id,log_id):
    log = Logger.query.get(log_id)
    db.session.delete(log)
    db.session.commit()
    return redirect('/tracker/'+str(tracker_id))

@app.route("/logger/<int:tracker_id>/update/<int:log_id>", methods = ["GET", "POST"])
def update_log(tracker_id,log_id):
    if request.method == 'POST':
        log = Logger.query.get(log_id)
        db.session.delete(log)
        tracker = Trackers.query.get(tracker_id)
        log_value = request.form['input_val']
        track = Logger(
            log_value = log_value
        )
        tracker.logged.append(track)
        db.session.commit()
        return redirect('/tracker/'+str(tracker_id))
    log = Logger.query.get(log_id)
    tracker = Trackers.query.get(tracker_id)
    return render_template('update_log.html', log = log, tracker = tracker)

#Login related controllers

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/')
        else:
            return render_template('user_not_found.html')
    return render_template('login.html', form=form)

@app.route('/signup', methods = ["GET", "POST"])
def signup():
    form = RegisterForm()

    user = User.query.filter_by(username = form.username.data).first()
    if not user:
        _email = User.query.filter_by(email = form.email.data).first()
        if _email:
            return render_template('email_used.html')
    else:
        return render_template('username_used.html')

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html', form=form)
 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/delete_account')
@login_required
def delete_account():
    trackers = Trackers.query.filter_by(user_id = current_user.id).all()
    for track in trackers:
        logs = track.logged
        for log in logs:
            db.session.delete(log)
        db.session.delete(track)
    user = current_user
    db.session.delete(user)
    db.session.commit()
    return redirect('/')