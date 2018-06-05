from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for
from info.models import User
import time, datetime


@admin_blue.route('/user_count')
def user_count():
    '''统计用户'''

    # 总用户
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin != True).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月增长数
    month_count = 0
    # 计算每月开始时间,比如每月2018-06-01 00:00:00
    t = time.localtime()
    # 生成当前月份开始时间的字符串
    month_begin = '%d-%02d-01' % (t.tm_year,t.tm_mon)
    month_begin_date = datetime.datetime.strptime(month_begin, '%Y-%m-%d')

    try:
        month_count = User.query.filter(User.is_admin != True, User.create_time>month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 天增长数
    day_count = 0
    # 计算每月开始时间,比如每月2018-06-05 00:00:00
    t = time.localtime()
    # 生成当前月份开始时间的字符串
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon,t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin != True, User.create_time>day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)


    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count
    }

    return render_template('admin/user_count.html',context = context)



@admin_blue.route('/index',methods=['GET','POST'])
def admin_index():
    '''管理员主页'''
    # 1, 判断用户是否登陆
    user_id = session.get('user_id')
    user = None
    # 判断是否信息存在,存在则显示该用户名
    if user_id:
        try:
            user = User.query.get(user_id)  # user是通过user_id创建的指定对象
        except Exception as e:
            current_app.logger.error(e)

    # is_admin = session.get('is_admin',False)
    # if not user or not is_admin:
    if not user:
        return redirect(url_for('admin.admin_login'))
    # admin/index里只应该管理员登陆, 不管非管理员,所以只看管理员是不是已登陆状态.不管is_admin.

    context = {
       'user': user.to_dict()
    }

    return render_template('admin/index.html',context=context)

    # 问题如何让非管理员用户登陆admin/login时自动调到新闻主页？(这就直接拦截非管理员登陆到admin主页了)
    # 请求勾子, 在admin蓝图中__init__中,定义一个每次请求之前执行的请求勾子, 在所有用户
    # 每次访问网点之前,就把非管理员限制住了,只要访问了admin的站点,自动重定向到新闻主页.



@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    '''管理员登陆'''
    if request.method == 'GET':
        # 如果管理员已经登陆,直接进入主页
        user_id = session.get('user_id',None)
        is_admin = session.get('is_admin',False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))


        return render_template('admin/login.html')

    if request.method == 'POST':
        '''管理员(非管理员)登陆'''
        # 1, 接收参数(接收form表单传来的值)
        username = request.form.get('username')
        password = request.form.get('password')

        # 2, 校验参数
        if not all([username,password]):
            return render_template('admin/login.html',errmsg='缺少参数')

        # 3, 查询管理员是否存在
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html', errmsg='查询管理员账号失败')
        if not user:
            return render_template('admin/login.html',errmsg='用户名或者密码错误')

        # 校验密码
        if not user.check_passowrd(password):
            return render_template('admin/login.html',errmsg='用户名或者密码错误')

        # if not user.is_admin:
        #     return render_template('admin/login.html',errmsg='用户权限不够')

        # 状态保持
        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        # 登陆成功转到主页
        return redirect(url_for('admin.admin_index'))

