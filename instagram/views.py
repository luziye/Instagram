# -*- encoding=UTF-8 -*-

from instagram import app, db
from models import User, Image, Comment
from flask import render_template, redirect, request, get_flashed_messages, flash
import random, hashlib
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    image = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html', images=image)


@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return render_template('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return render_template('/')
    return render_template('profile.html', user=user)


@app.route('/reloginpage/')
def relogin():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['relogin']):
        msg = msg + m
    return render_template('login.html', msg=msg)


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/reg/', methods={'post', 'get'})
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/reloginpage/', u'用户名和密码不能为空', 'relogin')
    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/reloginpage/', u'用户名已经存在', 'relogin')

    salt = '.'.join(random.sample('0123456789abcdefgABCDEFG', 10))
    m = hashlib.md5()
    m.update(password + salt)
    password = m.hexdigest()
    user1 = User(username, password, salt)
    db.session.add(user1)
    db.session.commit()
    login_user(user1)

    return redirect('/')


@app.route('/login/',methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg('/reloginpage/', u'用户名和密码不能为空', 'relogin')
    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/reloginpage/', u'用户名不存在', 'relogin')
    m = hashlib.md5()
    m.update(password + user.salt)
    if (m.hexdigest() != user.password):
        return redirect_with_msg('/reloginpage/', u'密码错误', 'relogin')
    login_user(user)
    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')
