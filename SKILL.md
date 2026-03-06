# Craft MCP 进阶操作手册

本技能通过 `mcporter` CLI 工具与 Craft.do MCP 服务器交互，实现对 Craft 文档的深度管理。

## 🛠️ 基础环境
- **配置文件**: `/root/.openclaw/workspace/config/mcporter.json`
- **核心工具**: `/usr/bin/mcporter`
- **调用规范**: 所有命令必须显式指定 `--config` 路径。

## 📖 核心操作指南

### 1. 嗅探与搜索
- **列出所有工具**: `mcporter list craft --config /root/.openclaw/workspace/config/mcporter.json`
- **列出文件夹**: `mcporter call craft.folders_list --config /root/.openclaw/workspace/config/mcporter.json`

### 2. 创建与归档 (关键陷阱)
- **创建文档**: `documents_create` 接收一个 `documents` 数组。
  ```bash
  mcporter call craft.documents_create documents='[{"title": "标题", "folderId": "文件夹ID"}]' --config /root/.openclaw/workspace/config/mcporter.json
  ```
- **强制移动**: 如果创建时 `folderId` 未生效（掉入 Unsorted），需使用 `documents_move`。注意 `destination` 必须是对象。
  ```bash
  mcporter call craft.documents_move documentIds='["文档ID"]' destination='{"folderId": "目标文件夹ID"}' --config /root/.openclaw/workspace/config/mcporter.json
  ```

### 3. 内容写入 (Markdown)
- **追加内容**: 使用 `markdown_add`。
  ```bash
  mcporter call craft.markdown_add pageId="文档ID" position="end" markdown="## 标题\n内容..." --config /root/.openclaw/workspace/config/mcporter.json
  ```

## 📂 常用目标 ID
- **雪儿的智情中心**: `65d64624-52fb-41d0-b318-8257adca989b`
- **公众号专题分析**: `20694333-06be-0904-5107-1ee1f44fcfd1`

## ⚠️ 故障排除
- **参数错误**: 如果遇到 `Invalid input: expected object, received undefined`，通常是因为参数（如 `destination`）没有被正确包装成 JSON 对象。
- **ID 混淆**: `Document ID` 既是文档的唯一标识，也是 `blocks_get` 的 `root block ID`。
