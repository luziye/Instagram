# -*- encoding=UTF-8 -*-

from instagram import app, db
from models import User, Image, Comment
from flask import render_template, redirect, request, get_flashed_messages, flash, send_from_directory
import random, hashlib, json, uuid, os
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
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imvo = {'uer_id': image.user_id, 'url': image.url, 'comment_count': len(image.comment)}
        images.append(imvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/reloginpage/')
def relogin():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['relogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category)
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
    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')


@app.route('/login/', methods={'post', 'get'})
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
    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/image/<image_name>/')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/upload', methods={'post'})
def upload():
    # print request.files
    file = request.files['file']
    # print dir(file)
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXTA']:
        # 上传保存的文件名，随机生成
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        # 保存图片文件
        url = save_to_local(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content'].strip()
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({'code': 0,
                       'id': comment.id,
                       'content': comment.content,
                       'username': comment.user.username,
                       'user_id': comment.user_id})


@app.route('/index/images/<int:page>/<int:perpage>/')
def index_images(page, perpage):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=perpage, error_out=False)
    map = {'has_next', paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0, min(2, len(image.comment))):
            comment = image.comment[i]
            comments.append({'username': comment.user.username,
                             'user_id': comment.user_id,
                             'content': comment.content})
            imvo = {'user_id': image.user_id,
                    'url': image.url,
                    'comment': comment,
                    'comment_count': len(image.comment),
                    'id': image.id,
                    'head_url': image.user.head_url,
                    'created_date': str(image.created_date)}
            images.append(imvo)
        map['images'] = images
    return json.dumps(map)
