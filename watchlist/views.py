# -*- coding: utf-8 -*-

import requests
import bs4

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
    data = datatable(movies)
    tableinfo = gentable(data)
    return render_template('index.html', movies=movies, tableinfo=tableinfo)

    
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

    
# 功能函数
headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'} 

# 从雪球网页标题获取品种信息
def getxqwebdata(code):
    url = 'https://xueqiu.com/S/%s' % code
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem %s' % exc)
    # return res.text
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    data = soup.title.string.split()
    cell = code, data[0], data[1], data[2][1:-1]
    print(cell)
    return cell

# 将两个品种配对放在一个列表中    
def datapair(fund, index):
    # cellpair = getxqwebdata(fund), getxqwebdata(index)
    cellpair = list(getxqwebdata(fund))
    cellpair.extend(list(getxqwebdata(index)))
    print(cellpair)
    return cellpair

# 要查询的所有品种对的列表，查询完后放在二维列表中    
def datatable(table):
    finaldata = []
    for item in table:
        finaldata.append(datapair(item.title, item.year))
        # finaldata.append(datapair(item['title'], item['year']))
    return  finaldata

# 生成表格的HTML文本    
def gentable(data):
    table_item = ['基金代码','基金名称','价格','涨跌幅','指数代码','指数名称','价格','涨跌幅']
    table_text= '<table><tr>'
    for item in table_item:
        table_text=table_text+'<th>'+item+'</th>'
    table_text=table_text+'</tr>'
    for row in data:
        table_text=table_text+'<tr>'
        for item in row:
            table_text=table_text+'<td>'+item+'</td>'
        table_text=table_text+'</tr>'
    table_text=table_text+'</table>'
    return table_text    