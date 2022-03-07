# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from urllib.parse import quote

import json
import requests
import xmltodict
import sys
import logging




# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = ''     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = ''   # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = ''      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
scheme = 'https'           # 指定使用 http/https 协议来访问 COS
bucket = '' #bucket名需包含appid
key = ''#存储在存储桶内图片的对象键，图片大小不能超过2M，必须以/开头
matchthreshold = 0         #相似度，返回的分数中，只有超过 MatchThreshold 值的结果才会返回;默认为0
offset = 0                 #起始序号，默认值为0
limit = 10                 #返回数量，默认值为10，最大值为100
filter = ''     #针对入库时提交的 Tags 信息进行条件过滤。支持>、>=、<、<=、=、!=，多个条件之间支持 AND 和 OR 进行连接; 举例：key!="value"
host = bucket + '.cos.' + region + '.myqcloud.com'                 #生成此次请求用的HOST
url = scheme + '://' + host + key + '?ci-process=ImageSearch&action=SearchImage&MatchThreshold=' + str(matchthreshold) + '&Offset=' + str(offset) + '&Limit=' + str(limit) + '&Filter=' + quote(filter)

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

def escape(response):
    response = response.replace('&amp;', '&')
    response = response.replace('&lt;', '<')
    response = response.replace('&gt;', '>')
    response = response.replace('&quot;', '"')
    return response


sign = client.get_auth(
    Method='GET',
    Bucket=bucket,
    Key=key,
    Headers={'Host': host},
    Expired=120  # 120秒后过期，过期时间请根据自身场景定义
)

headers = {
  'Authorization': sign,
  'Content-Type': 'application/xml'
}

response = requests.request("GET", url, headers=headers)

if response.status_code == 200:
    print(escape(response.text))
    print(json.loads(json.dumps(xmltodict.parse(escape(response.text).replace('&', '&#38;')))))
elif response.status_code == 400:
    json_str = json.loads(json.dumps(xmltodict.parse(response.text.replace('&', '&#38;'))))
    print(f'\033[0;31mError Message: ' + json_str['Error']['Message'] + '\033[0m')
else:
    print('<' + str(response.status_code) + '>' + '\n' + response.text)
