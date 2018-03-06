# -*- encoding=UTF-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')
db = SQLAlchemy(app)
app.secret_key = 'instagram'
login_manager = LoginManager(app)
login_manager.login_view='/reloginpage/'

from instagram import views, models
