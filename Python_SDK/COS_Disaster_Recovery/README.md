# TencentCOS
腾讯云对象存储SDK-Python

## 使用Python SDK 结合COS多版本功能快速批量恢复数据
* 恢复原理参考文档说明 https://cloud.tencent.com/developer/beta/article/1791791

### 使用方法

* 推荐使用Python3.x
* 安装[腾讯云对象存储SDK-Python](https://cloud.tencent.com/document/product/436/12269)  `pip install -U cos-python-sdk-v5` 
* 安装pandas库  `pip install -U pandas`
* git clone https://github.com/shezhangjun/TencentCOS.git
* 在[DisasterRecovery.py](https://github.com/shezhangjun/TencentCOS/blob/master/Python_SDK/COS_Disaster_Recovery/DisasterRecovery.py) 文件中最下方配置存储桶名以及密钥信息


### 效果展示
![image](https://cos.iclay.cn/Page/GitHub_Page_Bed/Recovery-COS-Python.png)
