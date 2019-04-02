# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, redirect, flash
# from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie

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
