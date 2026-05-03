# BaizePaw 待办想法

> 记录临时想法，不拘格式。确认后移到 ADR。

---

## 当前进行

- [ ] 架构重设计：单体力拆三层，Core 改生成器，引入 Pipeline/Plugin，TUI with Textual
  - ADR-007（输入排队，已整合）
  - ADR-008（系统事件层，已通过）
  - ADR-009（Core+Pipeline+App，已通过）
  - ADR-010（TUI，已通过）
  - Plan：`docs/plans/2026-05-03-architecture-redesign.md`

## 功能建议

- [ ] 记忆模块：记住用户偏好
- [ ] 真实搜索接入（不是占位符）
- [ ] 主动建议能力
- [ ] Web 界面
- [ ] 微信接入

## 优化点

- [x] 优化 grep 忽略 __pycache__
- [x] 添加命令执行历史
- [x] 复制文件工具
- [x] 查看目录工具
- [x] 追加写入工具
- [x] 输入排队

## 已完成

- [x] v0.1 核心框架
- [x] 计算器工具
- [x] 文件读写工具
- [x] find/delete/move 文件工具
- [x] grep 文件内容搜索工具
- [x] 工具封装重构（Tool 对象、JSON 参数解析、自动生成 Prompt）
- [x] 消息封装（UserMessage / ToolCallMessage / ToolResultMessage）
- [x] 工具结果 role 分离（user vs tool）
- [x] 删除循环上限
- [x] 配置系统修正
- [x] 工具系统各 bug 修复

---
