#Importing Libraries.
from flask import Flask
from application.database import db
from flask_bootstrap import Bootstrap
import os


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'secretkey__'
  app.config['SECURITY_PASSWORD_SALT'] = 'secretsalt__'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quantified.sqlite3'
  bootstrap = Bootstrap(app)
  db.init_app(app)
  app.app_context().push()
  return app

app = create_app()



#import all controllers
from application.controllers import *

#Start the App.
if __name__ == '__main__':
  # Run the Flask app
  app.run(
    host='0.0.0.0',
    debug=True,
  )
