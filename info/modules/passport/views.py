# 注册和登陆
from . import passport_blue
from flask import request,abort,current_app
# 导入captcha
from info.utils.captcha.captcha import captcha
from info import redis_store, constants


@passport_blue.route('/image_code')
def image_code():
    '''接收浏览器发来的图片验证码的请求,提供图片验证码'''
    # 1, 接收参数(uuid唯一标示)
    # 2, 判断参数是否存在
    # 3, 生成图片验证码
    # 4, 保存图片验证码到redis
    # 5, 响应图片验证码

    # 1, 接收参数(uuid唯一标示)  args专门获取查询字符串的
    imageCodeId = request.args.get('imageCodeId')

    # 2, 判断参数是否存在
    if not imageCodeId:
        abort(403)     # 没有uuid标示,不准浏览器访问

    # 3, 生成图片验证码 (有现成的生成工具)
        # 新建包utils,把生成工具captcha放进去(PIL模块需要自己安装: 虚拟环境-pip install Pilow
    name, text, image = captcha.generate_captcha()
        # text是验证码数字,需要存入redis, image返回给浏览器

    # 4, 保存图片验证码到服务器
    try:                                                    # 过期时间已设置300秒
        redis_store.set('imageCode: ' + imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5, 响应图片验证码
    return image

