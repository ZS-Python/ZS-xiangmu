from . import user_blue
from flask import render_template,session,current_app,jsonify,redirect,url_for,request,g
from info.models import User,News,Category
from info import response_code,db,constants
from info.utils.first_storage import upload_file
from info.utils.comment import user_login_data


@user_blue.route('/user_news_list')
@user_login_data
def user_news_list():
    '''个人中心新闻列表'''
    # 1, 判断用户是否登陆
    user = g.user

    if not user:
        return redirect(url_for('index.index'))

    # 2, 接收参数(点击的页码)
    page = request.args.get('p',1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 3, 分页获取当前用户发布的新闻
    paginate = None
    try:
        paginate = News.query.filter(News.user_id == user.id).order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)

    # 4, 构造响应数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    # 响应新闻列表展示结果
    return render_template('news/user_news_list.html',context=context)





@user_blue.route('/news_release',methods=['GET','POST'])
@user_login_data
def news_release():
    '''个人中心新闻发布'''
    # 1, 判断用户是否登陆
    user = g.user

    if not user:
        return redirect(url_for('index.index'))

    # GET请求
    if request.method == 'GET':
        # 渲染分类列表、
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 删除‘最新’
        categories.pop(0)
        context = {
            'categories': categories
        }
        return render_template('news/user_news_release.html',context=context)

    # POST请求
    if request.method == 'POST':
        "发布新闻内容"
        # 1, 获取要发布的内容信息
        title = request.form.get("title")
        source = "个人发布"
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")

        # 2, 校验参数
        if not all([title,source,digest,content,index_image,category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
        try:
            index_image_data = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取图片失败')
        # 3, 把图片上传到七牛云
        try:
            key = upload_file(index_image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传图片失败')

        # 4, 把数据存储到数据库
        news = News()
        news.title = title
        news.source = source
        news.digest = digest
        news.content = content
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        news.category_id = category_id
        # status = 1代表审核中
        news.status = 1
        news.user_id = user.id

        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='存储新闻失败')

        # 5, 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='新闻发布成功')



@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    '''我的收藏'''
    # 1, 判断用户是否登陆
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 3, 接收参数
    # 默认显示第几页
    page = request.args.get('p',1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 2, 获取收藏的新闻数据分页显示
    try:
        paginate = user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
    except Exception as e:
        current_app.logger.error(e)

    # 3, 构造响应数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    # 4, 模型对象转换成字典对象列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }
    # 5, 响应收藏的结果
    return render_template('news/user_collection.html', context = context)


@user_blue.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    '''修改密码'''
    # 1, 判断用户是否登陆
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # GET请求
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    # POST请求
    if request.method == 'POST':
        # 1, 接收参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        # 2, 校验参数
        if not all([old_password,new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        # 3, 判断原密码是否正确
        if not user.check_passowrd(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='原密码输入错误')

        # 4, 保存新密码
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改密码失败')

        # 5,响应修改密码的结果
        return jsonify(errno=response_code.RET.OK, errmsg='修改密码成功')



@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    '''上传头像'''
    # 1, 判断用户是否登陆
    user = g.user
    if not user:
        return redirect(url_for('index.index'))


    if request.method == 'GET':
        # 准备填充资料页面的数据
        context = {
            'user': user.to_dict()
        }

        # 渲染基本资料页面
        return render_template('news/user_pic_info.html', context=context)

    if request.method == 'POST':
        # 上传图片

        # 1, 接收图片文件
        avatar = request.files.get('avatar')

        # 3, 检查参数是否收到
        try:
            avatar_data = avatar.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取图片失败')

        # 4, 上传图片

        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传图片失败')

        # 5, 将key(图片在七牛云的唯一标示)存储数据到数据库
        user.avatar_url = key

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='存储图片失败')

        # 构造响应数据，为了上传头像后立即刷新出新头像
        data = {
            'avatar_url': constants.QINIU_DOMIN_PREFIX + key
        }

        return jsonify(errno=response_code.RET.OK, errmsg='上传成功',data = data)





@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    '''设置基本资料'''
    # 1, 判断用户是否登陆
    user = g.user

    if request.method == 'GET':
        # 准备填充资料页面的数据
        context = {
            'user': user
        }

        # 渲染基本资料页面
        return render_template('news/user_base_info.html',context=context)

    if request.method == 'POST':
        # 1, 接收参数(个性签名,昵称,性别)
        nick_name = request.json.get('nick_name')
        gender = request.json.get('gender')
        signature = request.json.get('signature')

        # 2, 校验参数
        if not all([nick_name,gender,signature]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

        # 3, 保存参数
        user.nick_name = nick_name
        user.gender = gender
        user.signature = signature

        # 4, 同步到数据库
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='基本资料修改失败')

        # 5, 重新修改状态保持里的nick_name
        session['nick_name'] = nick_name

        # 6, 响应保存结果
        return jsonify(errno=response_code.RET.OK, errmsg='基本资料修改成功')



@user_blue.route('/user_info')
@user_login_data
def user_info():
    '''个人中心首页'''
    # 1, 判断用户是否登陆
    user = g.user

    # 限制： 用户必须登陆后才能进入个人中心(点击退出进入主页)
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user': user.to_dict()
    }

    return render_template('news/user.html',context = context)
