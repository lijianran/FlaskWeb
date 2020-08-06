import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':   #如果用户提交了表单，request.method将会是post,就会开始验证用户的输入
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:   #如果用户名是空
            error = '用户名错误.'
        elif not password:   #如果密码为空
            error = '密码错误.'
        elif db.execute(       #都有的话，就查看用户名是否重复
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:      #重复的话，就提示重复
            error = '用户{} 已经被注册了.'.format(username)

        if error is None:     #如果没有出现错误，就将用户注册的信息填入数据库内
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))   #后面这个函数给用户密码添加保密
            )
            db.commit()    #提交数据库
            return redirect(url_for('auth.login'))   #注册完之后，跳转到登录界面

        flash(error)   #返回错误

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:    #如果提交的用户名，没有在数据库中的话
            error = '用户名不存在，或不正确.'
        elif not check_password_hash(user['password'], password):  #密码不正确的话
            error = '密码不正确.'

        if error is None:
            session.clear()   #session就相当于一个字典，验证成功，用户的id被储存于一个新的会话中
            session['user_id'] = user['id']
            return redirect(url_for('lijing.board'))#登录成功就跳转到另一个页面

        flash(error)

    return render_template('lijing/login.html')#就是在用户注册出错时，再显示一个注册表



@bp.before_app_request
def load_logged_in_user():   #检查用户id是否已经存储在session中，并从数据库中获取用户数据
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(      #如果用户存在，获取用户数据
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():   #注销
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
