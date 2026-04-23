#!/usr/bin/env python3
"""
fetch_google_play.py
从 opencli browser extract 输出的 Google Play Markdown 内容中提取 App 商店元信息。

用法：
    # 先用 opencli 抓取页面并保存：
    opencli browser open "https://play.google.com/store/apps/details?id=<pkg>&hl=en-us&gl=us"
    opencli browser extract > /tmp/gplay.md

    # 然后解析：
    python3 fetch_google_play.py /tmp/gplay.md

    # 或通过 stdin：
    opencli browser extract | python3 fetch_google_play.py -

输出：JSON，包含以下字段：
    package, app_name, developer, rating, rating_count, downloads,
    last_update, category, icon_url, google_play_url
"""

import json
import re
import sys


# Google Play 分类代码 → 中文名映射
CATEGORY_MAP = {
    "BOOKS_AND_REFERENCE": "图书与参考",
    "BUSINESS": "商务",
    "COMMUNICATION": "通讯",
    "EDUCATION": "教育",
    "ENTERTAINMENT": "娱乐",
    "FINANCE": "金融",
    "FOOD_AND_DRINK": "餐饮",
    "GAME": "游戏",
    "GAME_ACTION": "游戏 · 动作",
    "GAME_ADVENTURE": "游戏 · 冒险",
    "GAME_ARCADE": "游戏 · 街机",
    "GAME_BOARD": "游戏 · 棋盘",
    "GAME_CARD": "游戏 · 卡牌",
    "GAME_CASINO": "游戏 · 赌场",
    "GAME_CASUAL": "游戏 · 休闲",
    "GAME_EDUCATIONAL": "游戏 · 教育",
    "GAME_MUSIC": "游戏 · 音乐",
    "GAME_PUZZLE": "游戏 · 益智",
    "GAME_RACING": "游戏 · 赛车",
    "GAME_ROLE_PLAYING": "游戏 · 角色扮演",
    "GAME_SIMULATION": "游戏 · 模拟",
    "GAME_SPORTS": "游戏 · 体育",
    "GAME_STRATEGY": "游戏 · 策略",
    "GAME_TRIVIA": "游戏 · 问答",
    "GAME_WORD": "游戏 · 文字",
    "HEALTH_AND_FITNESS": "健康与健身",
    "HOUSE_AND_HOME": "家居",
    "LIFESTYLE": "生活",
    "MAPS_AND_NAVIGATION": "地图与导航",
    "MEDICAL": "医疗",
    "MUSIC_AND_AUDIO": "音乐与音频",
    "NEWS_AND_MAGAZINES": "新闻与杂志",
    "PARENTING": "育儿",
    "PERSONALIZATION": "个性化",
    "PHOTOGRAPHY": "摄影",
    "PRODUCTIVITY": "效率",
    "SHOPPING": "购物",
    "SOCIAL": "社交",
    "SPORTS": "体育",
    "TOOLS": "工具",
    "TRAVEL_AND_LOCAL": "旅行与本地",
    "VIDEO_PLAYERS": "视频播放器",
    "WEATHER": "天气",
}

# 英文月份缩写 → 数字
MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def normalize_date(raw: str) -> str:
    """将 'Apr 17, 2026' 转为 '2026-04-17'"""
    m = re.match(r"(\w{3})\s+(\d{1,2}),\s+(\d{4})", raw.strip())
    if m:
        mon, day, year = m.group(1), m.group(2).zfill(2), m.group(3)
        return f"{year}-{MONTH_MAP.get(mon, mon)}-{day}"
    return raw.strip()


def parse_markdown(text: str, package: str = "") -> dict:
    result: dict = {"package": package}

    # ── 应用名称（第一个 # 标题）────────────────────────────────
    m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    result["app_name"] = m.group(1).strip() if m else ""

    # ── 开发者（/store/apps/developer?id= 链接文本）─────────────
    m = re.search(r"\[([^\]]+)\]\(/store/apps/developer\?id=", text)
    result["developer"] = m.group(1).strip() if m else ""

    # ── 评分（独立一行的 x.x 数字，出现在 reviews 之前）────────
    m = re.search(r"^([\d.]+)\s*$\n.*?reviews", text, re.MULTILINE)
    if not m:
        # fallback：找第一个 x.x 格式的独立行
        m = re.search(r"^(\d\.\d)$", text, re.MULTILINE)
    result["rating"] = m.group(1) if m else ""

    # ── 评分数量（"22.2K reviews" 或 "1,234 reviews"）───────────
    m = re.search(r"([\d.,]+[KMB]?)\s+reviews", text)
    result["rating_count"] = m.group(1) + " reviews" if m else ""

    # ── 下载量（"5M+" Downloads）────────────────────────────────
    m = re.search(r"([\d.,]+[KMB]+\+?)\s*\n+\s*Downloads", text, re.IGNORECASE)
    result["downloads"] = m.group(1) if m else ""

    # ── 最近更新日期（"Updated on\n\nApr 17, 2026"）──────────────
    m = re.search(r"Updated on\s*\n+\s*([A-Za-z]+\s+\d+,\s+\d{4})", text)
    result["last_update"] = normalize_date(m.group(1)) if m else ""

    # ── 分类（"/store/apps/category/BOOKS_AND_REFERENCE"）────────
    m = re.search(r"/store/apps/category/([A-Z_]+)", text)
    if m:
        code = m.group(1)
        result["category"] = CATEGORY_MAP.get(code, code)
    else:
        result["category"] = ""

    # ── 图标 URL（从 icon_url 字段传入，此处不解析）─────────────
    # 图标需要通过 `opencli browser eval` 单独获取（见 SKILL.md Step 2）
    result["icon_url"] = ""

    # ── Google Play 链接（从包名构造）───────────────────────────
    if result["package"]:
        result["google_play_url"] = (
            f"https://play.google.com/store/apps/details?id={result['package']}&hl=en-us&gl=us"
        )
    else:
        result["google_play_url"] = ""

    return result


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 fetch_google_play.py <markdown_file_or_-> [package_name]",
            file=sys.stderr,
        )
        sys.exit(1)

    path = sys.argv[1]
    package = sys.argv[2] if len(sys.argv) > 2 else ""

    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()

    data = parse_markdown(text, package=package)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
