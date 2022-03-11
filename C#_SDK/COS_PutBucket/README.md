# TencentCOS
腾讯云对象存储 .NET(C#) SDK

## 使用.NET(C#) SDK 创建存储桶

### Windows 环境安装

* 下载和安装方式参考腾讯云对象存储SDK-[.NET(C#)](https://cloud.tencent.com/document/product/436/32819)
* Windows环境下安装 `Visual Studio 2019/2022`
* 如果您的Visual Studio没有安装NuGet，请先安装[NuGet](http://docs.nuget.org/docs/start-here/installing-nuget?spm=a2c4g.11186623.0.0.556e1cd5Nm58dC)。
* 在Visual Studio中新建或者打开已有的项目，选择工具 > NuGet程序包管理器 > 管理解决方案的NuGet程序包。
* 搜索Tencent.QCloud.Cos.Sdk，在结果中找到Tencent.QCloud.Cos.Sdk（`适用于.NET Framework`）选择最新版本，单击安装。

### Windwos 环境 .NET(C#) SDK 创建存储桶 示例

![image](https://cos.iclay.cn/Page/GitHub_Page_Bed/C%23-PutBucket.png)

### Windows 环境 .NET(C#) SDK 使用方法

* 打开 `PutBucket.sln` 项目解决方案
* 替换下方码块中的`COS_REGION|SECRET_ID|SECRET_KEY|BucketName`
* 编译调试

```
/// 初始化密钥信息
PutBucketModel()
        {
            CosXmlConfig config = new CosXmlConfig.Builder()
              .SetRegion("COS_REGION") // 设置默认的地域, COS 地域的简称请参照 https://cloud.tencent.com/document/product/436/6224 
              .Build();

            string secretId = "SECRET_ID";   // 云 API 密钥 SecretId, 获取 API 密钥请参照 https://console.cloud.tencent.com/cam/capi
            string secretKey = "SECRET_KEY"; // 云 API 密钥 SecretKey, 获取 API 密钥请参照 https://console.cloud.tencent.com/cam/capi
            long durationSecond = 600;          //每次请求签名有效时长，单位为秒
            QCloudCredentialProvider qCloudCredentialProvider = new DefaultQCloudCredentialProvider(secretId,
              secretKey, durationSecond);

            this.cosXml = new CosXmlServer(config, qCloudCredentialProvider);
        }

/// 创建存储桶
public void PutBucket()
        {
            //.cssg-snippet-body-start:[put-bucket]
            try
            {
                // 存储桶名称，此处填入格式必须为 BucketName-APPID, 其中 APPID 获取参考 https://console.cloud.tencent.com/developer
                string bucket = "BucketName";
                PutBucketRequest request = new PutBucketRequest(bucket);
                //执行请求
                PutBucketResult result = cosXml.PutBucket(request);
                //请求成功
                Console.WriteLine(result.GetResultInfo());
            }
            catch (COSXML.CosException.CosClientException clientEx)
            {
                //请求失败
                Console.WriteLine("CosClientException: " + clientEx);
            }
            catch (COSXML.CosException.CosServerException serverEx)
            {
                //请求失败
                Console.WriteLine("CosServerException: " + serverEx.GetInfo());
            }

            //.cssg-snippet-body-end
        }
```