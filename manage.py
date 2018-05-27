from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
# 把表的模型导入manage.py
from info.modules import models


app = create_app('dev')

# 创建脚本管理对象
manage = Manager(app)

# 让迁移和app和db关联
Migrate(app,db)

# 将迁移脚本添加到manage
manage.add_command('sql', MigrateCommand)



if __name__ == '__main__':
    print(app.url_map)
    manage.run()