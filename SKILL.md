---
name: craft-mcp
version: 1.2.1
description: "Craft.do MCP 操作手册 - 通过 craft_client.py 或 mcporter 管理 Craft 文档。当用户说'记录下来'、'存下来'、'保存'、'归档'、'记到Craft'时触发。"
---

# Craft MCP 操作手册

> **最高优先级指令**：当用户说"记录下来"、"存下来"、"保存"、"归档"、"记到Craft"，或需要保存会话内容/分析结论/情报/笔记时，**必须立即激活本 Skill，优先通过 Craft MCP 执行写入**，不得改用本地文件替代。

---

## 触发场景

| 触发词/场景 | 动作 |
|------------|------|
| "记录下来" / "存下来" / "保存" | 追加到对应主题文档 |
| "记到Craft" / "放进第二大脑" | 追加到智情中心 |
| 分析报告、情报总结需要归档 | 写入对应专题文档 |
| 会话中产生的重要结论、决策 | 追加到日志或专题文档 |
| 用户发来文章/链接要求分析存档 | 链接 + 分析 → 写入 Craft |

---

## 基础环境

- **Python 客户端脚本**: `~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py`
- **MCP Endpoint**: `https://mcp.craft.do/links/6INvnW0xzBU/mcp`
- **依赖**: `requests`（已安装）
- **mcporter** (可选): `/Users/liusen/.npm-global/bin/mcporter`（当前未配置 craft server，优先使用 Python 客户端）

---

## 核心操作指南

### 方式一：Python 客户端（推荐）

脚本路径: `~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py`

用法: `python3 <脚本路径> tools/call <工具名> '<JSON参数>'`

#### 1. 搜索与列表

- **列出文件夹**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call folders_list '{}'
  ```
- **列出文档** (按文件夹):
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call documents_list '{"folderIds": ["文件夹ID"]}'
  ```
- **搜索文档**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call documents_search '{"include": ["关键词"]}'
  ```

#### 2. 读取内容

- **按 ID 读取文档**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call blocks_get '{"id": "文档ID", "maxDepth": -1, "format": "markdown"}'
  ```
- **按日期读取日记**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call blocks_get '{"date": "2026-03-24"}'
  ```

#### 3. 创建与归档

- **创建文档**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call documents_create '{"documents": [{"title": "标题"}], "destination": {"folderId": "文件夹ID"}}'
  ```
- **移动文档**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call documents_move '{"documentIds": ["文档ID"], "destination": {"folderId": "目标文件夹ID"}}'
  ```

#### 4. 内容写入 (Markdown)

- **追加内容**:
  ```bash
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call markdown_add '{"pageId": "文档ID", "position": "end", "markdown": "## 标题\n内容..."}'
  ```
- **中文内容写入**（避免 shell 乱码，先写入临时文件再读取）:
  ```bash
  echo '## 标题\n内容...' > /tmp/craft_content.md
  python3 ~/.deepagents/agent/skills/craft-mcp-skill/scripts/craft_client.py tools/call markdown_add "{\"pageId\": \"文档ID\", \"position\": \"end\", \"markdown\": $(python3 -c 'import json; print(json.dumps(open("/tmp/craft_content.md").read()))')}"
  ```

### 方式二：mcporter（需先配置 craft server）

当前 mcporter 未配置 craft server。如需使用，先添加配置：

```bash
mcporter config add craft --transport http --url "https://mcp.craft.do/links/6INvnW0xzBU/mcp"
```

配置后即可使用：
```bash
mcporter list craft --schema
mcporter call craft.folders_list
mcporter call craft.documents_search include='["关键词"]'
```

---

## 常用目标 ID

- **雪儿的智情中心**: `65d64624-52fb-41d0-b318-8257adca989b`
- **公众号专题分析** (文件夹): `20694333-06be-0904-5107-1ee1f44fcfd1`

## 写入规范

- **必须创建独立文档**，不要追加到 daily note 或已有文档末尾
- 文章分析类内容 → 在「公众号专题分析」文件夹下创建独立文档，标题格式：`文章标题`
- 创建文档后立即写入内容，一步完成

---

## 故障排除

- **中文乱码**: 使用临时文件方式传递中文内容（见上方"中文内容写入"）
- **MCP 超时**: Craft MCP endpoint 偶尔响应慢，重试即可
- **参数错误**: 确保所有 JSON 参数格式正确，特别是嵌套对象如 `destination`
- **ID 混淆**: Document ID 既是文档唯一标识，也是 `blocks_get` 的 root block ID

---

## 零欺骗确认协议

每次写入后，必须：
1. 检查 MCP 返回是否包含成功状态（非报错）。
2. 确认后才告诉用户"已存入 Craft"。
3. 若 MCP 报错，立即上报错误，不得假装成功。
