package com.qiao;

import com.openai.client.OpenAIClient;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.responses.Response;
import com.openai.models.responses.ResponseCreateParams;

public final class UsageAndCachingDemo {
    private UsageAndCachingDemo() {}

    public static void main(String[] args) {
        OpenAIClient client = DemoConfig.client();

        String sharedInstructions = "你是一个严谨的技术面试官。先给出3条结论，再给出每条结论的一句话解释。";
        String staticPrefix = "候选人背景: 5年 Java 后端经验, 做过支付和交易系统, 熟悉 Spring Boot 与 Redis。";

        runOnce(client, sharedInstructions, staticPrefix, "变化内容A: 最近项目中引入了 Kafka。", "Run-1");
        runOnce(client, sharedInstructions, staticPrefix, "变化内容B: 最近项目中引入了 Elasticsearch。", "Run-2");
    }

    private static void runOnce(
            OpenAIClient client,
            String instructions,
            String prefix,
            String dynamicTail,
            String label
    ) {
//        ResponseCreateParams params = ResponseCreateParams.builder()
//                .model(DemoConfig.MODEL)
//                .instructions(instructions)
//                .input(prefix + "\n" + dynamicTail + "\n请判断这位候选人的系统设计能力。")
//                .build();
//
//        long start = System.nanoTime();
//        Response response = client.responses().create(params);
//        long latencyMs = (System.nanoTime() - start) / 1_000_000;

//        System.out.println("\n==== " + label + " ====");
//        System.out.println("latencyMs=" + latencyMs);
//        System.out.println("output=" + response.output());
//        System.out.println("usage=" + response.usage().map(Object::toString).orElse("null"));
        String userPrompt = prefix + "\n" + dynamicTail + "\n请判断这位候选人的系统设计能力。";

        ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()
                .model(DemoConfig.MODEL)
                .addSystemMessage(instructions)
                .addUserMessage(userPrompt)
                .build();

        long start = System.nanoTime();
        ChatCompletion completion = client.chat().completions().create(params);
        long latencyMs = (System.nanoTime() - start) / 1_000_000;

        String output = completion.choices().stream()
                .findFirst()
                .flatMap(choice -> choice.message().content().stream().findFirst())
                .orElse("");

        System.out.println("\n==== " + label + " ====");
        System.out.println("latencyMs=" + latencyMs);
        System.out.println("output=" + output);
        System.out.println("usage=" + completion.usage().map(Object::toString).orElse("null"));
    }
}
