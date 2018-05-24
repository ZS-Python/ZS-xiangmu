from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect


class Config():
    # 配置秘钥:项目中CSRF和sessin主要用到,还有一些其他签名
    SCRSTE_KEY = '123456'

    #开启调试
    DEBUG = True
    # 连接Mysql数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_database/new_information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置Redis数据库
    REDIS_HOST = '192.168.211.130'
    REDIS_PORT = '6379'



app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
# redis_store是连接到redis数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启csrf保护,当我们不断使用flask_wtf中扩展的flask_form类自定义表单时, 需要自己开启csrf保护
CSRFProtect(app)


@app.route("/")
def index():
    return "index"

if __name__ == '__main__':

    # redis_store.set("name",'zhangsheng')

    app.run(debug=True)