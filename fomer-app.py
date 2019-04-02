import os
import sys

import click
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
# 数据库设置
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。 session 用来在请求间存
# 储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'ceerfuce'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


# 表名将会是 user （自动生成，小写处理）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


# 表名将会是 movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(20))


'''    
name = 'Grey Li' 

movies = [ 
    {'title': 'My Neighbor Totoro', 'year': '1988'}, 
    {'title': 'Dead Poets Society', 'year': '1989'}, 
    {'title': 'A Perfect World', 'year': '1993'}, 
    {'title': 'Leon', 'year': '1994'}, 
    {'title': 'Mahjong', 'year': '1996'}, 
    {'title': 'Swallowtail Butterfly', 'year': '1996'}, 
    {'title': 'King of Comedy', 'year': '1999'}, 
    {'title': 'Devils on the Doorstep', 'year': '1999'}, 
    {'title': 'WALL-E', 'year': '2008'}, 
    {'title': 'The Pork of Music', 'year': '2012'}, 
] 
'''

'''
对于多个模板内都需要使用的变量，
我们可以使用app.context_processor装饰器注册一个
模板上下文处理函数
这个函数返回的变量（以字典键值对的形式）
将会统一注入到每一个模板的上下文环境中，
因此可以直接在模板中使用。
'''
@app.context_processor 
def inject_user():  # 函数名可以随意修改 
    user = User.query.first() 
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}

'''
在 app.route() 装饰器里，我们可以用 methods 关键字传递一个包含 HTTP 方法字符串的列
表，表示这个视图函数处理哪种方法类型的请求。默认只接受 GET 请求，下面的写法表示同时接
受 GET 和 POST 请求。
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    # Flask 会在请求触发后把请求信息放到 request 对象里
    # 它包含请求相关的所有信息
    if request.method == 'POST': # 判断是否是 POST 请求
        # 获取表单数据request.form.get
        # request.form 是一个特殊的字典，
        # 用表单字段的name 属性值可以获取用户填入的对应数据
        title = request.form.get('title') # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 20 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示
        return redirect(url_for('index')) # 重定向回主页
        
    # user = User.query.first()  # 读取用户记录
    movies = Movie.query.all()  # 读取所有电影记录
    # return render_template('index.html', user=user, movies=movies)
    # 使用模板上下文处理函数后，删除user变量定义，
    # 并删除在render_template函数里传入的关键字参数
    return render_template('index.html', movies=movies)

    
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # 下面是接受网页提交POST请求后的处理，如无POST请求，直接渲染movie
    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 20 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

    
'''
使用app.errorhandler装饰器注册一个错误处理函数，
它的作用和视图函数类似，当 404 错误发生时，这个函数会被触发，
返回值会作为响应主体返回给客户端
'''
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码
      
@app.route('/hello')
def hello_world():
    return 'Hello, World!'


@app.route('/user/<name>')
def hello_user(name):
    return 'Hello, user %s .' % name