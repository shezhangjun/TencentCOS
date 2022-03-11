using COSXML.Model.Object;
using COSXML.Auth;
using COSXML;

namespace COSSnippet
{
    public class PutObjectFromStream
    {

        private CosXml cosXml;

        PutObjectFromStream()
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

        /// 文件流上传, 从 5.4.24 版本开始支持
        public void PutObjectStream()
        {
            try
            {
                // 存储桶名称，此处填入格式必须为 bucketname-APPID, 其中 APPID 获取参考 https://console.cloud.tencent.com/developer
                string bucket = "BucketName";
                string key = "/ExampleObject"; //对象键
                string srcPath = @"Temp_Source_File";//本地文件绝对路径
                FileStream fileStream = new FileStream(srcPath, FileMode.Open, FileAccess.Read);
                // 组装上传请求，其中 offset sendLength 为可选参数
                long offset = 0L;
                long sendLength = fileStream.Length;
                PutObjectRequest request = new PutObjectRequest(bucket, key, fileStream, offset, sendLength);
                //设置进度回调
                request.SetCosProgressCallback(delegate (long completed, long total)
                {
                    Console.WriteLine(String.Format("progress = {0:##.##}%", completed * 100.0 / total));
                });
                //执行请求
                PutObjectResult result = cosXml.PutObject(request);
                //关闭文件流
                fileStream.Close();
                //对象的 eTag
                string eTag = result.eTag;
                //对象的 crc64ecma 校验值
                string crc64ecma = result.crc64ecma;
                //打印请求结果
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
        }

        static void Main(string[] args)
        {
            PutObjectFromStream m = new PutObjectFromStream();
            /// 从文件流上传对象
            m.PutObjectStream();
        }
    }
}