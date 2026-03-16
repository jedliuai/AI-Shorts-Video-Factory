#!/usr/bin/env python3
"""
Analytics Fetcher — 定时抓取已上传视频的 YouTube Analytics 数据
每6小时运行一次
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pytz

# 路径配置
BASE_DIR = Path("/shorts_system")
UPLOAD_RESULTS_DIR = BASE_DIR / "publishing" / "upload_results"
ANALYTICS_RAW_DIR = BASE_DIR / "analytics" / "raw"
ANALYTICS_SUMMARIES_DIR = BASE_DIR / "analytics" / "summaries"
LOG_DIR = BASE_DIR / "analytics" / "logs"
CONFIG_DIR = BASE_DIR / "config"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"

ET = pytz.timezone("US/Eastern")

CHANNELS = ["ch_a", "ch_b", "ch_c"]
CHANNEL_OAUTH_MAP = {
    "ch_a": "ch_a_oauth.json",
    "ch_b": "ch_b_oauth.json",
    "ch_c": "ch_c_oauth.json",
}

# 抓取间隔（秒）
FETCH_INTERVAL = 6 * 3600  # 6 hours

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "fetch_analytics.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("analytics_fetcher")


def get_youtube_analytics_service(oauth_credentials_path: str):
    """获取 YouTube Analytics API service"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    
    token_path = oauth_credentials_path.replace(".json", "_token.json")
    
    if not os.path.exists(token_path):
        logger.error(f"Token not found: {token_path}. Run uploader first to authenticate.")
        return None
    
    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return build("youtubeAnalytics", "v2", credentials=creds)


def get_youtube_data_service(oauth_credentials_path: str):
    """获取 YouTube Data API service"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    
    token_path = oauth_credentials_path.replace(".json", "_token.json")
    
    if not os.path.exists(token_path):
        return None
    
    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return build("youtube", "v3", credentials=creds)


def fetch_video_analytics(channel: str, youtube_video_id: str, video_id: str):
    """抓取单个视频的 analytics 数据"""
    oauth_path = str(CREDENTIALS_DIR / CHANNEL_OAUTH_MAP[channel])
    
    analytics = get_youtube_analytics_service(oauth_path)
    if analytics is None:
        logger.error(f"Cannot get analytics service for {channel}")
        return None
    
    # 也获取 Data API 来拿基本统计
    data_service = get_youtube_data_service(oauth_path)
    
    try:
        # 基本统计数据 via Data API
        basic_stats = {}
        if data_service:
            response = data_service.videos().list(
                part="statistics,contentDetails",
                id=youtube_video_id
            ).execute()
            
            if response.get("items"):
                item = response["items"][0]
                stats = item.get("statistics", {})
                basic_stats = {
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "duration": item.get("contentDetails", {}).get("duration", "")
                }
        
        # 详细分析数据 via Analytics API
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        analytics_response = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,averageViewDuration,averageViewPercentage,likes,shares,subscribersGained",
            filters=f"video=={youtube_video_id}"
        ).execute()
        
        analytics_data = {}
        if analytics_response.get("rows"):
            row = analytics_response["rows"][0]
            headers = [h["name"] for h in analytics_response["columnHeaders"]]
            analytics_data = dict(zip(headers, row))
        
        # 组装 performance card
        performance_card = {
            "video_id": video_id,
            "youtube_video_id": youtube_video_id,
            "channel": channel,
            "fetched_at": datetime.now(ET).isoformat(),
            "basic_stats": basic_stats,
            "analytics": analytics_data,
            "computed_metrics": {}
        }
        
        # 计算衍生指标
        views = basic_stats.get("views", 0)
        if views > 0:
            performance_card["computed_metrics"] = {
                "like_rate": basic_stats.get("likes", 0) / views,
                "comment_rate": basic_stats.get("comments", 0) / views,
                "share_rate": analytics_data.get("shares", 0) / views if views else 0
            }
        
        return performance_card
        
    except Exception as e:
        logger.error(f"Error fetching analytics for {youtube_video_id}: {e}")
        return None


def fetch_all_analytics():
    """抓取所有已上传视频的 analytics"""
    if not UPLOAD_RESULTS_DIR.exists():
        logger.info("No upload results directory found")
        return
    
    total_fetched = 0
    
    for result_file in UPLOAD_RESULTS_DIR.glob("upload_result_V_*.json"):
        try:
            with open(result_file, "r") as f:
                upload_data = json.load(f)
            
            if upload_data.get("status") != "success":
                continue
            
            video_id = upload_data["video_id"]
            channel = upload_data["channel"]
            youtube_video_id = upload_data.get("youtube_video_id", "")
            
            if not youtube_video_id:
                continue
            
            logger.info(f"Fetching analytics for {video_id} ({youtube_video_id})")
            
            card = fetch_video_analytics(channel, youtube_video_id, video_id)
            
            if card:
                # 保存 performance card
                card_file = ANALYTICS_RAW_DIR / f"performance_card_{video_id}.json"
                with open(card_file, "w", encoding="utf-8") as f:
                    json.dump(card, f, indent=2, ensure_ascii=False)
                
                total_fetched += 1
                logger.info(f"✅ Saved performance card for {video_id}")
            
        except Exception as e:
            logger.error(f"Error processing {result_file}: {e}")
    
    logger.info(f"Fetched analytics for {total_fetched} videos")


def generate_daily_summary():
    """生成每日汇总"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    all_cards = []
    for card_file in ANALYTICS_RAW_DIR.glob("performance_card_*.json"):
        try:
            with open(card_file, "r") as f:
                all_cards.append(json.load(f))
        except Exception:
            continue
    
    if not all_cards:
        return
    
    # 按频道分组
    by_channel = {}
    for card in all_cards:
        ch = card.get("channel", "unknown")
        if ch not in by_channel:
            by_channel[ch] = []
        by_channel[ch].append(card)
    
    summary = {
        "date": today,
        "generated_at": datetime.now(ET).isoformat(),
        "total_videos_tracked": len(all_cards),
        "channels": {}
    }
    
    for channel, cards in by_channel.items():
        views = [c.get("basic_stats", {}).get("views", 0) for c in cards]
        summary["channels"][channel] = {
            "videos_count": len(cards),
            "total_views": sum(views),
            "average_views": sum(views) // max(len(views), 1),
            "top_video": max(cards, key=lambda c: c.get("basic_stats", {}).get("views", 0)).get("video_id", "")
        }
    
    summary_file = ANALYTICS_SUMMARIES_DIR / f"daily_report_{today}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Generated daily summary: {summary_file}")


def main():
    """主循环"""
    logger.info("=" * 60)
    logger.info("Analytics Fetcher started")
    logger.info(f"Fetch interval: {FETCH_INTERVAL // 3600} hours")
    logger.info("=" * 60)
    
    ANALYTICS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            logger.info("Starting analytics fetch cycle...")
            fetch_all_analytics()
            generate_daily_summary()
            logger.info(f"Cycle complete. Next fetch in {FETCH_INTERVAL // 3600} hours.")
        except Exception as e:
            logger.error(f"Fetch cycle error: {e}", exc_info=True)
        
        time.sleep(FETCH_INTERVAL)


if __name__ == "__main__":
    main()
