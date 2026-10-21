from __future__ import annotations

import hashlib
import random


def _seed(*parts: str) -> random.Random:
    key = "|".join(parts).encode()
    return random.Random(int(hashlib.sha256(key).hexdigest()[:12], 16))


def _points(value: str) -> list[str]:
    values = [x.strip(" •·-—\n") for x in value.replace("，", "\n").split("\n")]
    return [x for x in values if x] or ["好用、实用、有设计感"]


def generate(payload: dict, platform: str, version: int = 1, optimization: str | None = None) -> dict:
    name = payload["productName"].strip() or "这款产品"
    audience = payload["audience"].strip() or "正在寻找更好选择的人"
    points = _points(payload["sellingPoints"])
    goal = payload["goal"]
    rng = _seed(name, platform, str(version), optimization or "")
    first, second = points[0], points[min(1, len(points) - 1)]
    flavor = {
        "更像真人": "像把最近的发现分享给朋友一样，",
        "更有网感": "这波真的很难不心动，",
        "更高级": "少一点喧闹，多一点恰到好处，",
        "更有转化力": "如果你正在犹豫要不要入手，先看这一点：",
        "减少AI感": "不用堆词，真正打动人的其实是细节：",
    }.get(optimization or "", "")
    goal_line = {
        "种草": "不是为了跟风，而是把日常里那些小麻烦，悄悄变得顺手。",
        "转化": "适合把钱花在真实体验上的人：看得见的方便，才值得被选择。",
        "品牌传播": "把产品做好，也是在把一种更从容的生活方式讲给更多人听。",
        "活动推广": "把这次认识它的机会留给真正需要的人，体验比口号更有说服力。",
    }[goal]
    templates = {
        "小红书": {
            "titles": [f"最近被{name}悄悄圈粉了", f"{audience}，这次真的可以看看{name}", f"不是广告，{name}的这点很戳我"],
            "subtitle": "场景种草 · 真实体验",
            "body": f"{flavor}最近用了{name}之后，才发现原来{first}可以这么省心。\n\n我是{audience}，一开始最在意的其实是它的{first}。实际用下来，{second}这个细节反而更惊喜——不是夸张的“改变生活”，而是在忙乱的时候，刚好帮你省下一点心力。\n\n{goal_line}\n\n如果你也在找一件能长期陪伴、而不是买回去吃灰的东西，可以把{name}放进备选清单。",
            "tags": ["#好物分享", "#生活方式", "#真实测评"],
            "insight": "从真实使用场景切入，降低广告感，再自然承接产品卖点。",
        },
        "抖音": {
            "titles": [f"{audience}先别划走，{name}值得看", f"我为什么把{name}留在身边", f"{name}：一个容易被低估的选择"],
            "subtitle": "短视频口播 · 前3秒抓人",
            "body": f"【开场】如果你也在为“{first}”纠结，先别急着划走。\n\n【痛点】很多产品功能不少，但真正用起来总是差最后一点顺手。\n\n【发现】{name}让我记住的，是{first}，还有{second}这个细节。\n\n【价值】{goal_line}\n\n【结尾】想了解的朋友，可以从自己的日常需求开始判断：它是不是刚好能替你解决那个小问题。",
            "tags": ["#好物推荐", "#日常好物", "#真实体验"],
            "insight": "使用“痛点—发现—价值”口播结构，确保前三秒明确、后续有记忆点。",
        },
        "微博": {
            "titles": [f"#把日常过得更顺一点# {name}给了我一个答案", f"#好产品该是什么样# {name}的一个小发现", f"#今日份好物# 为什么我想聊聊{name}"],
            "subtitle": "话题表达 · 轻传播",
            "body": f"{flavor}好产品不一定要大声证明自己。\n\n最近体验{name}，最有感的是{first}。对{audience}来说，{second}这种容易被忽略的细节，反而决定了会不会一直用下去。\n\n{goal_line}",
            "tags": ["#生活灵感", "#产品观察", "#好物分享"],
            "insight": "以可讨论的话题开场，用观点带出卖点，保留转发与互动空间。",
        },
        "公众号": {
            "titles": [f"一件好产品，如何把日常变得更从容？", f"从{name}，看见那些真正被需要的细节", f"不止于{first}：{name}的价值是什么"],
            "subtitle": "深度内容 · 价值解读",
            "body": f"## 从一个小问题说起\n\n对{audience}而言，选择产品并不是追逐复杂功能，而是希望日常少一些不必要的消耗。\n\n## {name}带来的改变\n\n{name}把重点放在{first}上，同时没有忽略{second}。这不是功能的简单罗列，而是对真实使用场景的回应。\n\n## 值得被选择的理由\n\n{goal_line}\n\n如果你也正在寻找一份更可靠、更贴近日常的体验，或许可以从{name}开始了解。",
            "tags": ["产品观察", "生活方式", "品牌故事"],
            "insight": "通过“问题—价值—选择理由”建立完整阅读逻辑，适合沉淀品牌认知。",
        },
        "朋友圈": {
            "titles": [f"最近想分享一下{name}", f"一个让我觉得很顺手的小发现", f"用了一阵子，聊聊{name}"],
            "subtitle": "朋友分享 · 轻量推荐",
            "body": f"最近在用{name}，想跟朋友们分享一下。\n\n本来是因为{first}关注到它，后来发现{second}这个细节也很用心。对{audience}来说，确实是那种越用越觉得顺手的存在。\n\n{goal_line}\n\n感兴趣可以来问我，不一定适合所有人，但也许刚好适合你。",
            "tags": [],
            "insight": "保留朋友式表达与克制的推荐感，让产品信息自然出现。",
        },
    }[platform]
    scores = {"platform": rng.randint(89, 96), "selling_point": rng.randint(86, 94), "appeal": rng.randint(87, 95), "naturalness": rng.randint(76, 89)}
    if optimization:
        scores["naturalness"] = min(96, scores["naturalness"] + 6)
    return {
        "title": rng.choice(templates["titles"]), "subtitle": templates["subtitle"], "body": templates["body"],
        "hashtags": templates["tags"], "scores": scores, "insight": templates["insight"], "version": version,
    }
