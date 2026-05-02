# ADR-003: 为什么选择 DeepSeek API

## 状态
已通过

## 背景
需要为 BaizePaw 选择一个 LLM API。选项包括：Claude、OpenAI GPT、国产模型（硅基流动/DeepSeek 等）。

## 决策
使用 DeepSeek API（`https://api.deepseek.com/v1`），模型 `deepseek-v4-flash`。

## 原因

### 1. 成本低
DeepSeek 性价比高，API 调用成本远低于 Claude 和 GPT。

### 2. 国内访问
服务器在国内，访问稳定，延迟低。

### 3. 能力足够
`deepseek-v4-flash` 虽然是 Flash 版本，但对话能力已经很不错，足够我们的场景。

### 4. 生态兼容
DeepSeek API 兼容 OpenAI 格式（`/v1/chat/completions`），迁移成本低。

## 代价

### 1. Function Calling 不完全兼容
DeepSeek 的 tool_calls 格式与 OpenAI 有细微差别，需要额外适配。

### 2. 能力上限
对比 Claude Opus 或 GPT-4，复杂推理能力有差距。

## 环境变量

```bash
export DEEPSEEK_API_KEY="sk-xxx"
export DEEPSEEK_API_BASE="https://api.deepseek.com/v1"
export MODEL_NAME="deepseek-v4-flash"
```

## 结果

当前阶段完全够用，成本可控。如果未来需要更强能力，可以升级到 Claude。
