# daily-arXiv-ai-enhanced

## 简介

本项目旨在实现 **axriv 每日论文抓取 + AI 增强摘要生成**，以便持续跟踪 AI 领域前沿研究进展，提升论文筛选阅读效率。

## 工作流

GitHub Actions (`.github/workflows/run.yml`) 每天执行：

1. 抓取当天论文到 `data/YYYY-MM-DD.jsonl`
2. 做多日去重（默认回看最近 7 天）
3. 仅对“去重后新增内容”做 AI 增强
4. 产出 `data/YYYY-MM-DD_AI_enhanced_<LANGUAGE>.jsonl`
5. 更新 `assets/file-list.txt`
6. 数据提交到 `data` 分支

默认定时：`01:30 UTC`（可在 workflow 里改 cron）。

## GitHub 配置

路径：`Settings -> Secrets and variables -> Actions`

### Secrets

| 名称 | 必填 | 说明 |
|---|---|---|
| `OPENAI_API_KEY` | 是 | LLM API Key |
| `OPENAI_BASE_URL` | 是 | LLM Base URL（写到 `/v1`，不要带 `/chat/completions`） |
| `TOKEN_GITHUB` | 否 | 读取 GitHub 仓库信息（stars/更新时间） |
| `ACCESS_PASSWORD` | 否 | 页面访问密码；不填则不启用密码保护 |

### Variables

| 名称 | 必填 | 示例 | 说明 |
|---|---|---|---|
| `CATEGORIES` | 是 | `cs.AI,cs.RO,cs.CL,cs.CV` | 抓取分类（逗号分隔） |
| `LANGUAGE` | 是 | `Chinese` | 生成文件语言后缀（Chinese/English） |
| `MODEL_NAME` | 是 | `gpt-4o-mini` | 模型名 |
| `EMAIL` | 是 | `you@example.com` | 自动提交时的 git email |
| `NAME` | 是 | `Your Name` | 自动提交时的 git name |
| `AI_MAX_WORKERS` | 否 | `20` | AI 并发数（默认20，上限20） |

## 快速开始

1. Fork 本仓库。
2. 配好上面的 Secrets / Variables。
3. 打开 `Actions -> arXiv-daily-ai-enhanced`，手动运行一次 `Run workflow`。
4. 打开 `Settings -> Pages`：
   - Source: `Deploy from a branch`
   - Branch: `main` + `/(root)`
5. 等待构建完成后访问：
   - `https://<你的用户名>.github.io/daily-arXiv-ai-enhanced/`

## 目录说明

- `daily_arxiv/`：爬虫与去重
- `ai/`：AI 增强
- `to_md/`：Markdown 转换
- `js/`：前端逻辑（含数据源切换）
- `data/`：生成的数据文件
- `.github/workflows/run.yml`：自动化流程
