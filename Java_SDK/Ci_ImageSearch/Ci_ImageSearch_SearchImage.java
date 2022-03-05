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

public class Ci_ImageSearch_SearchImage {
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
        // 6 相似度，返回的分数中，只有超过 MatchThreshold 值的结果才会返回;默认为0
        long matchthreshold = 0;
        // 7 起始序号，默认值为0
        long offset = 0;
        // 8 返回数量，默认值为10，最大值为100
        long limit = 10;
        // 9 针对入库时提交的 Tags 信息进行条件过滤。支持>、>=、<、<=、=、!=，多个条件之间支持 AND 和 OR 进行连接
        String filter = "";

        //以下为生成签名部分
        COSSigner signer = new COSSigner();
        Date expirationDate = new Date(System.currentTimeMillis() + 30L * 60L * 1000L);
        Map<String, String> params = new HashMap<String, String>();
        Map<String, String> headers = new HashMap<String, String>();
        headers.put(Headers.HOST, Bucket +  ".ci." + region + ".myqcloud.com");
        HttpMethodName method = HttpMethodName.GET; //请求方法
        String sign = signer.buildAuthorizationStr(method, key, headers, params, cred, expirationDate,true);
        //以上为生成签名部分

        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url("https://" + Bucket +  ".cos." + region + ".myqcloud.com" + key + "?ci-process=ImageSearch&action=SearchImage&MatchThreshold=" + matchthreshold + "&Offset=" + offset + "&Limit=" + limit + "&Filter=" + filter )
                .method("GET",null)
                .addHeader("Authorization", sign)
                .addHeader("Content-Type", "application/xml")
                .build();
        try {
            Response response = client.newCall(request).execute();
            System.out.println("<" + response.code() + ">" + "\r\n" + response.body().string());  //如果返回400，请检查参数部分是否传入有误，或者该图片是否有添加到图库中
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
