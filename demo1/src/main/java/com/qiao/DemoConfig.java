package com.qiao;

import com.openai.client.OpenAIClient;//AI 客户端接口
import com.openai.client.okhttp.OpenAIOkHttpClient;//具体的 AI 客户端实现（用网络框架 OkHttp 实现聊天）
//配置类
public final class DemoConfig {
    public static final String MODEL = "THUDM/GLM-Z1-9B-0414";
    private static final String DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1";

    private DemoConfig() {}

//    public static OpenAIClient client() {
//        String apiKey = System.getenv("OPENAI_API_KEY");
//        if (apiKey == null || apiKey.isBlank()) {
//            throw new IllegalStateException("OPENAI_API_KEY is not set");
//        }
//
//        String baseUrl = System.getenv().getOrDefault("OPENAI_BASE_URL", DEFAULT_BASE_URL);
//
//        return OpenAIOkHttpClient.builder()
//                .apiKey(apiKey)
//                .baseUrl(baseUrl)
//                .build();
//    }
    public static OpenAIClient client() {
        return OpenAIOkHttpClient.builder()// 创建AI客户端
            .apiKey(System.getenv("OPENAI_API_KEY"))//给客户端设置 API 密钥，读取电脑的环境变量
            .baseUrl(System.getenv().getOrDefault("OPENAI_BASE_URL", DEFAULT_BASE_URL))
                // 设置 AI 服务器地址，读取环境变量，如果没读到，就用默认值
            .build();
    }
}
