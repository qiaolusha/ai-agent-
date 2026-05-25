package com.qiao;

import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.StructuredChatCompletionCreateParams;
import com.qiao.model.Candidate;
import com.openai.client.OpenAIClient;
import com.openai.models.responses.ResponseCreateParams;
import com.openai.models.responses.StructuredResponseCreateParams;
//读取简历文本
//自动提取姓名、邮箱
//直接返回 Java 对象（Candidate），不是杂乱文字
//程序可以直接使用这个对象，不用手动解析文本
public final class StructuredOutputDemo {
//    private StructuredOutputDemo() {}
//
//    public static void main(String[] args) {
//        OpenAIClient client = DemoConfig.client();
//
//        String resumeText = """
//                姓名: 王晓明
//                邮箱: xiaoming.wang@example.com
//                工作经历: 5年 Java 后端开发，熟悉微服务与高并发系统。
//                技能: Java, Spring Boot, MySQL, Redis, Kafka, Docker
//                """;
//
//        StructuredResponseCreateParams<Candidate> params = ResponseCreateParams.builder()
//                .model(DemoConfig.MODEL)
//                .input("从下面简历文本提取候选人信息，并严格按 schema 返回。\n\n" + resumeText)
//                .text(Candidate.class)
//                .build();
//
//        client.responses().create(params).output().stream()
//                .flatMap(item -> item.message().stream())
//                .flatMap(message -> message.content().stream())
//                .flatMap(content -> content.outputText().stream())
//                .findFirst()
//                .ifPresentOrElse(
//                        candidate -> System.out.println("Structured candidate: " + candidate),
//                        () -> System.out.println("No structured candidate returned."));
//    }
public static void main(String[] args) {
    OpenAIClient client = DemoConfig.client();
    // 构建【结构化输出请求参数】
    // 强制 AI 返回 Candidate 格式的数据
    StructuredChatCompletionCreateParams<Candidate> params = ChatCompletionCreateParams.builder()
            .model(DemoConfig.MODEL)
            .addSystemMessage("你是简历信息抽取助手，只返回符合 schema 的结果。")
            .addUserMessage("""
                        姓名: 王晓明
                        邮箱: xiaoming.wang@example.com
                        技能: Java, Spring Boot, Redis, Kafka
                        """)
            // 强制 AI 返回的结果，必须匹配 Candidate 类
            .responseFormat(Candidate.class)
            .build();

    client.chat().completions().create(params).choices().stream()
            .flatMap(choice -> choice.message().content().stream())
            .forEach(candidate -> System.out.println("structured=" + candidate));
}
}
