from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import configs
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf import csrf
from info.utils.comment import do_rank



def create_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 创建mysql数据库对象
db = SQLAlchemy()

redis_store = None

def create_app(config_name):
    # 集成日志: 根据不同的配置环境,加载不同的日志等级
    create_log(configs[config_name].LEVEL_LOG)

    app = Flask(__name__ )

    # 根据传入的参数, 创建不同app,参数就是外界传入的配置环境
    app.config.from_object(configs[config_name])

    # 手动调用init_app(app)
    db.init_app(app)

    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT,decode_responses=True)

    # 开启csrf保护,当我们不使用flask_wtf中扩展的flask_form类自定义表单时, 需要自己开启csrf保护
    CSRFProtect(app)

    # 开启csrf_token保护
    # 1, 开启csrf_token保护
    # 请求勾子: 服务器先自动生成csrf_token值, 在每次请求结束后都把csrf_token值写入到浏览器的cookie.
    @app.after_request
    def after_request(response):
        # 2,生成csrf_token值
        csrf_token = csrf.generate_csrf()
        # 3, 把csrf_token写入浏览器
        response.set_cookie('csrf_token',csrf_token)
        return response

    # 将自定义函数转换成模板可直接执行的过滤器
    app.add_template_filter(do_rank, 'rank')

    # 配置flask_session, 将session数据写入redis数据库
    Session(app)

    # 注册路由到app(在哪里注册就在哪里导入蓝图)
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    # 把passport路由注册到app
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)


    return app