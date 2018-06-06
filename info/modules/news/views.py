from .import news_blue
from flask import render_template,session,current_app,abort,request,jsonify,g
from info.models import News,User,Comment,CommentLike
from info import constants,db,response_code
from info.utils.comment import user_login_data
# 把视图注册到蓝图


@news_blue.route('/comment_like',methods=['POST'])
def comment_like():
    '''点赞和取消点赞'''
    # 1,获取用户信息
    user = g.user

    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登陆')

    # 2, 接收参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 3, 校验参数
    if not all([comment_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    if action not in ['add','remove']:
        return jsonify(errno=response_code.RET.DBERR, errmsg='参数错误')

    # 4, 查询要点赞的评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg='评论不存在')

    # 5, 点赞和取消点赞
    # 点赞和取消点赞之前要查询点赞记录存在不存在
    comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,CommentLike.comment_id == comment_id).first()

    if action == 'add':
        # 如果点赞记录不存在才能点赞
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.comment_id = comment_id
            comment_like_model.user_id = user.id
            # 累加点赞量
            comment.like_count += 1

            db.session.add(comment_like_model)

    if action == 'remove':
        # 如果点赞记录存在才能取消点赞
        if comment_like_model:
            # 删除点赞记录
            db.session.delete(comment_like_model)
            # 累减点赞量
            comment.like_count -= 1

    # 更新数据库到
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 6, 响应点赞和取消点赞的结果
    return jsonify(errno=response_code.RET.OK, errmsg='OK')



@news_blue.route('/news_comment',methods=['POST'])
@user_login_data
def news_comment():
    '''新闻评论和回复评论'''
    # 1, 判断用户是否登陆
    user = g.user

    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登陆')

    # 2, 接收参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3, 校验参数
    if not all([news_id,comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='参数错误')

    # 4, 查看新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

    # 5, 评论新闻和回复评论
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    # 评论回复
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败')

    # 为了评论显示给用户看, 需要将评论内容响应给页面.
    # 构造响应数据
    # data = {
    #     'comment':comment.to_dict()
    # }


    # 6, 响应评论和回复结果
    return jsonify(errno=response_code.RET.OK, errmsg='评论成功',data = comment.to_dict())





@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    '''新闻收藏和取消收藏'''
    # 1, 判断用户是否登陆
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登陆')


    # 2, 接收参数(news_id, action(collect, cancel_collect))
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3, 校验参数
    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=response_code.RET.DBERR, errmsg='参数有误')

    # 4, 查询新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.DBERR, errmsg='新闻不存在')

    # 5, 收藏和取消收藏
    if action == 'collect':
        # 如果是收藏,把新闻添加到用户新闻收藏表,（User中的关系表：collection_new连表查询）
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')

    # 6, 响应收藏和取消收藏的结果
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')


@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    '''显示新闻详情'''
    # 判断登陆中显示用户名, 退出了显示"登陆/注册"
    # 1, 从redis获取用户登陆信息,直接取user_id
    # 2, 显示点击排行
    # 3, 按点击的新闻的id获取对应的新闻详情
    # 4, 点击量加1,更新到数据库News表
    # 5, 判断用户是否收藏该新闻
    # 6, 展示新闻评论和评论回复

    # 1, 从redis获取用户登陆信息,直接取user_id
    user = g.user

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
        if news in user.collection_news:  # user.collection_news表示该用户收藏的所有新闻,(用户表的关联表)
            is_collected = True

    # 6, 展示所有用户的新闻评论和评论回复
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()  # 按时间倒序查看全部的评价
    except Exception as e:
        current_app.logger.error(e)

    comment_like_ids = []
    if user:
        try:
            # 为了用户登陆后自动显示已点赞的高亮
            # 先查询当前用户点赞了的所有评论
            comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id)
            # 取出这些评论对应的id,(列表生成式)
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
            # comment_like_ids是个列表,里面是当前用户已点赞的评论的id号
        except Exception as e:
            current_app.logger.error(e)


    # 遍历对象列表,转成字典列表(为了做些数据的格式化等处理,不转也可以,js自动获取里面的内容)
    comments_dict_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 在渲染评论时添加是否点赞的调价,默认是未点赞
        comment_dict['is_like'] = False

        # 遍历所有评论, 如果有评论的id在当前用户已经点赞的评论id的列表中,则在这条评论渲染时把‘赞‘置为高亮.即已赞状态
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comments_dict_list.append(comment_dict)


    context = {
       'user': user.to_dict() if user else None,
       'news_clicks': news_clicks,
       'news': news.to_dict(),     # 对数据的优化(包括时间格式化,创建作者),把模型对象转成字典,前段省了很多工作
       'is_collected': is_collected,
       'comment': comments_dict_list
    }


    # 渲染新闻详情页面
    return render_template('news/detail.html',context = context)
