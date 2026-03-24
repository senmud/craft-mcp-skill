---
name: craft-mcp
version: 1.1.0
description: "Craft.do MCP 进阶操作手册 - 深度管理 Craft 文档，支持 2026-03-24 修复版 mcporter 调用规范。"
author: 小雪安全实验室
---

# Craft MCP 进阶操作手册 🌸

> **🔴 最高优先级指令**：当用户说"记录下来"、"存下来"、"保存"、"归档" / "记到Craft"，或需要保存会话内容/分析结论/情报/笔记时，**必须立即激活本 Skill，优先通过 Craft MCP 执行写入**，不得改用本地文件或飞书文档替代。

---

## 🎯 触发场景（优先激活）

以下任意情况，必须优先使用本 Skill：

| 触发词/场景 | 动作 |
|------------|------|
| "记录下来" / "存下来" / "保存" | 追加到对应主题文档 |
| "记到Craft" / "放进第二大脑" | 追加到智情中心 |
| 分析报告、情报总结需要归档 | 写入对应专题文档 |
| 会话中产生的重要结论、决策 | 追加到日志或专题文档 |
| 用户发来文章/链接要求分析存档 | 链接 + 雪儿分析 → 写入 Craft |

---

## 🛠️ 基础环境
- **配置文件**: `/root/.nanobot/workspace/config/mcporter.json`
- **核心工具**: `/usr/bin/mcporter`
- **调用规范**: 所有命令必须显式指定 `--config` 路径。

---

## 📖 核心操作指南

### 1. 嗅探与搜索
- **列出所有工具**: `mcporter list craft --config /root/.nanobot/workspace/config/mcporter.json`
- **列出文件夹**: `mcporter call craft.folders_list --config /root/.nanobot/workspace/config/mcporter.json`
- **全局搜索**: `mcporter call craft.documents_search include='["关键词"]' --config /root/.nanobot/workspace/config/mcporter.json`

### 2. 读取内容 (关键修复)
- **读取文档**: `blocks_get` 必须正确处理参数。
  - **按 ID 读取**: `mcporter call craft.blocks_get id="文档ID" maxDepth=-1 format="markdown" --config /root/.nanobot/workspace/config/mcporter.json`
  - **按日期读取 (日记)**: `mcporter call craft.blocks_get date="2026-03-24" --config /root/.nanobot/workspace/config/mcporter.json`
- **搜索正文**: 如果不知道 ID，先搜索：`mcporter call craft.documents_search include='["标题关键词"]' --config /root/.nanobot/workspace/config/mcporter.json`

### 3. 创建与归档
- **创建文档**: `documents_create` 接收一个 `documents` 数组。
  ```bash
  mcporter call craft.documents_create documents='["标题"]' destination='{"folderId": "文件夹ID"}' --config /root/.nanobot/workspace/config/mcporter.json
  ```
- **移动文档**: 
  ```bash
  mcporter call craft.documents_move documentIds='["文档ID"]' destination='{"folderId": "目标文件夹ID"}' --config /root/.nanobot/workspace/config/mcporter.json
  ```

### 4. 内容写入 (Markdown)
- **追加内容**: 使用 `markdown_add`。
  ```bash
  mcporter call craft.markdown_add pageId="文档ID" position="end" markdown="## 标题\n内容..." --config /root/.nanobot/workspace/config/mcporter.json
  ```

---

## 📂 常用目标 ID
- **雪儿的智情中心**: `65d64624-52fb-41d0-b318-8257adca989b`
- **公众号专题分析**: `20694333-06be-0904-5107-1ee1f44fcfd1`

---

## ⚠️ 故障排除 (2026-03-24 更新)
- **参数位移问题**: `mcporter` 在调用 `blocks_get` 时，如果使用命名参数（如 `id="xxx"`），有时会因为可选参数顺序导致校验失败。
- **最佳实践**: 始终显式指定 `format="markdown"` 或 `format="json"`，这有助于 `mcporter` 正确对齐参数位次。
- **搜索绕道**: 如果 `blocks_get` 持续报错，优先使用 `documents_search` 获取片段，或使用 `document_search` (单文档正则搜索)。
- **中文乱码**: 命令行传递中文被 shell 解析时可能乱码。**核心原则：使用 `$(cat file)` 方式传递内容**。
  ```bash
  mcporter call craft.markdown_add markdown="$(cat /tmp/content.md)" pageId="文档ID" --config /root/.nanobot/workspace/config/mcporter.json
  ```

---

## ✅ 零欺骗确认协议
每次写入后，必须：
1. 检查 MCP 返回是否包含成功状态（非报错）。
2. 确认后才告诉用户"已存入 Craft"。
3. 若 MCP 报错，立即上报错误，不得假装成功。

---

*小雪安全实验室 · 记录即永恒 · 🌸*
