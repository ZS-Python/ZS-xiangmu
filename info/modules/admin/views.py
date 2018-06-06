from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,jsonify,abort
from info.models import User,constants,News,Category
import time, datetime
from info.utils.comment import user_login_data
from info import response_code,db
from info.utils.first_storage import upload_file



@admin_blue.route('/news_type',methods=['GET','POST'])
def news_type():
    '''新闻分类管理'''

    if request.method == 'GET':

        # 获取全部新闻分类
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)

        context = {
            'categories':categories
        }
        return render_template('admin/news_type.html',context=context)

    if request.method == 'POST':

        # 获取参数
        category_id = request.json.get('id')
        category_name = request.json.get('name')

        # 检验参数
        if not category_name:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        if category_id:
            # 修改分类
            try:
                category = Category.query.get(category_id)
            except Exception as e:
                current_app.logger.error(e)
            category.name = category_name

        else:
            # 添加分类
            category = Category()
            category.name = category_name
            db.session.add(category)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')

        # 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='操作成功')



@admin_blue.route('/news_edit_detail/<int:news_id>',methods=['GET','POST'])
def news_edit_detail(news_id):
    '''新闻编辑详情'''
    # GET请求方法
    if request.method == 'GET':
        # 获取新闻详情
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)

        # 获取新闻分类
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not categories:
            abort(404)

        context = {
            'news': news.to_dict(),
            'categories': categories
        }

        return render_template('admin/news_edit_detail.html',context=context)

    # POST请求方法
    if request.method == 'POST':
        # 编辑修改新闻内容

        # 接受参数
        news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")
        # 校验参数
        if not all([news_id,title,digest,content,category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')

        # 查询要编辑的新闻
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻失败')
        if not news:
            return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

        # 保存编辑
        if index_image:
            try:
                index_image_data = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取图片失败')
            if not index_image_data:
                return jsonify(errno=response_code.RET.NODATA, errmsg='图片不存在')
            # 上传图片到七牛云
            try:
                key = upload_file(index_image_data)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg='图片上传失败')

            # 保存图片的key
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key

        # 保存新闻对象
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改失败')

        # 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='修改成功')



@admin_blue.route('/news_edit')
def news_edit():
    '''新闻再次编辑展示界面'''
    # 接收参数
    page = request.args.get('p', 1)
    keyword = request.args.get('keyword')
    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 分页查询
    paginate = None
    try:
        if keyword:
            paginate = News.query.filter(News.status==0,News.title.contains(keyword)).order_by(News.create_time.desc()).paginate(page,
                                                                                                        10,
                                                                                                        False)
        else:
            paginate = News.query.filter(News.status==0).order_by(News.create_time.desc()).paginate(page,10,False)

    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 构造渲染数据
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

    return render_template('admin/news_edit.html',context=context)




@admin_blue.route('/news_review_detail/<int:news_id>',methods=['GET','POST'])
def news_review_detail(news_id):
    '''新闻审核中'''
    #  根据新闻id渲染界面

    # GET方法
    if request.method == 'GET':
        # 获取新闻详情数据
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)

        context = {
            'news': news
        }

        return render_template('admin/news_review_detail.html',context = context)


    # POST方法
    if request.method == 'POST':
        # 处理通过和拒绝通过逻辑

        # 接收参数
        news_id = request.json.get('news_id')
        action = request.json.get('action')
        reason = request.json.get('reason')

        # 校验参数
        if not all([news_id,action]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        if action not in ['accept','reject']:
            return jsonify(errno=response_code.RET.DBERR, errmsg='参数错误')

        # 判断要审核的新闻是否存在

        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='新闻查询失败')
        if not news:
            return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

        # 审核逻辑
        if action == 'accept':
            # 审核通过
            news.status = 0

        else:
            # 审核不通过
            if not reason:
                return jsonify(errno=response_code.RET.NODATA, errmsg='缺少原因')
            news.reason = reason
            news.status = -1

        # 同步到数据库
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')

        # 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='操作成功')





@admin_blue.route('/news_review')
def news_review():
    '''新闻审核列表显示'''
    # 接收参数
    page = request.args.get('p',1)
    keyword = request.args.get('keyword')

    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 分页获取未审核和未通过的新闻
    try:
        if keyword:
            # 根据输入的关键字搜索标题
            paginate = News.query.filter(News.status!=0,News.title.contains(keyword)).order_by(News.create_time.desc()).paginate(page,10,False)
        else:
            paginate = News.query.filter(News.status!=0).order_by(News.create_time.desc()).paginate(page,10,False)

        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 构造渲染数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }


    return render_template('admin/news_review.html',context=context)


@admin_blue.route('/user_list')
def user_list():
    '''用户列表'''
    # 接收参数
    page = request.args.get('p',1)
    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 分页查询
    paginate = None
    try:
        paginate = User.query.filter(User.is_admin==False).order_by(User.create_time.desc()).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 构造渲染数据
    users = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())

    context = {
        'users': user_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }


    return render_template('admin/user_list.html',context = context)


@admin_blue.route('/admin_exit')
def admin_exit():
    '''退出后台主页'''
    try:
        session.pop('user_id',None)
        session.pop('nick_name',None)
        session.pop('mobile',None)
        session.pop('is_admin',False)
    except Exception as e:
        current_app.logger.error(e)

    return redirect(url_for('admin.admin_login'))


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

    # 用户活跃度统计（横轴是每隔一天,纵轴是活跃用户的数量）
    active_date = []
    active_count = []

    t = time.localtime()
    # 获取当前的时间(字符串形式)
    today_begin = '%d-%02d-%02d' % (t.tm_year,t.tm_mon,t.tm_mday)
    # 转成时间的对象
    today_begin_date = datetime.datetime.strptime(today_begin,'%Y-%m-%d')
    # 今天的结束就是明天的开始,从当前时间开始往前推本个月, 展示最近半个月的活跃用户数量

    for i in range(0,15):
        # 开始时间
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 结束时间
        end_date = today_begin_date - datetime.timedelta(days=(i-1))

        #把时间添加到列表
        active_date.append(datetime.datetime.strftime(begin_date,'%Y-%m-%d'))
        # 把本次循环的开始时间到结束时间内活跃的用户数统计以下
        try:
            count = User.query.filter(User.is_admin==False,User.last_login>=begin_date,User.last_login<end_date).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)


    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count,
        'active_date': active_date,
        'active_count': active_count
    }

    return render_template('admin/user_count.html',context = context)



@admin_blue.route('/index',methods=['GET','POST'])
@user_login_data
def admin_index():
    '''管理员主页'''
    # 1, 判断用户是否登陆
    user = g.user

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

