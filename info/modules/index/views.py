from . import index_blue
from flask import render_template,current_app,session,request,jsonify
from info.models import User,News,Category
from info import constants,response_code


# 展示主页新闻
@index_blue.route('/news_list')
def index_news():
    '''提供主页新闻数据列表'''
     # http://127.0.0.1:5000/newslist?cid=1&page=2&per_page=10
    # 1,获取网址里的请求数据(新闻分类cid,当前第几页,每页多少条)
    # 2,校验参数是否是数字
    # 3,根据参数查询用户需要的数据,根据新闻发布时间倒序,并分页显示
    # 4,构造响应的新闻数据
    # 5,响应结果新闻数据

    # 1,获取请求数据(新闻分类cid,当前第几页,每页多少条)
    cid = request.args.get('cid', 1)  # 不写默认是1分类
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)  # 不写默认是10页
    # 这种request.args.get()接收数据的方式只能适用于GET请求下, 对应的ajax是$.get(){}发出的请求.

    # 2,校验参数是否是数字
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='参数有误')

    # 3,根据参数查询用户需要的数据,根据新闻发布时间倒序,并分页显示
    if cid == 1:
        # 所有新闻分类按发布时间倒序并分页
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        # 指定新闻分类按发布时间倒序并分页
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)

    print(paginate)  # <flask_sqlalchemy.Pagination object at 0x7f48d014c828>
    # paginate是个分页模型对象

    # 4,构造响应的新闻数据
    news_list = paginate.items
    # 取出来是个10个模型对象的列表
    # new_list = [New,New,New,New,New,New,New,New,New,New]

    # 总共页数
    total_page = paginate.pages
    # 当前在第几页
    current_page = paginate.page

    # 构造响应json数据的字典
    # news_list是模型对象列表,不支持json序列化, 字典和数组才可以,news_list转成字典列表才行
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())   # 这个方法在models.py中写好了.

    data = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    # 5,新闻数据响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='OK',data = data)





@index_blue.route('/')
def index():
    '''显示主页'''
    # 判断登陆中显示用户名, 退出了显示"登陆/注册"
    # 1, 从redis获取用户登陆信息,直接取user_id
    # 2, 主页点击排行
    # 3, 新闻分类标签展示


    # 1, 从redis获取用户登陆信息,直接取user_id
    user_id = session.get('user_id')

    user = None
    # 判断是否信息存在,存在则显示该用户名
    if user_id:
        try:
            user = User.query.get(user_id)    # user是通过user_id创建的指定对象
        except Exception as e:
            current_app.logger.error(e)

    # 2, 显示点击排行
    # 查询新闻数据,根据clicks的点击量进行倒序排序
    # news_clicks = [News1,News2,News3,News4,News5,News6,],每个模型对象
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3, 新闻分类标签展示
    categories = []
    try:
        categories =Category.query.all()
    except Exception as e:
        current_app.logger.error(e)


    # 渲染的很多
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'categories': categories
    }


    return render_template('news/index.html',context = context)


# 显示网页图标
@index_blue.route('/favicon.ico', methods=['GET'])
def favicon_show():
    # return '/home/python/Desktop/NewXaingMu/ZS-xiangmu/info/static/news/favicon.ico'

    # send_static_file是系统访问静态文件所调用的方法
    return current_app.send_static_file('news/favicon.ico')


