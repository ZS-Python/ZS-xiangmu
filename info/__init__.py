from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
# from config import Config, DevelopmentConfig, ProductionConfig, UnittestConfig
from config import configs


# 创建mysql数据库对象
db = SQLAlchemy()


def create_app(config_name):
    # 根据传入的参数, 创建不同app,参数就是外界传入的配置环境

    app = Flask(__name__ )

    app.config.from_object(configs[config_name])

    # 手动调用init_app(app)
    db.init_app(app)

    # redis_store是连接到redis数据库的对象
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)

    # 开启csrf保护,当我们不断使用flask_wtf中扩展的flask_form类自定义表单时, 需要自己开启csrf保护
    CSRFProtect(app)

    # 配置flask_session, 将session数据写入redis数据库
    Session(app)

    return app