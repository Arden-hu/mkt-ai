# MKT.AI v1.0

面向产品经理面试演示的 AI 多平台营销内容助手。输入一次产品 Brief，按不同内容平台生成具备结构、评分与可迭代版本的营销文案。

## 已完成

- 产品名称、核心卖点、目标人群输入
- GPT / DeepSeek / 豆包模型选择（每个 Provider 独立解析 API Key / Base URL / 模型；GPT 无密钥时走演示生成器，DeepSeek / 豆包未配置时在界面明确标注「未配置」且不发送任何请求，不做伪装）
- 「试用案例」一键填充，并自动选中全部 5 个平台
- 种草、转化、品牌传播、活动推广四类营销目标
- 小红书、抖音、微博、公众号、朋友圈多选与分别生成
- 生成过程 Loading 状态与平台内容策略提示
- 每个平台的标题、正文、标签、策略洞察与 4 项内容评分
- 一键复制、重新生成、5 种 AI 优化方向与版本切换
- 无 API Key 时自动使用完整的 Mock Generator，适合稳定演示
- 可选 OpenAI-compatible 接口，Prompt Engine 拆分为 System、Product Context、Marketing Strategy、Platform Strategy 四层
- 输入必填、长度、平台与模型校验，并在页面内给出可理解的错误提示

## 项目结构

```text
MKT.AI/
├── server.py              # Flask 路由与 LLM / Mock fallback（生产入口 wsgi.py / gunicorn 也指向它）
├── app/
│   ├── mock_generator.py  # 离线演示内容生成器
│   └── prompt_engine.py   # 四层 Prompt 组装
├── templates/index.html   # 单页应用结构
├── static/style.css       # 响应式产品视觉
├── static/app.js          # 前端状态与交互
├── requirements.txt
└── .env.example
```

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

访问 http://127.0.0.1:5001 。默认使用 Mock Mode，不需要配置任何密钥。

## 生产部署（让面试官也能访问）

应用已做生产化改造，本地开发与云部署共用一份代码：

- 默认关闭 `debug`（仅 `FLASK_DEBUG=1` 才开），支持 `PORT` / `HOST` 环境变量；
- 提供 `wsgi.py` + `Procfile` + `render.yaml`，可用 `gunicorn` 启动或一键部署到 Render；
- 密钥通过环境变量注入（本地读 `.env`，云端在平台控制台配置），**绝不进仓库**。

### 方式一：本地直接跑（最快，适合当场演示）

```bash
pip install -r requirements.txt
python server.py            # 默认 http://127.0.0.1:5001
```

### 方式二：本地 + 公网隧道（面试官远程也能开，需保持电脑开机）

在你自己的 Mac 上起服务，再用隧道把本地端口暴露成公网 URL：

```bash
pip install -r requirements.txt
python server.py &                       # 本地 5001
# 任选其一（二选一）：
brew install cloudflared && cloudflared tunnel --url http://127.0.0.1:5001   # 免费，无需账号
# 或
brew install ngrok && ngrok http 5001                                         # 需 ngrok 账号
```

终端会打印一个 `https://xxxx.trycloudflare.com` 之类的公网地址，发给面试官即可。

### 方式三：部署到云平台（最稳，关机也能访问，推荐面试用）

把仓库推到 GitHub，连 Render（免费）一键部署，获得固定公网 URL：

1. `git init && git add -A && git commit -m "MKT.AI v1.0"` 后推到 GitHub 新仓库；
2. Render 新建 **Blueprint** → 关联该仓库 → 它会读取 `render.yaml`；
3. 在 Render 控制台 **Environment** 里填 `DOUBAO_API_KEY`（以及可选的 `DEEPSEEK_API_KEY` / `GPT_API_KEY`），留空则对应模型走演示/未配置态；
4. 部署完成后得到 `https://mkt-ai.onrender.com` 这类固定地址，面试前发面试官即可。

> 云端部署时**不要**设置 `HTTP_PROXY`/`HTTPS_PROXY`：云主机可直接访问 DeepSeek / 豆包等国内服务。
> 若只填了 `DOUBAO_API_KEY`，面试官会看到「豆包=真实免费生成、GPT=演示、DeepSeek=未配置」——这已经是一个完整的多模型可演示产品。

## 接入真实模型（可选）

服务启动时会自动读取项目根目录下的 `.env` 文件（通过 python-dotenv）。复制 `.env.example` 为 `.env` 后填写变量即可，**无需手动 export**。

每个 Provider 独立解析自己的 API Key / Base URL / 模型，彼此不会串用：

- **GPT**：设置 `LLM_API_KEY`（或 `GPT_API_KEY`）、`LLM_BASE_URL`、`LLM_MODEL`。未配置时自动使用内置演示生成器（DEMO），可正常演示。
- **DeepSeek**：需设置 `DEEPSEEK_API_KEY` 与 `DEEPSEEK_BASE_URL`（OpenAI 兼容接口），可选 `DEEPSEEK_MODEL`（默认 `deepseek-chat`）。未配置时界面标注「未配置」且不发送请求。
- **豆包**：需设置 `DOUBAO_API_KEY` 与 `DOUBAO_BASE_URL`（火山引擎方舟 OpenAI 兼容接口），可选 `DOUBAO_MODEL`（默认 `doubao-pro-32k`）。未配置时界面标注「未配置」且不发送请求。

启动日志会打印每个 Provider 的 `CONFIGURED` / `DEMO` / `UNCONFIGURED` 状态，便于核对。

> 注意：DeepSeek 与豆包**不会**复用 `LLM_API_KEY`，必须填写各自的专属变量，否则会被识别为「未配置」。

## 当前 Key 配置状态（2026-10-21 实测）

| Provider | 状态 | 说明 |
| --- | --- | --- |
| GPT | 演示（DEMO） | 未提供 Key，走内置演示生成器 |
| DeepSeek | 已配置但**余额不足** | Key 鉴权与网络正常，调用返回 `402 Insufficient Balance`，需充值后生效 |
| 豆包 | 已配置 · **真实免费可用** | 用 `doubao-seed-evolving`（稳定开通 + 支持 JSON 输出，走「安心体验」免费额度）。注：`doubao-seed-2-1-*` 在 API 层仍 `ModelNotOpen`；`doubao-seed-character-*` 不支持 `json_object`，故未采用 |

## 本地网络的代理注意事项（重要）

OpenAI SDK 默认 `trust_env=True`，会读取 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量。

- **DeepSeek / 豆包**（`api.deepseek.com`、`ark.cn-beijing.volces.com`）都是**国内服务**。在你自己的 Mac 上，若 XQNetwork 等代理**正在运行且端口有效**（本机实测为 `63418` 而非已失效的 `7890`），保持代理开启即可，国内请求会正常经代理出网；若代理**已关闭**或环境变量指向一个死端口，反而要清掉代理让请求直连：

  ```bash
  unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
  python server.py
  ```

- **GPT（OpenAI）** 属海外服务，大陆环境需要**可用的海外代理**才能连通；配置 GPT 时请保持代理开启。
- **云端部署**时（Render 等）不要设置任何代理变量，云主机可直接访问国内服务。

> 排查口诀：本地真实模型调不通时，先看 `python -c "import os;print(os.getenv('HTTPS_PROXY'))"` 指向的端口是否真的在监听；代理死了就 unset，代理活着就留着。

