# daily-arXiv-ai-enhanced 本地运行文档

本文档用于在本地把基础项目完整跑起来，并定位常见配置问题。

## 1. 环境要求

- macOS 或 Linux
- Python `>=3.12`
- `uv`（推荐，项目默认依赖管理工具）
- 可访问 `arxiv.org` 与你配置的 LLM API 服务

## 2. 安装依赖

在仓库根目录执行：

```bash
uv sync
source .venv/bin/activate
mkdir -p data
```

## 3. 环境变量配置

### 3.1 必填（完整流程）

- `OPENAI_API_KEY`：LLM 服务密钥

### 3.2 强烈建议配置

- `OPENAI_BASE_URL`：LLM API 根地址（重要：写到 `/v1` 即可，不要带 `/chat/completions`）
- `MODEL_NAME`：模型名，例如 `deepseek-chat`、`gemini-3-flash-preview`
- `LANGUAGE`：输出语言，例如 `Chinese` 或 `English`
- `CATEGORIES`：arXiv 分类，逗号分隔，例如 `cs.CV,cs.CL,cs.AI`

### 3.3 可选

- `TOKEN_GITHUB`：用于补充 GitHub 仓库信息（不配置也可运行）

## 4. 标准启动方式

```bash
source .venv/bin/activate
bash run.sh
```

`run.sh` 的执行链路为：

1. 爬取当日 arXiv 数据
2. 过去 7 日去重（`daily_arxiv/check_stats.py`）
3. AI 增强（`ai/enhance.py`）
4. 生成 Markdown（`to_md/convert.py`）
5. 更新文件列表（`assets/file-list.txt`）

## 5. 你当前参数的正确写法（已验证）

你提供的 URL 是 `http://xxx:xxx/v1/chat/completions`。
在本项目里应配置为：

```bash
export OPENAI_API_KEY="<YOUR_KEY>"
export OPENAI_BASE_URL="http://xxx:xxx/v1"
export MODEL_NAME="gemini-3-flash-preview"
export LANGUAGE="Chinese"
export CATEGORIES="cs.CV"
```

然后执行：

```bash
source .venv/bin/activate
bash run.sh
```

## 6. 快速链路验收（建议先做）

如果你只想先确认“爬取 + AI + 转 Markdown”是否可用，可使用小样本：

```bash
source .venv/bin/activate
today=$(date -u "+%Y-%m-%d")
mkdir -p data

# 先跑爬虫拿原始数据
cd daily_arxiv
CATEGORIES="cs.CV" scrapy crawl arxiv -o ../data/${today}.jsonl
cd ..

# 截取前 2 条做 AI 和 Markdown 验证
head -n 2 data/${today}.jsonl > data/${today}-mini.jsonl
python ai/enhance.py --data data/${today}-mini.jsonl --max_workers 1
LANGUAGE="${LANGUAGE:-Chinese}" CATEGORIES="${CATEGORIES:-cs.CV}" python to_md/convert.py --data data/${today}-mini_AI_enhanced_${LANGUAGE}.jsonl
```

## 7. 关键输出文件

- `data/YYYY-MM-DD.jsonl`：原始爬取结果（去重后）
- `data/YYYY-MM-DD_AI_enhanced_<LANGUAGE>.jsonl`：AI 增强结果
- `data/YYYY-MM-DD.md`：最终 Markdown 展示内容
- `assets/file-list.txt`：前端读取的数据文件索引

## 7.1 前端本地/远程数据切换

`index.html` 和 `statistic.html` 顶部新增了 `Remote / Local` 切换按钮：

- `Remote`：从 GitHub 仓库 `data` 分支读取数据
- `Local`：从当前站点本地路径读取 `assets/file-list.txt` 和 `data/*.jsonl`（默认）

注意：
- `Local` 模式下，需要你本地有 `data/` 文件和 `assets/file-list.txt`
- 建议通过本地静态服务器访问页面（例如 `python -m http.server 8000`）
- 选择会保存在浏览器 `localStorage`，刷新后仍保持

## 8. 常见问题排查

### 8.1 `Invalid URL (POST /v1/chat/completions/chat/completions)`

原因：`OPENAI_BASE_URL` 写成了 `.../chat/completions`，而 SDK 会自动拼接一次 `/chat/completions`。

修复：把 `OPENAI_BASE_URL` 改成只到 `/v1`。

### 8.2 `OPENAI_API_KEY not set`

原因：未导出密钥。

修复：执行 `export OPENAI_API_KEY="..."` 后重跑。

### 8.3 AI 增强文件为空

现象：`*_AI_enhanced_*.jsonl` 为空或 Markdown 内容极少。

可能原因：
- 文本被 `spam.dw-dengwei.workers.dev` 敏感词检查过滤；
- 上游模型返回异常内容导致条目被丢弃。

建议：
- 先用小样本确认；
- 检查 `ai/enhance.py` 的 stderr 输出；
- 必要时临时加日志定位是“摘要过滤”还是“AI 字段过滤”。

### 8.4 `Using SOCKS proxy, but the 'socksio' package is not installed`

原因：你的终端配置了 SOCKS 代理（如 `ALL_PROXY=socks5://...`），但 Python 环境未安装 `socksio`。

修复：

```bash
source .venv/bin/activate
uv add socksio
```

然后重新执行 `bash run.sh` 即可。

## 9. 安全提示

- 不要把 `OPENAI_API_KEY`、`TOKEN_GITHUB` 提交到 Git。
- 本地调试建议使用 shell 临时环境变量，避免写入源码文件。
