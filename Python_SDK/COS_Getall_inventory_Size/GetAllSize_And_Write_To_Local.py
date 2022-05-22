# -*- coding: utf8 -*-
import gc
import os
import json
import logging
import pandas as pd
from io import BytesIO
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class Data_Frames:
    a = None


def main_handler():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)

    global client, bucket, mainfest_key, Compression, Headers, Chunksize
    bucket = ''  # 清单文件所在的存储桶
    region = ''  # 清单文件所在存储桶的地域
    secretid = ''  # 有权限读写清单文件所在存储桶的账号密钥ID
    secretkey = ''  # 有权限读写清单文件所在存储桶的账号密钥Key
    mainfest_key = ''  # 清单报告Mainfest.json文件存储路径，示例 destination-prefix/appid/source-bucket/config-ID/YYYYMMDD/manifest.json

    config = CosConfig(Region=region, SecretId=secretid, SecretKey=secretkey)
    client = CosS3Client(config)

    gc.enable()
    Compression = 'gzip'
    mainfest_json = json.load(_get_object(mainfest_key)['Body'].get_raw_stream())
    Headers = mainfest_json['fileSchema'].split(', ')
    Chunksize = 10 ** 6
    _start_calculate(mainfest_json['files'])
    getattr(Data_Frames, 'Directory_Calculate_Size_Results_Dataframes').to_csv('统计结果-按文件夹和存储类型维度.csv', index=None)
    getattr(Data_Frames, 'FileType_Calculate_Size_Results_Dataframes').to_csv('统计结果-按文件夹和文件类型维度.csv', index=None)
    print('* 统计文件已在当前脚本运行目录下生成')
    return 'Success!'


def _start_calculate(data_list):
    directory_size_calculate_single_results = []
    filetype_size_calculate_single_results = []
    for k in data_list:
        _single_data_calculate_size(pd.read_csv(BytesIO(_get_object(k['key'])['Body'].get_raw_stream().data), encoding='utf8', compression=Compression, names=Headers, chunksize=Chunksize, low_memory=False))
        directory_size_calculate_single_results.append(getattr(Data_Frames, 'Directory_Single_Calculate_Size_Dataframes'))
        filetype_size_calculate_single_results.append(getattr(Data_Frames, 'FileType_Single_Calculate_Size_Dataframes'))
    df_directory = pd.concat(directory_size_calculate_single_results, axis=0, ignore_index=True)
    df_directory = df_directory.groupby(['StorageClass', 'Key'], as_index=False).sum().sort_values('Size', ascending=False)
    df_filetype = pd.concat(filetype_size_calculate_single_results, axis=0, ignore_index=True)
    df_filetype = df_filetype.groupby(['StorageClass', 'Key', 'FileType'], as_index=False).sum().sort_values('Size', ascending=False)

    setattr(Data_Frames, 'Directory_Calculate_Size_Results_Dataframes', df_directory)
    setattr(Data_Frames, 'FileType_Calculate_Size_Results_Dataframes', df_filetype)
    gc.collect()
    return None


def _single_data_calculate_size(data):
    pd.set_option('mode.chained_assignment', None)
    chunks_directory = []
    chunks_type = []
    loop = True
    while loop:
        try:
            print('* ' + str(10 ** 6) + ' bytes data has been read')
            chunk = data.get_chunk(Chunksize)

            chunk_directory = chunk[['Key', 'StorageClass', 'Size']]
            chunk_directory['Key'].replace(['^((?!/).)*$'], 'Root directory', regex=True, inplace=True)
            for t in range(10): chunk_directory['Key'].replace(['(?:/[^/]*$)'], '', regex=True, inplace=True)
            chunk_directory['Key'].replace(['/\w+(\S+).*'], '', regex=True, inplace=True)
            chunk_directory = chunk_directory.groupby(['StorageClass', 'Key'], as_index=False).agg(Size=('Size', 'sum'), Counts=('Key', 'count'))
            chunks_directory.append(chunk_directory)

            chunk_type = chunk[['Key', 'StorageClass', 'Size']]
            chunk_type['FileType'] = chunk_type['Key']
            chunk_type['Key'].replace(['^((?!/).)*$'], 'Root directory', regex=True, inplace=True)
            for t in range(10): chunk_type['Key'].replace(['(?:/[^/]*$)'], '', regex=True, inplace=True)
            chunk_type['Key'].replace(['/\w+(\S+).*'], '', regex=True, inplace=True)
            chunk_type['FileType'].replace(['^((?![.]).)*$'], 'None', regex=True, inplace=True)
            chunk_type['FileType'].replace(['(?:.*[.])'], '', regex=True, inplace=True)
            chunk_type = chunk_type.groupby(['StorageClass', 'Key', 'FileType'], as_index=False).agg(Size=('Size', 'sum'), Counts=('FileType', 'count'))
            chunks_type.append(chunk_type)
        except StopIteration:
            loop = False
    directory_single_calculate_size_dataframe = pd.concat(chunks_directory, axis=0, ignore_index=True)
    directory_single_calculate_size_dataframes = directory_single_calculate_size_dataframe.groupby(['StorageClass', 'Key'], as_index=False).sum().sort_values('Size', ascending=False)
    filetype_single_calculate_size_dataframe = pd.concat(chunks_type, axis=0, ignore_index=True)
    filetype_single_calculate_size_dataframes = filetype_single_calculate_size_dataframe.groupby(['StorageClass', 'Key', 'FileType'], as_index=False).sum().sort_values('Size', ascending=False)

    setattr(Data_Frames, 'Directory_Single_Calculate_Size_Dataframes', directory_single_calculate_size_dataframes)
    setattr(Data_Frames, 'FileType_Single_Calculate_Size_Dataframes', filetype_single_calculate_size_dataframes)
    gc.collect()
    return None


def _get_object(key):
    response = client.get_object(
        Bucket=bucket,
        Key=key
    )
    return response



if __name__ == '__main__':
    main_handler()
