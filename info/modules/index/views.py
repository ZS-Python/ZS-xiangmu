from . import index_blue
from flask import render_template,current_app,session
from info.models import User


# 把视图注册到蓝图
@index_blue.route('/')
def index():
    # 判断登陆中显示用户名, 退出了显示"登陆/注册"
    # 1, 从redis获取用户登陆信息,直接取user_id
    user_id = session.get('user_id')

    user = None
    # 2, 判断是否信息存在,存在则显示该用户名
    if user_id:
        try:
            user = User.query.get(user_id)    # user是通过user_id创建的指定对象
        except Exception as e:
            current_app.logger.error(e)

    # 渲染的很多
    context = {
        'user':user
    }


    return render_template('news/index.html',context = context)

# 显示网页图标
@index_blue.route('/favicon.ico', methods=['GET'])
def favicon_show():
    # return '/home/python/Desktop/NewXaingMu/ZS-xiangmu/info/static/news/favicon.ico'

    # send_static_file是系统访问静态文件所调用的方法
    return current_app.send_static_file('news/favicon.ico')


