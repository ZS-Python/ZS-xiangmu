from .import news_blue
from flask import render_template,session,current_app,abort
from info.models import News,User
from info import constants,db


# 把视图注册到蓝图
@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    '''显示新闻详情'''
    # 判断登陆中显示用户名, 退出了显示"登陆/注册"
    # 1, 从redis获取用户登陆信息,直接取user_id
    # 2, 显示点击排行
    # 3, 按点击的新闻的id获取对应的新闻详情
    # 4, 点击量加1,更新到数据库News表
    # 5, 判断用户是否收藏该新闻

    # 1, 从redis获取用户登陆信息,直接取user_id
    user_id = session.get('user_id')

    user = None
    # 判断是否信息存在,存在则显示该用户名
    if user_id:
        try:
            user = User.query.get(user_id)  # user是通过user_id创建的指定对象
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

    # 3, 按点击的新闻的id获取对应的新闻详情
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)

    # 4,点击量加1,更新到数据库News表
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 5, 判断用户是否收藏该新闻
    is_collected = False    # 默认没有收藏
    if user:
        if news in user.collection_news:  # user.collection_news表示该用户收藏的所有新闻,(用户表的外键)
            is_collected = True



    context = {
       'user':user,
       'news_clicks':news_clicks,
        'news':news.to_dict(),     # 对数据的优化(包括时间格式化,创建作者),把模型对象转成字典,前段省了很多工作
        'is_collected':is_collected
    }


    # 渲染新闻详情页面
    return render_template('news/detail.html',context = context)