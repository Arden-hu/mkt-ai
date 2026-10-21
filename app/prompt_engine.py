"""Prompt composition for the production LLM path.

Keeping the four layers separate makes strategy decisions reviewable and avoids
turning the interface copy into an opaque single prompt.
"""

from __future__ import annotations

import json

SYSTEM_PROMPT = """你是 MKT.AI 的资深内容策略师。输出中文，真实、具体、克制。
不要编造产品参数，不要使用空泛夸张的营销话术。严格返回符合 JSON schema 的对象。"""

PLATFORM_STRATEGIES = {
    "小红书": "用第一人称场景体验开场；标题有种草感；正文分段清晰，并给出自然标签。",
    "抖音": "用前三秒 Hook 开场；短句、口播节奏；按痛点、卖点、行动号召组织。",
    "微博": "从可参与的话题或观点切入；文字简洁有传播性，附带 2-4 个话题标签。",
    "公众号": "以清晰标题和小标题结构展开；有洞察、场景和可信的产品价值，避免硬广。",
    "朋友圈": "像朋友分享而非广告；内容精炼，有真实使用语气和轻量 CTA。",
}

MARKETING_STRATEGIES = {
    "种草": "优先激发兴趣与使用想象，突出真实体验和发现感。",
    "转化": "清楚说明谁为什么值得选择，并给出自然的下一步行动。",
    "品牌传播": "提升品牌调性与认知，让产品价值可被复述和分享。",
    "活动推广": "突出活动理由、时效和参与动作，不虚构价格或日期。",
}

OUTPUT_SCHEMA = {
    "title": "一条适配平台的标题",
    "subtitle": "一句内容策略摘要",
    "body": "可直接使用的正文，保留换行",
    "hashtags": ["标签1", "标签2"],
    "scores": {"platform": 90, "selling_point": 90, "appeal": 90, "naturalness": 80},
    "insight": "一句简短的平台策略说明",
}


def build_messages(payload: dict, platform: str, optimization: str | None = None) -> list[dict]:
    product_context = {
        "产品名称": payload["productName"],
        "核心卖点": payload["sellingPoints"],
        "目标人群": payload["audience"],
    }
    strategy = {
        "营销目标": payload["goal"],
        "目标策略": MARKETING_STRATEGIES[payload["goal"]],
        "平台": platform,
        "平台策略": PLATFORM_STRATEGIES[platform],
        "优化方向": optimization or "无，先生成一个高质量初稿",
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Product Context:\n" + json.dumps(product_context, ensure_ascii=False)},
        {"role": "user", "content": "Marketing Strategy:\n" + json.dumps(strategy, ensure_ascii=False)},
        {"role": "user", "content": "Platform Strategy:\n" + PLATFORM_STRATEGIES[platform]},
        {"role": "user", "content": "Return only this JSON schema:\n" + json.dumps(OUTPUT_SCHEMA, ensure_ascii=False)},
    ]
