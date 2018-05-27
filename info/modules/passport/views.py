# 注册和登陆
from . import passport_blue
from flask import request,abort,current_app,json,jsonify
# 导入captcha
from info.utils.captcha.captcha import captcha
from info import redis_store, constants,response_code
import re, random
from info.libs.yuntongxun.sms import CCP



@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    '''发送短信验证码'''
    # 1,接收参数(手机号,图片验证码,图片uuid)
    # 2,校验参数(是否存在,手机好是否合理)
    # 3,查询服务器存储的图片验证码
    # 4,和客户端传入的图片验证码进行比较
    # 5,如果成功,生成短信验证码
    # 6,调用CCP()封装的发送短信的方法,发送短信给手机
    # 7,存储短信验证码到服务器, 后来注册时判断输入的验证码是否正确
    # 8,响应发送短信验证码的结果

    # 1,接收参数(手机号,图片验证码,图片uuid) ajax发来的
    # 传过来的是字符串,里面是字典
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('moblie')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get('image_code_id')

    # 2,校验参数(是否存在,手机好是否合理)
    if not all([mobile,image_code_client,image_code_id]):
        # 响应给ajax的状态(errno表示状态码, errmsg表示状态说明) PARAMERR:代表参数错误
        return jsonify(errno = response_code.RET.PARAMERR, errmsg = '缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')

    # 3,查询服务器存储的图片验证码
    try:
        image_code_server = redis_store.get('imageCode: ' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询图片验证码失败')
    # 如果数据库没有错误,但查询出来的为空或者其他
    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='图片验证码不存在')

    # 4,和客户端传入的图片验证码进行比较 (服务器查出来的是大写,转成小写比较)
    if not image_code_server.lower() != image_code_client:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入验证码有误')

    # 5,如果成功,生成短信验证码(不足六位数字,前面用0补充)
    sms_code = '%06d' % random.randint(0, 999999)

    # 6,调用CCP()封装的发送短信的方法,发送短信给手机
    result = CCP().send_template_sms(mobile,[sms_code,5],1)  # 5; 5分钟后过期, 1: 表示1号默认短信模板
    if result != 0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='发送短信验证码失败')  # 第三方错误

    # 7,存储短信验证码到服务器, 后来注册时判断输入的验证码是否正确
    try:
        redis_store.set('SMS:' + mobile, sms_code, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='存储短信验证码失败')

    # 8,响应发送短信验证码的结果
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')



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

