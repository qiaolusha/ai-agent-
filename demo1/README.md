# OpenAI Java SDK 入门示例

本项目是基于 OpenAI Java SDK 的入门学习示例，演示了如何调用 AI 模型（兼容 OpenAI 接口）完成基础聊天、流式输出、结构化数据提取等常见任务。


## 文件说明

[DemoConfig.java] 配置类 | 创建 AI 客户端、设置 API Key 和 Base URL
[BasicChatDemo.java] 基础聊天 | 非流式调用，一次性获取完整回复
[StreamChatDemo.java] 流式聊天 | 逐字输出，类似 ChatGPT 打字效果
[StructuredOutputDemo.java] 结构化输出 | 强制 AI 返回指定 Java 对象格式
[StructuredOutputStreamingDemo.java] 流式结构化输出 | 流式接收 + 手动解析 JSON
[UsageAndCachingDemo.java] 用量统计 | 查看 Token 消耗和响应延迟


## 核心概念

### 客户端创建
```java
OpenAIClient client = OpenAIOkHttpClient.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .baseUrl("https://api.siliconflow.cn/v1")
    .build();
```

### 非流式调用（一次性返回）
```java
ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()
    .model("模型名称")
    .addUserMessage("你的问题")
    .build();

ChatCompletion completion = client.chat().completions().create(params);
```

### 流式调用（逐字输出）
```java
try (StreamResponse<ChatCompletionChunk> stream = client.chat().completions().createStreaming(params)) {
    stream.stream()
        .flatMap(chunk -> chunk.choices().stream())
        .map(choice -> choice.delta().content().orElse(null))
        .filter(content -> content != null)
        .forEach(System.out::print);
}
```

### 结构化输出（返回 Java 对象）
```java
StructuredChatCompletionCreateParams<Candidate> params = ChatCompletionCreateParams.builder()
    .model("模型名称")
    .addUserMessage("提取简历信息")
    .responseFormat(Candidate.class)  // 指定返回类型
    .build();
```

