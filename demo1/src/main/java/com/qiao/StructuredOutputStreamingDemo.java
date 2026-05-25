package com.qiao;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.openai.helpers.ChatCompletionAccumulator;
import com.openai.models.chat.completions.ChatCompletionChunk;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.StructuredChatCompletionCreateParams;
import com.qiao.model.Candidate;
import com.openai.client.OpenAIClient;
import com.openai.core.http.StreamResponse;
import com.openai.helpers.ResponseAccumulator;
import com.openai.models.responses.ResponseCreateParams;
import com.openai.models.responses.ResponseStreamEvent;
import com.openai.models.responses.StructuredResponseCreateParams;


public final class StructuredOutputStreamingDemo {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private StructuredOutputStreamingDemo() {}

    public static void main(String[] args) {
        OpenAIClient client = DemoConfig.client();

        String resumeText = """
                Candidate: Li Lei
                Mail: lilei@example.com
                Profile: 6 years in backend development.
                Tech stack: Java, Spring Cloud, PostgreSQL, Redis, Elasticsearch
                """;

//        StructuredResponseCreateParams<Candidate> createParams = ResponseCreateParams.builder()
//                .model(DemoConfig.MODEL)
//                .input("Extract candidate name, email, and skills from this resume text.\n\n" + resumeText)
//                .text(Candidate.class)
//                .build();
//
//        ResponseAccumulator accumulator = ResponseAccumulator.create();
//
//        try (StreamResponse<ResponseStreamEvent> streamResponse =
//                     client.responses().createStreaming(createParams)) {
//            streamResponse.stream()
//                    .peek(accumulator::accumulate)
//                    .flatMap(event -> event.outputTextDelta().stream())
//                    .forEach(textEvent -> System.out.print(textEvent.delta()));
//            System.out.println();
//        }
//
//        Candidate candidate = accumulator.response(Candidate.class).output().stream()
//                .flatMap(item -> item.message().stream())
//                .flatMap(message -> message.content().stream())
//                .flatMap(content -> content.outputText().stream())
//                .findFirst()
//                .orElse(null);
//
//        System.out.println("\n[structured_result]");
//        System.out.println(candidate == null ? "No structured candidate returned." : candidate);
        // 核心：强制模型返回 纯JSON格式，无任何多余文字
        String prompt = """
                从简历中提取姓名(name)和邮箱(email)，仅返回标准JSON，不要任何解释、文字、标点：
                {"name":"","email":""}
                简历内容：
                %s
                """.formatted(resumeText);

        // 构建普通流式请求（弃用所有结构化API）
        ChatCompletionCreateParams createParams = ChatCompletionCreateParams.builder()
                .model(DemoConfig.MODEL)
                .addUserMessage(prompt)
                .build();

        // 手动拼接完整响应（替代累加器，解决id报错）
        StringBuilder fullJson = new StringBuilder();

        System.out.println("=== 流式结构化输出 ===");
        // 流式调用
        try (StreamResponse<ChatCompletionChunk> streamResponse = client.chat().completions().createStreaming(createParams)) {
            streamResponse.stream()
                    .flatMap(chunk -> chunk.choices().stream())
                    // 修复Optional：提取文本，空值返回null
                    .map(choice -> choice.delta().content().orElse(null))
                    .filter(content -> content != null)
                    // 实时打印 + 拼接完整JSON
                    .forEach(content -> {
                        System.out.print(content);
                        fullJson.append(content);
                    });
        }

        // 手动解析JSON为 Candidate 对象
        System.out.println("\n\n=== 结构化解析结果 ===");
        try {
            Candidate candidate = OBJECT_MAPPER.readValue(fullJson.toString(), Candidate.class);
            System.out.println("解析成功：" + candidate);
        } catch (Exception e) {
            System.out.println("解析失败：" + e.getMessage());
            System.out.println("原始JSON：" + fullJson);
        }
    }
}
