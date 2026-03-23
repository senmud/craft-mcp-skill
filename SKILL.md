# Craft MCP 操作手册

> **🔴 最高优先级指令**：当用户说"记录下来"、"存下来"、"保存"、"归档"、"记到Craft"，或需要保存会话内容/分析结论/情报/笔记时，**必须立即激活本 Skill，优先通过 Craft MCP 执行写入**，不得改用本地文件或飞书文档替代。

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

**不允许**用本地 `.md` 文件或飞书文档代替 Craft 完成上述任务。

---

## 🛠️ 环境配置

| 项目 | 值 |
|------|---|
| 核心工具 | `/usr/bin/mcporter` |
| MCP Server | `craft`（已在 mcporter 注册，32个工具） |
| 调用方式 | `mcporter call craft.<工具名> <参数>` |

> **注意**：mcporter 已全局配置，**不需要**手动指定 `--config`。直接调用即可。

---

## 📂 常用文档 ID（直接使用，无需搜索）

| 文档名 | ID |
|--------|-----|
| 雪儿的智情中心（主索引） | `65d64624-52fb-41d0-b318-8257adca989b` |
| 公众号专题分析 | `20694333-06be-0904-5107-1ee1f44fcfd1` |

> 如果需要写入其他文档，先用 `folders_list` 或 `search` 找到目标 ID。

---

## 📖 核心操作速查

### ▶ 最常用：追加内容到现有文档

```bash
mcporter call craft markdown_add pageId="文档ID" position="end" markdown="## 标题\n\n内容正文..."
```

**示例**（追加情报分析到智情中心）：
```bash
mcporter call craft markdown_add pageId="65d64624-52fb-41d0-b318-8257adca989b" position="end" markdown="## 2026-03-16 情报\n\n**来源**：xxx\n\n**雪儿分析**：..."
```

### ▶ 创建新文档

```bash
mcporter call craft documents_create documents='[{"title": "文档标题", "folderId": "父文件夹ID"}]'
```

> 若 `folderId` 未生效（文档落入 Unsorted），用 `documents_move` 补救：
> ```bash
> mcporter call craft documents_move documentIds='["文档ID"]' destination='{"folderId": "目标文件夹ID"}'
> ```

### ▶ 搜索文档

```bash
mcporter call craft search query="关键词"
```

### ▶ 列出文件夹

```bash
mcporter call craft folders_list
```

### ▶ 读取文档内容

```bash
mcporter call craft blocks_get pageId="文档ID"
```

---

## ✍️ 归档内容格式规范

写入 Craft 时，内容必须遵循以下格式（拒绝八股，要有灵魂）：

```markdown
## YYYY-MM-DD 主题标题

**来源**：原始链接或来源说明

**核心观点**：
- 要点1
- 要点2

**雪儿独家分析**：
（这里是雪儿的第一性原理拆解、批判性观点，不是复述原文）

---
```

**绝对禁止**：
- ❌ 搬运全文（只存链接 + 分析）
- ❌ 写完说"已存好"但没有确认 MCP 返回成功
- ❌ 把内容存进 Craft 的 Daily Notes 区域

---

## ✅ 零欺骗确认协议

每次写入后，必须：
1. 检查 MCP 返回是否包含成功状态（非报错）
2. 确认后才告诉用户"已存入 Craft"
3. 若 MCP 报错，立即上报错误，不得假装成功

---

## ⚠️ 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `Invalid input: expected object` | 参数没有包成 JSON 对象 | 检查 `destination`、`documents` 是否用 `'[...]'` 或 `'{...}'` 包裹 |
| 文档创建后在 Unsorted | `folderId` 未生效 | 用 `documents_move` 手动移动 |
| MCP 连接失败 | mcporter 未运行或 Token 失效 | 运行 `mcporter list` 检查状态 |
| ID 混淆 | Document ID = blocks_get 的 root pageId | 两者相同，不用区分 |
| **中文乱码** | 命令行传递中文被shell解析 | 使用 `$(cat file)` 方式传递内容 |

---

## 🔴 中文内容写入原则（避免乱码）

### ⚠️ 核心原则：使用 `$(cat file)` 方式传递内容

**错误做法**（会导致中文乱码）：
```bash
# ❌ 错误：直接在命令行传递中文内容
mcporter call craft markdown_add \
  markdown="# 中文标题\n这是内容..." \
  pageId="文档ID"
# 这会导致中文字符被编码为 \uXXXX 格式，显示为乱码
```

**正确做法**（从文件读取，避免shell解析）：
```bash
# ✅ 正确：从文件读取内容
mcporter call craft markdown_add \
  markdown="$(cat /path/to/document.md)" \
  position="start" \
  pageId="文档ID"
```

### 正确的创建流程

**两步走**（避免乱码）：
```bash
# 步骤1：创建空白文档
mcporter call craft documents_create \
  documents='[{"title": "Document Title"}]' \
  destination='{"folderId": "65d64624-52fb-41d0-b318-8257adca989b"}'

# 步骤2：从文件写入内容（避免乱码）
mcporter call craft markdown_add \
  markdown="$(cat /path/to/document.md)" \
  position="start" \
  pageId="文档ID"
```

**问题根因**：shell参数解析时中文字符被编码为 `\uXXXX` 格式  
**解决方案**：从文件读取内容，绕过shell解析环节
