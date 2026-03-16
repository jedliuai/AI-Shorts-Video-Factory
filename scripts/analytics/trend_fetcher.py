#!/usr/bin/env python3
"""
Trend Fetcher — 每日自动抓取 YouTube 热门 Shorts 趋势数据
数据用于 Antigravity Trend Scout Agent 生成提示词时参考

功能：
  1. 用 YouTube Data API v3 搜索各频道关键词的热门 Shorts
  2. 获取视频标题、描述、标签、播放量、点赞数
  3. 提取高频关键词和 hook 模式
  4. 保存到 analytics/trends/ 供 Antigravity 读取

运行频率：每天一次（每24小时）
"""

import os
import json
import time
import logging
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import pytz

# ─── 路径配置 ─────────────────────────────────────────────────
BASE_DIR      = Path("/shorts_system")
CONFIG_DIR    = BASE_DIR / "config"
TRENDS_DIR    = BASE_DIR / "analytics" / "trends"
LOG_DIR       = BASE_DIR / "analytics" / "logs"

ET = pytz.timezone("US/Eastern")

# YouTube Data API Key（公开数据，无需 OAuth）
API_KEY_FILE  = BASE_DIR / "config" / "api_key.txt"

CHANNELS = {
    "ch_a": CONFIG_DIR / "channels" / "ch_a_animals.json",
    "ch_b": CONFIG_DIR / "channels" / "ch_b_fantasy.json",
    "ch_c": CONFIG_DIR / "channels" / "ch_c_knowledge.json",
}

# 每个关键词抓取的视频数量
RESULTS_PER_KEYWORD = 10

# 运行间隔（24小时）
FETCH_INTERVAL = 24 * 3600

# ─── 日志 ────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "trend_fetcher.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("trend_fetcher")


# ─── API 工具 ─────────────────────────────────────────────────

def get_api_key() -> str:
    """从文件或环境变量读取 API Key"""
    # 优先从环境变量读取
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if key:
        return key
    # 从文件读取
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()
    # 从 .env 文件找（PC 端使用）
    env_file = BASE_DIR.parent / ".env"
    if not env_file.exists():
        env_file = Path("/shorts_system/../.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "AIzaSy" in line:
                # 提取 API key（格式：...Key：AIzaSyXXXX）
                match = re.search(r"(AIzaSy[A-Za-z0-9_-]{33})", line)
                if match:
                    return match.group(1)
    return ""


def search_shorts(api_key: str, query: str, max_results: int = 10) -> list:
    """
    搜索 YouTube Shorts
    使用 YouTube Data API v3 search.list endpoint
    """
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", developerKey=api_key)

    # 搜索最近7天的短视频
    published_after = (datetime.utcnow() - timedelta(days=7)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    try:
        search_response = youtube.search().list(
            q=query + " #shorts",
            part="id,snippet",
            type="video",
            videoDuration="short",          # 60秒以内
            order="viewCount",              # 按播放量排序
            publishedAfter=published_after,
            maxResults=max_results,
            relevanceLanguage="en",
        ).execute()
    except Exception as e:
        log.error(f"Search failed for '{query}': {e}")
        return []

    video_ids = [
        item["id"]["videoId"]
        for item in search_response.get("items", [])
        if item["id"].get("videoId")
    ]

    if not video_ids:
        return []

    # 获取详细统计数据
    try:
        stats_response = youtube.videos().list(
            part="statistics,snippet,contentDetails",
            id=",".join(video_ids),
        ).execute()
    except Exception as e:
        log.error(f"Stats fetch failed: {e}")
        return []

    results = []
    for item in stats_response.get("items", []):
        snippet = item.get("snippet", {})
        stats   = item.get("statistics", {})
        results.append({
            "video_id":     item["id"],
            "title":        snippet.get("title", ""),
            "description":  snippet.get("description", "")[:300],
            "tags":         snippet.get("tags", [])[:20],
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count":   int(stats.get("viewCount",   0)),
            "like_count":   int(stats.get("likeCount",   0)),
            "comment_count":int(stats.get("commentCount",0)),
            "duration":     item.get("contentDetails", {}).get("duration", ""),
        })

    # 按播放量排序
    results.sort(key=lambda x: x["view_count"], reverse=True)
    return results


# ─── 分析工具 ─────────────────────────────────────────────────

def extract_hook_patterns(videos: list) -> dict:
    """
    从热门视频标题中提取 hook 模式
    用于 Trend Scout Agent 生成新提示词时参考
    """
    titles = [v["title"] for v in videos if v["view_count"] > 10000]

    # 常见 hook 开头词（疑问 / 惊叹 / 数字）
    hook_openers = Counter()
    for title in titles:
        title_lower = title.lower()
        # 疑问 hook
        for word in ["what", "why", "how", "when", "watch", "look"]:
            if title_lower.startswith(word):
                hook_openers[word] += 1
        # 惊叹 hook
        for word in ["this", "the moment", "you won't", "nobody expected", "unbelievable", "insane"]:
            if word in title_lower:
                hook_openers[word] += 1
        # 数字 hook
        if re.match(r"^\d", title):
            hook_openers["[number]"] += 1

    # 高频词（过滤常见无意义词）
    stop_words = {"a", "an", "the", "is", "are", "was", "were", "to", "of", "in",
                  "on", "at", "by", "for", "with", "and", "or", "but", "this", "that"}
    all_words = Counter()
    for title in titles:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
        for w in words:
            if w not in stop_words:
                all_words[w] += 1

    # 高播放量视频的标题模式
    top_titles = [
        {"title": v["title"], "views": v["view_count"]}
        for v in videos[:5]
        if v["view_count"] > 0
    ]

    return {
        "hook_openers":  dict(hook_openers.most_common(10)),
        "trending_words": dict(all_words.most_common(20)),
        "top_titles":    top_titles,
    }


def analyze_tags(videos: list) -> list:
    """统计最常出现的标签"""
    tag_counter = Counter()
    for v in videos:
        for tag in v.get("tags", []):
            tag_counter[tag.lower()] += 1
    return [tag for tag, _ in tag_counter.most_common(30)]


# ─── 主抓取逻辑 ───────────────────────────────────────────────

def fetch_trends_for_channel(channel: str, config_path: Path, api_key: str):
    """抓取单个频道的趋势数据"""
    log.info(f"Fetching trends for {channel}...")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    keywords = config.get("trend_keywords", [])

    all_videos = []
    seen_ids   = set()

    for kw in keywords:
        log.info(f"  Searching: '{kw}'")
        videos = search_shorts(api_key, kw, max_results=RESULTS_PER_KEYWORD)
        for v in videos:
            if v["video_id"] not in seen_ids:
                seen_ids.add(v["video_id"])
                all_videos.append(v)
        time.sleep(1)  # 礼貌性延迟，避免触发配额限制

    # 去重 + 排序
    all_videos.sort(key=lambda x: x["view_count"], reverse=True)

    # 分析
    patterns = extract_hook_patterns(all_videos)
    top_tags  = analyze_tags(all_videos)

    # 筛选出高播放量视频（>10万播放）作为"标杆"
    benchmark_videos = [v for v in all_videos if v["view_count"] >= 100_000]

    result = {
        "channel":          channel,
        "niche":            config.get("niche", ""),
        "fetched_at":       datetime.now(ET).isoformat(),
        "keywords_searched":keywords,
        "total_videos_found": len(all_videos),
        "benchmark_videos_100k_plus": len(benchmark_videos),

        # 前10热门视频（供 Antigravity 分析）
        "top_10_videos": all_videos[:10],

        # 标杆视频（高播放量，重点参考）
        "benchmark_videos": benchmark_videos[:20],

        # 提取的模式
        "hook_patterns":  patterns,
        "trending_tags":  top_tags,

        # 给 Trend Scout Agent 的快速摘要
        "scout_brief": {
            "hot_topics": patterns["trending_words"],
            "best_hook_openers": list(patterns["hook_openers"].keys())[:5],
            "top_titles_this_week": patterns["top_titles"],
            "recommended_tags": top_tags[:15],
        }
    }

    # 保存原始数据
    today = datetime.now().strftime("%Y-%m-%d")
    raw_file = TRENDS_DIR / channel / f"trends_{today}.json"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # 覆盖写入"最新"文件（供 Antigravity 快速读取）
    latest_file = TRENDS_DIR / channel / "trends_latest.json"
    latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    log.info(
        f"  ✅ {channel}: {len(all_videos)} videos found, "
        f"{len(benchmark_videos)} benchmarks (100k+), saved to {raw_file.name}"
    )
    return result


def fetch_all_trends(api_key: str):
    """抓取所有频道的趋势"""
    log.info("=" * 50)
    log.info(f"Trend fetch cycle started at {datetime.now(ET).strftime('%Y-%m-%d %H:%M ET')}")

    summary = {}
    for channel, config_path in CHANNELS.items():
        try:
            result = fetch_trends_for_channel(channel, config_path, api_key)
            summary[channel] = {
                "total_found":     result["total_videos_found"],
                "benchmarks_100k": result["benchmark_videos_100k_plus"],
                "fetched_at":      result["fetched_at"],
            }
        except Exception as e:
            log.error(f"Failed to fetch trends for {channel}: {e}", exc_info=True)
            summary[channel] = {"error": str(e)}

    # 保存全局摘要
    summary_file = TRENDS_DIR / f"trend_summary_{datetime.now().strftime('%Y-%m-%d')}.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(json.dumps({
        "generated_at": datetime.now(ET).isoformat(),
        "channels":     summary,
    }, indent=2, ensure_ascii=False))

    log.info(f"Trend cycle complete. Next fetch in 24 hours.")
    log.info("=" * 50)


# ─── 主循环 ───────────────────────────────────────────────────

def main():
    TRENDS_DIR.mkdir(parents=True, exist_ok=True)

    api_key = get_api_key()
    if not api_key:
        log.error(
            "YouTube API key not found!\n"
            "Set YOUTUBE_API_KEY environment variable, or create:\n"
            "  /shorts_system/config/api_key.txt"
        )
        sys.exit(1)

    log.info(f"YouTube API key loaded ✅ (ends with ...{api_key[-6:]})")

    while True:
        try:
            fetch_all_trends(api_key)
        except Exception as e:
            log.error(f"Trend fetch failed: {e}", exc_info=True)

        time.sleep(FETCH_INTERVAL)


if __name__ == "__main__":
    main()
