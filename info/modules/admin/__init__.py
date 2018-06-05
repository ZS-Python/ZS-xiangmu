from flask import Blueprint,redirect,session,url_for,request

admin_blue = Blueprint('admin',__name__,url_prefix='/admin')

from . import views




# 请求勾子(每次请求之前执行)
@admin_blue.before_request
def check_admin():
    '''每次访问admin站点时需要做用户身份验证'''
    is_admin = session.get('is_admin',False)
    # 单独根据is_admin判断不行,会导致连管理员都进不去后台了,
    # 所以需要放开后台登陆界面的权限,同时限制非管理员不能登陆到后台主页

    #  1,在未登录状态下, 无论什么身份的用户访问站点admin/login时, 都会显示当前登陆界面
    #  2,如果管理员已登陆,该条件不成立,会直接登陆后台主页
    #  3,如果非管理员已登陆,和第一种情况一样,因为is_admin= False
    #  4,如果非管理员此时登陆账户, 点击登陆按钮后,发出新的请求，又要在这里重新判断一次,
        # 因为is_admin=False,新的请求路由是admin/index, 所以条件成立, 跳转到新闻主页
    #  5,如果管理员登陆, 点登陆请求后,也是重新再判断一次, 因为is_true是Ture, 新的请求
        # 路由是admin/login, 所以条件不成立, 会切换到自己的请求站点也就是admin/index.
    if not is_admin and not request.url.endswith('/admin/login'):
        return redirect(url_for('index.index'))
