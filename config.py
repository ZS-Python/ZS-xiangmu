from redis import StrictRedis



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


# 开发
class DevelopmentConfig(Config):
    pass

# 测试
class UnittestConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_database/new_information_test'

# 发布
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_database/new_information_online'


# 准备工厂方法
configs = {
    'dev': DevelopmentConfig,
    'pro':ProductionConfig,
    'unit':UnittestConfig
}