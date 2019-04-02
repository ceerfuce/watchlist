# -*- coding: utf-8 -*-
from watchlist import db

# 表名将会是 user （自动生成，小写处理）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


# 表名将会是 movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(20))