# -*- coding=utf-8
#author v_yyjwang
#Python2.x - 3.x
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
# 设置用户属性, 包括 secret_id, secret_key, region
# APPID 已在配置中移除，请在参数 Bucket 中带上 APPID。Bucket 由 BucketName-APPID 组成
secret_id = ''     # 替换为用户的 secret_id
secret_key = ''     # 替换为用户的 secret_key
token = None               # 使用临时密钥需要传入 Token，默认为空,可不填
region = ''    # 替换为用户的 region
scheme = 'http'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)  # 获取配置对象

client = CosS3Client(config) #实例化Client对象