# -*- coding=utf-8
# author v_yyjwang
# Python2.x - 3.x

import logging
import threading
import json

from Configs import client

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class MyThread(threading.Thread):  # 主线程类，用于从子线程获取返回值

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


def _get_prefix_lists(bucket, prefix, delimiter, marker, maxkeys):  # 去除重复的文件夹名称
    responselist = client.list_objects_versions(
        Bucket=bucket,
        Prefix=prefix,
        Delimiter=delimiter,
        KeyMarker=marker,
        VersionIdMarker='',
        MaxKeys=maxkeys,
        EncodingType=''
    )
    lists = responselist['CommonPrefixes']
    news_lists = []
    for id in lists:
        if id not in news_lists:
            news_lists.append(id)
    return news_lists


def _get_bucket_lists(bucket, prefix, delimiter, marker, maxkeys):  # 获取存储桶内的所有对象及其历史版本信息
    responselist = client.list_objects_versions(
        Bucket=bucket,
        Prefix=prefix,
        Delimiter=delimiter,
        KeyMarker=marker,
        VersionIdMarker='',
        MaxKeys=maxkeys,
        EncodingType=''
    )
    lists = responselist
    return lists


def _get_root_directory_list(bucket, marker, maxkeys):  # 拉取存储桶内根目录下的所有对象及其历史版本信息（不包含虚拟目录）
    responselist = client.list_objects_versions(
        Bucket=bucket,
        Prefix='',
        Delimiter='/',
        KeyMarker=marker,
        VersionIdMarker='',
        MaxKeys=maxkeys,
        EncodingType=''
    )
    lists = responselist
    return lists


def _get_marker(lists):  # 获取下一个Marker
    try:
        nextmarker = lists['NextKeyMarker']
        return nextmarker
    except:
        nextmarker = ''
        return nextmarker


def _get_root_directory_version(lists):  # 判断根目录是否有文件
    try:
        nextmarker = lists['Version']
        return nextmarker
    except:
        nextmarker = ''
        return nextmarker


def _get_marker_list_size(file_count, size, keylists):  # 获取当前Marker里的文件并统计大小
    for i in keylists:
        file_count += 1
        size = size + int(i['Size'])
    size_counts_json = json.dumps({'Size': size, 'Counts': file_count})
    return size_counts_json


def _get_nomarker_list_size(file_count, size, lists):  # 获取最后一个Marker里的文件并统计大小
    keylists = lists['Version']
    for i in keylists:
        file_count += 1
        size = size + int(i['Size'])
    size_counts_json = json.dumps({'Size': size, 'Counts': file_count})
    return size_counts_json


def _calculate_size(size):  # 将Byte转为其他单位
    if size < 1024 * 1024:
        Size = size / 1024
        Size = str(round(Size, 2)) + 'Kb'
    elif 1024 * 1024 < size < 1024 * 1024 * 1024:
        Size = size / 1024 / 1024
        Size = str(round(Size, 2)) + 'Mb'
    elif 1024 * 1024 * 1024 < size < 1024 * 1024 * 1024 * 1024:
        Size = size / 1024 / 1024 / 1024
        Size = str(round(Size, 2)) + 'Gb'
    elif 1024 * 1024 * 1024 * 1024 < size < 1024 * 1024 * 1024 * 1024 * 1024:
        Size = size / 1024 / 1024 / 1024 / 1024
        Size = str(round(Size, 2)) + 'Tb'
    return Size


def _root_size(file_count, size, bucket, marker, maxkeys):  # 计算根目录下的文件大小（不包含虚拟目录）
    a = 1
    lists = _get_root_directory_list(bucket, marker, maxkeys)
    version = _get_root_directory_version(lists)
    if version == '':
        Size = json.dumps({'Prefix': '/', 'Size': 0})
        return (Size)
    else:
        nextmarker = _get_marker(lists)
        if nextmarker == '':
            size_counts_json = json.loads(_get_nomarker_list_size(file_count, size, lists))
            Size = json.dumps({'Prefix': '/', 'Size_counts_json': size_counts_json})
            return (Size)
        else:
            while nextmarker != '':
                a, marker = a + 1, nextmarker
                markerinfo = ' '.join(['当前已列出存储桶根目录下的 [', str(a / 10), '] 万个对象，', '下一个节点是 ', marker])
                print(markerinfo)
                lists = _get_root_directory_list(bucket, marker, maxkeys)
                nextmarker = _get_marker(lists)
                keylists = lists['Version']
                size = _get_marker_list_size(size, keylists)
            if nextmarker == '':
                marker = nextmarker
                lists = _get_root_directory_list(bucket, marker, maxkeys)
                Size = _get_nomarker_list_size(file_count, size, lists)
                Size = json.dumps({'Prefix': '/', 'Size': Size})
                return (Size)


def _prefix_size(file_count, size, bucket, prefix, marker, maxkeys):  # 计算虚拟目录的文件大小（不包含存储桶根目录）
    a = 1
    delimiter = ''
    lists = _get_bucket_lists(bucket, prefix, delimiter, marker, maxkeys)
    nextmarker = _get_marker(lists)
    if nextmarker == '':
        list_size_count_json = json.loads(_get_nomarker_list_size(file_count, size, lists))
        Size = json.dumps({'Prefix': prefix, 'Size': list_size_count_json['Size'], 'Counts': list_size_count_json['Counts']})
        return (Size)
    else:
        while nextmarker != '':
            a, marker = a + 1, nextmarker
            markerinfo = ' '.join(['当前已列出 ' + prefix + ' 目录的 [', str(a / 10), '] 万个对象，', '下一个节点是 ', marker])
            print(markerinfo)
            lists = _get_bucket_lists(bucket, prefix, delimiter, marker, maxkeys)
            nextmarker = _get_marker(lists)
            keylists = lists['Version']
            list_size_count_json = json.loads(_get_marker_list_size(file_count, size, keylists))
            size = int(list_size_count_json['Size'])
            file_count = int(list_size_count_json['Counts'])
        if nextmarker == '':
            marker = nextmarker
            lists = _get_bucket_lists(bucket, prefix, delimiter, marker, maxkeys)
            prefix_size = json.loads(_get_nomarker_list_size(file_count, size, lists))['Size']
            prefix_counts = json.loads(_get_nomarker_list_size(file_count, size, lists))['Counts']
            Size = json.dumps({'Prefix': prefix, 'Size': prefix_size, 'Counts':prefix_counts})
            return (Size)


def _get_list_start(bucket, marker, CommonPrefixes, maxkeys, files_exits):  # 获取当前存储桶的所有文件大小主函数（如果存储桶开启了多版本，也会一并统计）
    bucket_count = 0
    bucket_size = 0
    size = 0
    file_count = 0
    threads = []
    directory_size_dict = []
    if files_exits == 1:
        directory_size = json.dumps({'Prefix': '/', 'Size': 0, 'Counts': 0})
        directory_size_dict.append(directory_size)
        for prefix in CommonPrefixes:
            CommonPrefixes = prefix['Prefix']
            t = MyThread(_prefix_size, (file_count, size, bucket, CommonPrefixes, marker, maxkeys), )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
            directory_size_dict.append(t.get_result())
        for directory in directory_size_dict:
            directory = json.loads(directory)
            prefix = directory['Prefix']
            size = directory['Size']
            count = directory['Counts']
            bucket_count += count
            bucket_size += size
            size_calculate = _calculate_size(size)
            prefix_Size = json.dumps({'Prefix': prefix, 'Size': size_calculate, 'Counts': count})
            print(prefix_Size)
        size_calculate = _calculate_size(bucket_size)
        bucket_Size = json.dumps({'Bucket': bucket, 'Size': size_calculate, 'Counts': bucket_count})
        print(bucket_Size)
        return 'Success list'
    elif files_exits == 2:
        print(json.dumps({'Bucket': bucket, 'Size': 0, 'Counts': 0}))
        return 'Success list'
    elif files_exits == 3:
        root_directory_size = _root_size(file_count, size, bucket, marker, maxkeys)
        directory_size = json.dumps({'Prefix': '/', 'Size': int(json.loads(root_directory_size)['Size_counts_json']['Size']), 'Counts': int(json.loads(root_directory_size)['Size_counts_json']['Counts'])})
        directory_size_dict.append(directory_size)
        for prefix in CommonPrefixes:
            CommonPrefixes = prefix['Prefix']
            t = MyThread(_prefix_size, (file_count, size, bucket, CommonPrefixes, marker, maxkeys), )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
            directory_size_dict.append(t.get_result())
        for directory in directory_size_dict:
            directory = json.loads(directory)
            prefix = directory['Prefix']
            size = directory['Size']
            count = directory['Counts']
            bucket_count += count
            bucket_size += size
            size_calculate = _calculate_size(size)
            prefix_Size = json.dumps({'Prefix': prefix, 'Size': size_calculate, 'Counts': count})
            print(prefix_Size)
        size_calculate = _calculate_size(bucket_size)
        bucket_Size = json.dumps({'Bucket': bucket, 'Size': size_calculate, 'Counts': bucket_count})
        print(bucket_Size)
        return 'Success list'
    else:
        root_directory_size = _root_size(file_count, size, bucket, marker, maxkeys)
        file_count = int(json.loads(root_directory_size)['Size_counts_json']['Counts'])
        directory_size = _calculate_size(int(json.loads(root_directory_size)['Size_counts_json']['Size']))
        print(json.dumps({'Bucket': bucket, 'Size': directory_size, 'Counts': file_count}))
        return 'Success list'

        
if __name__ == '__main__':
    bucket = ''  # 传入存储桶名
    prefix = ''  # 指定需要统计大小的目录；留空代表整个存储桶
    marker = ''  # 此处请勿修改
    delimiter = '/'  # 此处请勿修改
    maxkeys = 1000

    lists = _get_root_directory_list(bucket, marker, maxkeys)
    version = _get_root_directory_version(lists)
    if version == '':  
        #当根目录下没有文件，但可能有子文件夹时
        try:
            #当根目录下没有文件，只有子文件夹时
            files_exits = 1
            CommonPrefixes = _get_prefix_lists(bucket, prefix, delimiter, marker, maxkeys)
            resp = _get_list_start(bucket, marker, CommonPrefixes, maxkeys, files_exits)
            print(resp)
        except:
            #当根目录下没有文件，也没有子文件夹时
            files_exits = 2
            CommonPrefixes = ''
            resp = _get_list_start(bucket, marker, CommonPrefixes, maxkeys, files_exits)
            print(resp)
    else:
        #当根目录下有文件，同时也有子文件夹时
        try:
            files_exits = 3
            CommonPrefixes = _get_prefix_lists(bucket, prefix, delimiter, marker, maxkeys)
            resp = _get_list_start(bucket, marker, CommonPrefixes, maxkeys, files_exits)
            print(resp)
        except:
            #当根目录下有文件，但没有子文件夹时
            files_exits = 4
            CommonPrefixes = ''
            resp = _get_list_start(bucket, marker, CommonPrefixes, maxkeys, files_exits)
            print(resp)