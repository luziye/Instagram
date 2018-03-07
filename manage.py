# -*- encoding=UTF-8 -*-
from instagram import app, db
from flask_script import Manager
from instagram.models import User, Image, Comment
from sqlalchemy import and_, or_
import random

manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

@manager.command
def add_user():
    user=User.query.get(100)
    for i in range(0,5):
        db.session.add(Image(get_image_url(),user.id))
    db.session.commit()


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i + 1), 'a' + str(i)))
        for j in range(0, 3):
            db.session.add(Image(get_image_url(), i + 1))
            for k in range(0, 3):
                db.session.add(Comment('this is a comment' + str(k), 1 + 3 * i + j, i + 1))
    db.session.commit()
    #删除
    for i in range(50,100,2):
        comment=Comment.query.get(i)
        db.session.delete(comment)
    db.session.commit()

    #更新
    # for i in range(0, 100, 2):
    #     u = User.query.get(i)
    #     u.username = '[NEW]'
    # db.session.commit()
    User.query.filter_by(id=51).update({'username':'[NEW]'})
    db.session.commit()

    # 查询
    print 1, User.query.get(4)
    print 2, User.query.filter_by(id=5).first()
    print 3, User.query.order_by(User.id.desc()).offset(1).limit(2).all()
    print 4, User.query.filter(User.username.endswith('0')).limit(3).all()
    print 5, User.query.filter(or_(User.id == 88, User.id == 99)).all()
    print 6, User.query.filter(and_(User.id > 88, User.id < 93)).all()
    print 7, User.query.filter(and_(User.id > 88, User.id < 93)).first_or_404()
    print 8, User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items
    user = User.query.get(1)
    print 9, user.images
    image = Image.query.get(1)
    print 10, image.user


if __name__ == '__main__':
    manager.run()
