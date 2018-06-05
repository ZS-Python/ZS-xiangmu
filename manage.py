from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db,modules  # 把表的模型导入manage.py
from info.models import User

app = create_app('dev')

# 创建脚本管理对象
manage = Manager(app)

# 让迁移和app和db关联
Migrate(app,db)

# 将迁移脚本添加到manage
manage.add_command('sql', MigrateCommand)


# 脚本： 底层封装好的函数, 函数暴漏在外面, 执行脚本命令时实际在调用函数
# 创建超级管理员用户(一个函数通过manage脚本对象加载成脚本命令, 执行时调用这个函数)

@manage.option('-u','-username',dest='username')
@manage.option('-p','-password',dest='password')
@manage.option('-m','-mobile',dest='mobile')
def createsuperuser(username,password,mobile):
    '''创建超级管理员'''
    if not all([username,password,mobile]):
        print('缺少参数')
    else:
        # 创建模型对象
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        # 指定为超级管理员
        user.is_admin = True

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)



if __name__ == '__main__':
    print(app.url_map)
    manage.run()