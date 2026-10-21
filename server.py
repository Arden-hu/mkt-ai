from __future__ import annotations

import json
import logging
import os

from flask import Flask, jsonify, render_template, request

from app.mock_generator import generate as mock_generate
from app.prompt_engine import build_messages

# Load variables from a local .env file (if present). Without this, `os.getenv`
# only reads OS-level environment variables and a configured key in .env is
# silently ignored -- which is why a "configured" model could never actually
# call its API. Guarded so the app still runs if python-dotenv is absent.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at import time
    pass

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

PLATFORMS = {"小红书", "抖音", "微博", "公众号", "朋友圈"}
GOALS = {"种草", "转化", "品牌传播", "活动推广"}
PROVIDERS = {
    "gpt": {"label": "GPT", "api_key_env": "GPT_API_KEY", "base_url_env": "GPT_BASE_URL", "model_env": "GPT_MODEL", "default_base_url": "https://api.openai.com/v1", "default_model": "gpt-4.1-mini", "demo_fallback": True},
    "deepseek": {"label": "DeepSeek", "api_key_env": "DEEPSEEK_API_KEY", "base_url_env": "DEEPSEEK_BASE_URL", "model_env": "DEEPSEEK_MODEL", "default_base_url": "https://api.deepseek.com/v1", "default_model": "deepseek-chat", "demo_fallback": False},
    "doubao": {"label": "豆包", "api_key_env": "DOUBAO_API_KEY", "base_url_env": "DOUBAO_BASE_URL", "model_env": "DOUBAO_MODEL", "default_base_url": "", "default_model": "doubao-pro-32k", "demo_fallback": False},
}


def provider_settings(provider_id: str) -> dict:
    """Resolve one provider only; legacy LLM_* variables are GPT-compatible only."""
    provider = PROVIDERS[provider_id]
    is_gpt = provider_id == "gpt"
    api_key = os.getenv(provider["api_key_env"]) or (os.getenv("LLM_API_KEY") if is_gpt else None)
    base_url = os.getenv(provider["base_url_env"]) or (os.getenv("LLM_BASE_URL") if is_gpt else None) or provider["default_base_url"]
    model = os.getenv(provider["model_env"]) or (os.getenv("LLM_MODEL") if is_gpt else None) or provider["default_model"]
    return {**provider, "id": provider_id, "api_key": api_key, "base_url": base_url, "model": model}


def provider_public_status(provider_id: str) -> dict:
    settings = provider_settings(provider_id)
    if settings["api_key"] and settings["base_url"]:
        state, message = "configured", f"已配置 · {settings['model']}"
    elif settings["demo_fallback"]:
        state, message = "demo", "演示生成器 · 未配置真实 API"
    else:
        state, message = "unconfigured", "未配置 · 需要 API Key 与 Base URL"
    return {"id": provider_id, "label": settings["label"], "state": state, "configured": state == "configured", "model": settings["model"], "message": message}


def generate_with_provider(settings: dict, payload: dict, platform: str, version: int, optimization: str | None):
    """One OpenAI-compatible request path per selected Provider; never cross-fallback."""
    try:
        from openai import OpenAI

        # 使用系统代理（OpenAI SDK 默认 trust_env=True）。本机开启 XQNetwork 等
        # 代理时，国内 Provider（DeepSeek / 豆包）与海外 GPT 都走代理出网；
        # 若代理关闭，请 unset HTTP_PROXY/HTTPS_PROXY 后启动，让国内 API 直连。
        client = OpenAI(api_key=settings["api_key"], base_url=settings["base_url"])
        response = client.chat.completions.create(
            model=settings["model"],
            messages=build_messages(payload, platform, optimization),
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        result = json.loads(response.choices[0].message.content)
        result["version"] = version
        return result
    except Exception as exc:
        app.logger.warning("Provider %s request failed: %s", settings["id"], exc)
        detail = str(exc)
        if len(detail) > 300:
            detail = detail[:300] + "..."
        raise RuntimeError(
            f"{settings['label']} 调用失败（{type(exc).__name__}）：{detail}。请检查 API Key、Base URL、模型名与账户状态。"
        ) from exc


def validate(data: dict) -> str | None:
    if not isinstance(data, dict):
        return "请求格式不正确，请刷新页面后再试。"
    for field in ("productName", "sellingPoints", "audience"):
        value = data.get(field, "")
        if not isinstance(value, str) or not value.strip():
            return "请完整填写产品名称、核心卖点和目标人群。"
    if len(data["productName"].strip()) > 60 or len(data["audience"].strip()) > 100 or len(data["sellingPoints"].strip()) > 800:
        return "产品信息过长，请精简后再生成。"
    if data.get("goal") not in GOALS:
        return "请选择营销目标。"
    if not isinstance(data.get("platforms"), list) or not data["platforms"] or not set(data["platforms"]).issubset(PLATFORMS):
        return "请至少选择一个发布平台。"
    if data.get("provider", "gpt") not in PROVIDERS:
        return "请选择可用的 AI 模型。"
    return None


@app.after_request
def _cors(response):
    # 允许跨域：静态托管的 index.html 可通过 ?api= 指向本后端调用真实模型。
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/providers")
def providers():
    return jsonify({"providers": [provider_public_status(provider_id) for provider_id in PROVIDERS]})


@app.post("/api/generate")
def generate():
    payload = request.get_json(silent=True) or {}
    error = validate(payload)
    if error:
        return jsonify({"error": error}), 400
    try:
        version = max(1, int(payload.get("version", 1)))
    except (TypeError, ValueError):
        version = 1
    optimization = payload.get("optimization")
    provider_id = payload.get("provider", "gpt")
    settings = provider_settings(provider_id)
    status = provider_public_status(provider_id)
    if not status["configured"] and not settings["demo_fallback"]:
        return jsonify({"error": f"{settings['label']} 尚未配置，未发送任何模型请求。请配置 API Key 与 Base URL 后再试。", "provider": provider_id, "provider_state": status["state"]}), 409

    results = {}
    if status["configured"]:
        try:
            for platform in payload["platforms"]:
                results[platform] = generate_with_provider(settings, payload, platform, version, optimization)
        except RuntimeError as error:
            return jsonify({"error": str(error), "provider": provider_id, "provider_state": status["state"]}), 502
        source = "llm"
    else:
        for platform in payload["platforms"]:
            results[platform] = mock_generate(payload, platform, version, optimization)
        source = "demo"
    return jsonify({"results": results, "source": source, "provider": provider_id, "provider_state": status["state"]})


def log_provider_status() -> None:
    """Emit each provider's resolved state once at startup for easy debugging."""
    for provider_id in PROVIDERS:
        status = provider_public_status(provider_id)
        if status["state"] == "configured":
            app.logger.info("Provider %s: CONFIGURED -> %s @ %s", status["id"], status["model"], status["message"])
        else:
            app.logger.info("Provider %s: %s -> %s", status["id"], status["state"].upper(), status["message"])


if __name__ == "__main__":
    log_provider_status()
    # 部署 / 本地统一入口：可用环境变量覆盖，默认本地开发。
    # PORT  对外端口（云平台注入）   HOST 绑定地址（容器/云填 0.0.0.0）
    # FLASK_DEBUG=1 才开启 debug，生产默认关闭。
    port = int(os.getenv("PORT", "5001"))
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host=host, port=port)
