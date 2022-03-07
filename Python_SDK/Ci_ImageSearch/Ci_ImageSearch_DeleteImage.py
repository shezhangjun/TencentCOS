# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

import json
import requests
import xmltodict
import sys
import logging


# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = ''     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = ''    # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = ''        # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                   # COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
scheme = 'https'   # 指定使用 http/https 协议来访问 COS
bucket = ''        #bucket名需包含appid
key = ''           #存储在存储桶内图片的对象键，图片大小不能超过2M，必须以/开头
entityId = ''
host = bucket + '.cos.' + region + '.myqcloud.com'                 #生成此次请求用的HOST
url = scheme + '://' + host + key + '?ci-process=ImageSearch&action=DeleteImage'
jsonbody = {"Request": [{"EntityId": entityId}]}

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

def json_to_xml(json_str):
    """
    # xmltodict库的unparse()json转xml
    # 参数pretty 是格式化xml
    :param json_str
    :return: xml_str
    """
    xml_str = xmltodict.unparse(json_str, pretty=1)
    return xml_str

sign = client.get_auth(
    Method='POST',
    Bucket=bucket,
    Key=key,
    Headers={'Host': host},
    Expired=120  # 120秒后过期，过期时间请根据自身场景定义
)

headers = {
  'Authorization': sign,
  'Content-Type': 'application/xml'
}

response = requests.request("POST", url, headers=headers, data=json_to_xml(jsonbody))

if response.status_code == 200:
    print(f'\033[0;32mSuccess Delete Image!\033[0m')
elif response.status_code == 400:
    json_str = json.loads(json.dumps(xmltodict.parse(response.text.replace('&', '&#38;'))))
    print(f'\033[0;31mError Message: ' + json_str['Error']['Message'] + '\033[0m')
else:
    print('<' + str(response.status_code) + '>' + '\n' + response.text)
