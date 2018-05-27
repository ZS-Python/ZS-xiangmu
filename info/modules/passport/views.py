# 注册和登陆
from . import passport_blue


@passport_blue.route('/image_code')
def image_code():
    '''接收浏览器的图片验证码的请求,提供图片验证码'''
    pass