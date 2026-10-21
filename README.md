# MKT.AI · AI 多平台营销内容助手

![Demo](https://img.shields.io/badge/🚀%20Demo-在线可用-3ccf93)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)

> 一次输入产品 Brief，AI 自动理解目标人群、营销目标与平台内容逻辑，生成可直接使用的多平台营销内容。

**🚀 [在线演示 → https://arden-hu.github.io/mkt-ai/](https://arden-hu.github.io/mkt-ai/)**
点开即用，无需注册、无需 API Key，支持手机访问。

## ✨ 功能特性

- **一份 Brief，多平台产出**：同时生成小红书 / 抖音 / 微博 / 公众号 / 朋友圈五个平台的内容，每个平台按其内容逻辑独立生成。
- **四类营销目标**：内容种草、提升转化、品牌传播、活动推广。
- **结构化输出**：标题、正文、话题标签、平台内容策略洞察，以及四维内容评分（平台适配度 / 卖点表达度 / 用户吸引力 / 自然度）。
- **持续迭代**：重新生成、多版本管理（V1 / V2 …）、五种 AI 优化方向（更像真人 / 更有网感 / 更高级 / 更有转化力 / 减少 AI 感）。
- **一键复制**：单平台复制，或全平台文案汇总复制。
- **双运行模式**：
  - 离线演示模式 —— 内置生成器，零依赖、打开即用（默认）；
  - 真实多模型模式 —— 接入 GPT / DeepSeek / 豆包（OpenAI 兼容接口），通过 `?api=<后端地址>` 一键切换。

## 🛠 技术栈

- **后端**：Python 3.10+ / Flask 3 / OpenAI 兼容 SDK
- **前端**：原生 HTML + CSS + JS（自包含单文件 `index.html`，无构建步骤）
- **部署**：GitHub Pages（静态）/ Render（后端，`render.yaml` 一键部署）

## 🏃 快速开始

### 方式一：纯静态体验（0 依赖，推荐）

```bash
# 直接用浏览器打开根目录的 index.html，或起一个静态服务：
python3 -m http.server 8088   # 然后访问 http://127.0.0.1:8088
```

### 方式二：运行完整后端（真实多模型）

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 按需填入你的 API Key
python server.py              # 访问 http://127.0.0.1:5001
```

## ⚙️ 接入真实模型

复制 `.env.example` 为 `.env` 后按需填写（不填的模型自动降级为演示 / 未配置状态，应用仍可完整运行）：

| Provider | 环境变量 | 说明 |
| --- | --- | --- |
| GPT | `GPT_API_KEY` / `GPT_BASE_URL` / `GPT_MODEL` | 未配置时走内置演示生成器 |
| DeepSeek | `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` | OpenAI 兼容接口 |
| 豆包 | `DOUBAO_API_KEY` / `DOUBAO_BASE_URL` / `DOUBAO_MODEL` | 火山引擎方舟 OpenAI 兼容接口 |

组合玩法：把后端部署到 Render 等云平台后，访问 `index.html?api=https://你的后端地址`，即可在静态站点上使用真实多模型生成。

## 📡 API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/providers` | 各模型配置状态（configured / demo / unconfigured） |
| POST | `/api/generate` | 按所选平台生成营销内容，返回结构化 JSON |

## ☁️ 部署

- **静态站点**：本仓库本身就是静态站点。GitHub Pages 选择 `main` 分支、`/(root)` 目录即可（本项目已启用）。
- **后端**：Render → New Blueprint → 关联本仓库，自动读取 `render.yaml`；在 Environment 中填入模型 Key 即完成真实多模型部署。

## 🗂 项目结构

```text
├── index.html               # 自包含单文件前端（离线演示 + ?api= 真实模式）
├── server.py                # Flask 后端（生产入口，gunicorn server:app）
├── wsgi.py                  # WSGI 入口
├── app/
│   ├── prompt_engine.py     # 四层 Prompt 组装（System / 产品 / 营销 / 平台策略）
│   └── mock_generator.py    # 离线演示内容生成器（与前端 JS 版同源）
├── templates/ + static/     # Flask 版前端页面与静态资源
├── render.yaml / Procfile   # 云端部署配置
└── requirements.txt
```

## 🗺 Roadmap

- [ ] 真实多模型在线演示（Render 后端 + `?api=` 模式）
- [ ] 文案导出（Markdown / 图片卡片）
- [ ] 生成历史与收藏

## 📄 License

[MIT](LICENSE)
