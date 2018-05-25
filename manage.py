from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db


app = create_app('dev')


# 创建脚本管理对象
manage = Manager(app)

# 让迁移和app和db关联
Migrate(app,db)

# 将迁移脚本添加到manage
manage.add_command('sql', MigrateCommand)



@app.route("/")
def index():
    redis_store.set("name",'zhangsheng')

    # 测试session
    from flask import session
    # 把name:zs写入浏览器 cookies
    session['name'] = 'zs'

    return "index"



if __name__ == '__main__':

    manage.run()