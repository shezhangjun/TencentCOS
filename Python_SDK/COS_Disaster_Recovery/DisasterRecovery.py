# -*- coding=utf-8
# author shezhangjun
# Python3.x
import logging
import pandas as pd
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
logger = logging

copied_object_list = []
copied_object_mtime = []
copied_object_versionid_list = []


def _get_bucket_lists(src_region, src_secret_id, src_secret_key, src_bucket, prefix, keymarker, versionidmarker,
                      maxkeys):  # 获取存储桶内的所有对象及其历史版本信息
    client = CosS3Client(CosConfig(Region=src_region, SecretId=src_secret_id, SecretKey=src_secret_key))
    responselist = client.list_objects_versions(
        Bucket=src_bucket,
        Prefix=prefix,
        Delimiter='',
        KeyMarker=keymarker,
        VersionIdMarker=versionidmarker,
        MaxKeys=maxkeys,
        EncodingType=''
    )
    lists = responselist
    return lists


def _copy_object_to_dst_bucket(dst_region, dst_secret_id, dst_secret_key, src_region, dst_bucket, dst_objectkey,
                               src_bucket, src_objectkey, versionId):
    client = CosS3Client(CosConfig(Region=dst_region, SecretId=dst_secret_id, SecretKey=dst_secret_key))
    client.copy(
        Bucket=dst_bucket,
        Key=dst_objectkey,
        CopySource={
            'Bucket': src_bucket,
            'Key': src_objectkey,
            'Region': src_region,
            'VersionId': versionId
        }
    )


def _copied_object(obejectkey):
    data = {'key': copied_object_list}
    df = pd.DataFrame(data)
    is_exist = obejectkey in df['key'].values
    return is_exist


def _recover_main(src_region, src_secret_id, src_secret_key, src_bucket, prefix, keymarker, versionidmarker, maxkeys,
                  dst_region, dst_secret_id, dst_secret_key, dst_bucket):
    i = 0
    while True:
        response = _get_bucket_lists(src_region, src_secret_id, src_secret_key, src_bucket, prefix, keymarker,
                                     versionidmarker, maxkeys)
        if 'Version' in response:  # 标记不是删除标记的记录
            for k in response['Version']:
                i += 1
                versionId = k['VersionId']
                key = k['Key']
                expectedLength = k['Size']
                expectedEtag = k['ETag']
                islatest = k['IsLatest']
                owner = k['Owner']
                getStorageClass = k['StorageClass']
                mtime = k['LastModified']
                print(f'Id:{i}')  # ID
                print(f'versionId:{versionId}')  # 版本ID
                print(f'key:{key}')  # 对象全称
                print(f'islatest:{islatest}')  # 是否最新
                print(f'expectedLength:{expectedLength}')  # 对象大小
                print(f'expectedEtag:{expectedEtag}')  # Etag值
                print(f'Owner:{owner["ID"]}:{owner["DisplayName"]}')  # 资源拥有者ID和名称
                print(f'getStorageClass:{getStorageClass}')  # 对象类型
                print(f'LastModified:{mtime}')
                if islatest == 'true':  # 标记是最新的记录
                    print(f'最新版文件,拷贝key:{key},version:{versionId}')
                    try:
                        _copy_object_to_dst_bucket(dst_region, dst_secret_id, dst_secret_key, src_region, dst_bucket,
                                                   key, src_bucket, key, versionId)
                        copied_object_list.append(key)
                        copied_object_mtime.append(mtime)
                        copied_object_versionid_list.append(versionId)
                    except Exception as e:
                        logger.error(e)
                        pass
                else:
                    if not _copied_object(obejectkey=key):  # 判断此文件是否被拷贝过,如已拷贝则跳过不复制
                        print(f'次新版文件,拷贝key:{key},version:{versionId}')
                        try:
                            _copy_object_to_dst_bucket(dst_region, dst_secret_id, dst_secret_key, src_region, dst_bucket,
                                                       key, src_bucket, key, versionId)
                            copied_object_list.append(key)
                            copied_object_mtime.append(mtime)
                            copied_object_versionid_list.append(versionId)
                        except Exception as e:
                            logger.error(e)
                            pass
                    else:
                        print(f'文件已被拷贝复制，此处跳过')
        if response['IsTruncated'] == 'false':
            break
        keymarker = response['NextKeyMarker']
        versionidmarker = response['NextVersionIdMarker']
    print('--------------------------------------')
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print("已复制的对象列表")
    print(copied_object_list)
    data = {'key': copied_object_list, 'versionid': copied_object_versionid_list, 'LastModified': copied_object_mtime}
    df = pd.DataFrame(data)
    df.to_csv('已复制的对象列表.csv', index=False)


if __name__ == '__main__':
    src_region = ''  # 误删桶文件的地域
    src_secret_id = ''  # 误删桶文件的SecretID
    src_secret_key = ''  # 误删桶文件的SecretID
    src_bucket = ''  # 误删文件的桶名
    dst_region = ''  # 待恢复文件的地域
    dst_secret_id = ''  # 待恢复文件桶的SecretID
    dst_secret_key = ''  # 待恢复文件桶的SecretKey
    dst_bucket = ''  # 待恢复文件的桶名
    prefix = ''  # 设置要恢复的对象前缀
    keymarker = ''  # 默认为空，勿动此参数
    versionidmarker = ''  # 默认为空，勿动此参数
    maxkeys = 1000
    _recover_main(src_region, src_secret_id, src_secret_key, src_bucket, prefix, keymarker, versionidmarker, maxkeys,
                  dst_region, dst_secret_id, dst_secret_key, dst_bucket)
