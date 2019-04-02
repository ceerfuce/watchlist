# -*- coding: utf-8 -*-
from flask import render_template

from watchlist import app

'''
使用app.errorhandler装饰器注册一个错误处理函数，
它的作用和视图函数类似，当 404 错误发生时，这个函数会被触发，
返回值会作为响应主体返回给客户端
'''
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码