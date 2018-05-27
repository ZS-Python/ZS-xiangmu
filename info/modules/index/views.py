from . import index_blue
from flask import render_template,current_app


# 把视图注册到蓝图
@index_blue.route('/')
def index():

    return render_template('news/index.html')


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon_show():
    # return '/home/python/Desktop/NewXaingMu/ZS-xiangmu/info/static/news/favicon.ico'

    # send_static_file是系统访问静态文件所调用的方法
    return current_app.send_static_file('news/favicon.ico')