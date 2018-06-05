import qiniu

access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'


def upload_file(data):
    # 上传文件到七牛云
    # :param
    # data: 要上传的文件的二进制
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)

    print(ret['key'])
    # 判断是否上传成功
    if info.status_code != 200:
        raise Exception('七牛上传失败')

    # 将来要存储到数据库中的
    return ret['key']


# if __name__ == '__main__':
#     with open('/home/python/Desktop/123.jpg','rb')as file:
#         upload_file(file.read())