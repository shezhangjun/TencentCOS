﻿using COSXML.Model.Bucket;
using COSXML.Auth;
using COSXML;

namespace COSSnippet
{
    public class PutBucketModel
    {

        private CosXml cosXml;

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
                string bucket = "examplebucket-1250000000";
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

        // .cssg-methods-pragma

        static void Main(string[] args)
        {
            PutBucketModel m = new PutBucketModel();

            /// 创建存储桶
            m.PutBucket();
            // .cssg-methods-pragma
        }
    }
}