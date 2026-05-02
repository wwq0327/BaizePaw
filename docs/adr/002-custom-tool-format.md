# ADR-002: 为什么自己发明工具调用格式

## 状态
已通过

## 背景
标准的 LLM 工具调用有 OpenAI Function Calling / Claude Tools 等规范，但我们的实现选择了自创格式：`【tool】xxx【/tool】`

## 决策
用正则匹配 `【tool】函数名【/tool】参数` 这种简单标记。

## 原因

### 1. 简单直接
不需要理解 OpenAI 的 tool_calls 结构，不需要定义 JSON Schema，直接看字符串就能知道有没有工具调用。

### 2. 模型无关
不管是 DeepSeek、Claude 还是 GPT，只要它在回复里包含这个格式，我们就能捕获。不依赖特定 API 的工具调用支持。

### 3. 调试友好
```python
# 直接打印就能看
print(response)
# 【tool】calculator【/tool】2+2
```

### 4. 学习目的
理解 Agent 的本质：解析 LLM 输出 → 调用工具 → 返回结果。不被 API 细节掩盖。

## 代价

### 1. 需要 System Prompt 引导 LLM
LLM 不知道这个格式，需要在 system prompt 里告诉它怎么用。

### 2. 参数解析简单
复杂参数（如嵌套对象）需要自己解析。当前只支持简单字符串参数。

### 3. 不够健壮
LLM 可能输出格式略有不同的变体。正则需要维护。

## 替代方案考虑

### OpenAI Function Calling
- 优点：标准、模型原生支持
- 缺点：绑定 OpenAI 生态，调试复杂

### Claude Tools
- 优点：能力强
- 缺点：需要特殊 API

## 结果

当前阶段够用。未来如果需要更复杂的工具调用，可以升级到 Function Calling 格式。
