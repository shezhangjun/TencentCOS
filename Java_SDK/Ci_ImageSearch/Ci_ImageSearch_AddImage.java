import com.qcloud.cos.Headers;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.auth.COSSigner;
import com.qcloud.cos.http.HttpMethodName;
import com.squareup.okhttp.*;

import java.io.IOException;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;


public class Ci_ImageSearch_AddImage {
    public static void main(String[] args) {
        // 1 初始化用户身份信息（secretId, secretKey）。
        // SECRETID和SECRETKEY请登录访问管理控制台进行查看和管理
        String secretId = "";
        String secretKey = "";
        COSCredentials cred = new BasicCOSCredentials(secretId, secretKey);
        // 2 设置 bucket 的地域, COS 地域的简称请参照 https://cloud.tencent.com/document/product/436/6224
        String region = "";
        // 4 bucket名需包含appid
        String Bucket = "";
        // 5 存储在存储桶内图片的对象键，图片大小不能超过2M
        String key = "";
        // 6 图片添加至图库中定义的物品 ID
        String entityid = "";
        // 6 图片添加至图库中自定义的内容，最多支持4096个字符，查询时原样带回
        String customcontent = "";
        // 7 图片添加至图库中，图片自定义标签，最多不超过10个，json 字符串，格式为 key:value 对
        String tags = "{\"key1\":\"val1\",\"key2\":\"val2\"}";

        //以下为生成签名部分
        COSSigner signer = new COSSigner();
        Date expirationDate = new Date(System.currentTimeMillis() + 30L * 60L * 1000L);
        Map<String, String> params = new HashMap<String, String>();
        Map<String, String> headers = new HashMap<String, String>();
        headers.put(Headers.HOST, Bucket +  ".ci." + region + ".myqcloud.com");
        HttpMethodName method = HttpMethodName.POST; //请求方法
        String sign = signer.buildAuthorizationStr(method, key, headers, params, cred, expirationDate,true);
        //以上为生成签名部分

        OkHttpClient client = new OkHttpClient();
        MediaType mediaType = MediaType.parse("application/xml");
        RequestBody body = RequestBody.create(mediaType, "<Request>\r\n    <EntityId>" + entityid + "</EntityId>\r\n    <CustomContent>" + customcontent + "</CustomContent>\r\n    <Tags>" + tags + "</Tags>\r\n</Request>");
        Request request = new Request.Builder()
                .url("https://" + Bucket +  ".cos." + region + ".myqcloud.com" + key + "?ci-process=ImageSearch&action=AddImage")
                .method("POST", body)
                .addHeader("Authorization", sign)
                .addHeader("Content-Type", "application/xml")
                .build();
        try {
            Response response = client.newCall(request).execute();
            System.out.println("<" + response.code() + ">" + "\r\n" + response.body().string() + "\r\n" + response.headers()); //如果返回400，请检查参数部分是否传入有误，或者该图片已添加至图片库
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}