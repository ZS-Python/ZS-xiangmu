from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand


class Config():
    # 配置秘钥:项目中CSRF和sessin主要用到,还有一些其他签名
    SECRET_KEY = '123456'

    #开启调试
    DEBUG = True
    # 连接Mysql数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_database/new_information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置Redis数据库
    REDIS_HOST = '192.168.211.130'
    REDIS_PORT = '6379'

    # 配置flask_session, 将session数据写入redis数据库
    # 指定session存储在redis
    SESSION_TYPE = 'redis'
    # 告诉session redis的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 是否将session签名后在存储
    SESSION_USE_SIGNER = True
    # 当SESSION_USE_SIGNER为True时,设置session的有效期才可以成立,正好默认就是True
    PERMANENT_SESSION_LIFETIME = 60*60*24

app = Flask(__name__ )

app.config.from_object(Config)

db = SQLAlchemy(app)
# redis_store是连接到redis数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启csrf保护,当我们不断使用flask_wtf中扩展的flask_form类自定义表单时, 需要自己开启csrf保护
CSRFProtect(app)

# 配置flask_session, 将session数据写入redis数据库
Session(app)

# 创建脚本管理对象
manage = Manager(app)

# 让迁移和app和db关联
Migrate(app,db)

# 将迁移脚本添加到manage
manage.add_command('sql', MigrateCommand)



@app.route("/")
def index():
    # redis_store.set("name",'zhangsheng')

    # 测试session
    from flask import session
    # 把name:zs写入浏览器 cookies
    session['name'] = 'zs'

    return "index"



if __name__ == '__main__':

    manage.run()