package com.qiao;

import com.openai.client.OpenAIClient;//AI 聊天客户端
import com.openai.models.chat.completions.ChatCompletion;//接收 AI 返回的完整回答
import com.openai.models.chat.completions.ChatCompletionCreateParams;//聊天请求参数
import com.openai.models.responses.Response;
import com.openai.models.responses.ResponseCreateParams;

//调用 AI 聊天的极简演示，非流式
public final class BasicChatDemo {
//    private BasicChatDemo() {}
//
//    public static void main(String[] args) {
//        OpenAIClient client = DemoConfig.client();
//
//        ResponseCreateParams params = ResponseCreateParams.builder()
//                .model(DemoConfig.MODEL)
//                .input("请用三句话介绍 Java 17 最值得关注的改进。")
//                .build();
//
//        Response response = client.responses().create(params);
//        System.out.println(response.output());
//    }
public static void main(String[] args) {
    OpenAIClient client = DemoConfig.client();//从配置类里，拿到一个已经配置好的 AI 客户端

    ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()//组装「发给 AI 的请求参数」
            .model(DemoConfig.MODEL)//设置 AI 模型
            .addSystemMessage("你是一个简洁的技术助手。")//系统提示词
            .addUserMessage("请用三句话介绍 Java 17 的亮点。")//用户的问题
            .build();

    ChatCompletion completion = client.chat().completions().create(params);//把打包好的请求，发送给 AI 服务器

    completion.choices()//AI 回复的选项列表（AI 一般只返回 1 个答案）
            .stream()//流式处理
            .flatMap(choice -> choice.message().content().stream())//展开嵌套内容，获取 AI 回答的纯文本内容
            .forEach(System.out::println);//一行行打印在屏幕上
    }
}
