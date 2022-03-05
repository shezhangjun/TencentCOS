package com.cos.demo;

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


public class Ci_TriggerWorkflow {
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
        // 5 需要触发的工作流 ID 参照 https://console.cloud.tencent.com/cos/workflow/list
        String workflowId = "";
        // 6 使用triggerworkflow生成签名，请勿修改！
        String signkey = "/triggerworkflow";
        // 7 需要进行工作流处理的对象名称
        String objectkey = "";
        // 8 生成此次请求用的HOST
        String host = Bucket +  ".ci." + region + ".myqcloud.com";

        //以下为生成签名部分
        COSSigner signer = new COSSigner();
        Date expirationDate = new Date(System.currentTimeMillis() + 30L * 60L * 1000L);
        Map<String, String> params = new HashMap<String, String>();
        Map<String, String> headers = new HashMap<String, String>();
        headers.put(Headers.HOST, host);
        HttpMethodName method = HttpMethodName.POST; //请求方法
        String sign = signer.buildAuthorizationStr(method, signkey, headers, params, cred, expirationDate,true);
        //以上为生成签名部分

        OkHttpClient client = new OkHttpClient();
        MediaType mediaType = MediaType.parse("application/xml");
        RequestBody body = RequestBody.create(mediaType, "");
        Request request = new Request.Builder()
                .url("https://" + host + signkey +  "?workflowId=" + workflowId + "&object=" + objectkey)
                .method("POST", body)
                .addHeader("Authorization", sign)
                .addHeader("Content-Type", "application/xml")
                .build();
        try {
            Response response = client.newCall(request).execute();
            System.out.println("<" + response.code() + ">" + "\r\n" + response.body().string() + "\r\n" + response.headers());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}