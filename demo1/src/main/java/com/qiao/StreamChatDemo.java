package com.qiao;

import com.openai.client.OpenAIClient;
import com.openai.core.http.StreamResponse;
import com.openai.helpers.ResponseAccumulator;
import com.openai.models.responses.ResponseCreateParams;
import com.openai.models.responses.ResponseStreamEvent;
import com.openai.helpers.ChatCompletionAccumulator;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionChunk;//AI 回答的小碎片（流式输出的每一个字 / 词）
import com.openai.models.chat.completions.ChatCompletionCreateParams;//聊天请求参数（装问题、模型的盒子）
public final class StreamChatDemo {
    private StreamChatDemo() {}
// AI 流式聊天程序 流式
    public static void main(String[] args) {
        OpenAIClient client = DemoConfig.client();

//        ResponseCreateParams createParams = ResponseCreateParams.builder()
//                .model(DemoConfig.MODEL)
//                .input("请给我一个 30 分钟准备 Java 面试的行动清单，按 1-5 编号。")
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
//        System.out.println("\n[full_response]");
//        System.out.println(accumulator.response().output());
        ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()
                .model(DemoConfig.MODEL)
                .addUserMessage("给我一个 30 分钟 Java 面试冲刺清单。")
                .build();

//        ChatCompletionAccumulator acc = ChatCompletionAccumulator.create();
        // 手动拼接完整响应（替代累加器，解决id缺失报错）
        StringBuilder fullText = new StringBuilder();
//try(...)：Java 安全语法，自动关闭网络连接
        try (StreamResponse<ChatCompletionChunk> stream = client.chat().completions().createStreaming(params)) {
            stream.stream()
                    // 遍历分片
                    .flatMap(chunk -> chunk.choices().stream())
                    // 核心修复：从 Optional 中提取文本，为空则返回 null
                    .map(choice -> choice.delta().content().orElse(null))
                    // 过滤 null 值，不打印空内容
                    .filter(content -> content != null)
                    // 纯文本打印 + 拼接
                    .forEach(content -> {
                        System.out.print(content);
                        fullText.append(content);
                    });
        }

        System.out.println("\n\n=== 完整响应结果 ===");
        System.out.println(fullText);
    }
}