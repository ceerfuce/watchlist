# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
# 数据库设置
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
# 注意更新这里的路径，把 app.root_path 添加到 os.path.dirname() 中
# 以便把文件定位到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。 session 用来在请求间存
# 储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
# app 和 db 是程序实例和扩展对象，可在子文件中使用下面的导入语句来导入
# from watchlist import app, db

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
    from watchlist.models import User 
    user = User.query.first() 
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}

'''
在构造文件中，为了让视图函数、错误处理函数和命令函数注册到程序实例上，
我们需要在这里导入这几个模块。但是因为这几个模块同时也要导入构造文件中的程序实例，
为了避免循环依赖（A导入 B，B 导入 A），我们把这一行导入语句放到构造文件的结尾。
同样的， load_user() 函数和 inject_user() 函数中使用的模型类也在函数内进行导入。
'''
from watchlist import views, errors, commands