#!/usr/bin/env python3
"""
Schedule Manager — 定时上传 + 手动触发支持
每个频道 3 个固定时间窗口（US Eastern）：11:30 / 19:30 / 21:30
同时监听手动触发信号文件，支持立即上传
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pytz

# ─── 路径配置 ───────────────────────────────────────────────
BASE_DIR = Path("/shorts_system")
READY_DIR        = BASE_DIR / "nas_shorts" / "ready"
UPLOADED_DIR     = BASE_DIR / "nas_shorts" / "uploaded"
FAILED_DIR       = BASE_DIR / "nas_shorts" / "failed"
UPLOAD_RESULTS   = BASE_DIR / "publishing" / "upload_results"
SCHEDULE_JOBS    = BASE_DIR / "publishing" / "schedule_jobs"
LOG_DIR          = BASE_DIR / "publishing" / "logs"
CONFIG_DIR       = BASE_DIR / "config"
CREDENTIALS_DIR  = CONFIG_DIR / "credentials"

# 手动触发信号文件（Web UI 写入 → 本脚本读取 → 执行后删除）
MANUAL_TRIGGER_DIR = BASE_DIR / "publishing" / "manual_triggers"

ET = pytz.timezone("US/Eastern")
CHANNELS = ["ch_a", "ch_b", "ch_c"]
CHANNEL_OAUTH = {
    "ch_a": "ch_a_oauth.json",
    "ch_b": "ch_b_oauth.json",
    "ch_c": "ch_c_oauth.json",
}

# 上传时间表（ET，格式 HH:MM）
UPLOAD_SLOTS = ["11:30", "19:30", "21:30"]

# 主循环检查间隔（秒）
CHECK_INTERVAL = 60

# ─── 日志 ────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "schedule_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("schedule_manager")


# ─── 工具函数 ─────────────────────────────────────────────────

def now_et() -> datetime:
    return datetime.now(ET)


def is_upload_slot(current: datetime, slot: str, tolerance_minutes: int = 2) -> bool:
    """判断当前时间是否在上传窗口（±tolerance_minutes）"""
    h, m = map(int, slot.split(":"))
    target = current.replace(hour=h, minute=m, second=0, microsecond=0)
    return abs((current - target).total_seconds()) <= tolerance_minutes * 60


def slot_done_marker(date_str: str, channel: str, slot: str) -> Path:
    """今日某个 slot 已完成的标记文件路径"""
    return SCHEDULE_JOBS / f"{date_str}_{channel}_{slot.replace(':', '')}.done"


def get_next_ready_video(channel: str) -> Path | None:
    """取 ready/{channel}/ 下按名称排序的第一个视频目录"""
    ch_ready = READY_DIR / channel
    if not ch_ready.exists():
        return None
    dirs = sorted(
        [d for d in ch_ready.iterdir() if d.is_dir() and d.name.startswith("V_")]
    )
    return dirs[0] if dirs else None


def archive_uploaded(video_dir: Path, channel: str, youtube_video_id: str, title: str, attempts: int):
    """上传成功后：写日志 + 移入 uploaded/"""
    video_id = video_dir.name
    result = {
        "video_id": video_id,
        "channel": channel,
        "youtube_video_id": youtube_video_id,
        "youtube_url": f"https://youtube.com/shorts/{youtube_video_id}",
        "title": title,
        "uploaded_at": now_et().isoformat(),
        "status": "success",
        "attempts": attempts,
    }
    (UPLOAD_RESULTS / f"upload_result_{video_id}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )
    dest = UPLOADED_DIR / channel / video_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(video_dir), str(dest))
    log.info(f"✅ Archived {video_id} → uploaded/{channel}/")


def archive_failed(video_dir: Path, channel: str, error: str, attempts: int):
    """上传失败后：写日志 + 移入 failed/"""
    video_id = video_dir.name
    result = {
        "video_id": video_id,
        "channel": channel,
        "status": "failed",
        "error": error,
        "failed_at": now_et().isoformat(),
        "attempts": attempts,
    }
    (UPLOAD_RESULTS / f"upload_result_{video_id}_FAILED.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )
    dest = FAILED_DIR / f"{video_id}_{now_et().strftime('%Y%m%d_%H%M%S')}"
    shutil.move(str(video_dir), str(dest))
    log.error(f"❌ Archived {video_id} → failed/")


def do_upload(video_dir: Path, channel: str) -> bool:
    """执行一次上传（含重试），返回是否成功"""
    video_file = video_dir / "video.mp4"
    prep_file  = video_dir / "publish_prep.json"
    video_id   = video_dir.name

    if not video_file.exists() or not prep_file.exists():
        log.error(f"Missing files in {video_dir}")
        return False

    meta = json.loads(prep_file.read_text(encoding="utf-8"))
    oauth_path = str(CREDENTIALS_DIR / CHANNEL_OAUTH[channel])

    if not Path(oauth_path).exists():
        log.error(
            f"OAuth credentials not found: {oauth_path}\n"
            "→ Please set up OAuth 2.0 credentials first!"
        )
        return False

    cfg = json.loads((CONFIG_DIR / "upload_settings.json").read_text())
    max_retries   = cfg["upload"]["max_retries"]
    retry_delays  = cfg["upload"]["retry_delays_seconds"]

    from youtube_uploader import do_youtube_upload

    for attempt in range(max_retries + 1):
        try:
            log.info(f"Uploading {video_id} → {channel} (attempt {attempt + 1})")
            resp = do_youtube_upload(
                video_path=str(video_file),
                title=meta.get("title", video_id),
                description=meta.get("description", ""),
                tags=meta.get("tags", ["#Shorts"]),
                category_id=meta.get("category_id", "22"),
                privacy_status=meta.get("privacy_status", "public"),
                oauth_credentials_path=oauth_path,
                made_for_kids=False,
            )
            archive_uploaded(video_dir, channel, resp.get("id", ""), meta.get("title", ""), attempt + 1)
            return True

        except Exception as exc:
            log.error(f"Attempt {attempt + 1} failed: {exc}")
            if attempt < max_retries:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                log.info(f"Retrying in {delay}s …")
                time.sleep(delay)
            else:
                archive_failed(video_dir, channel, str(exc), attempt + 1)
                return False

    return False


def upload_one(channel: str, trigger_source: str = "schedule") -> bool:
    """取下一条视频并上传，返回是否成功"""
    video_dir = get_next_ready_video(channel)
    if video_dir is None:
        log.info(f"[{trigger_source}] No ready video for {channel} — skipping")
        return False
    log.info(f"[{trigger_source}] Starting upload: {channel}/{video_dir.name}")
    return do_upload(video_dir, channel)


# ─── 手动触发逻辑 ──────────────────────────────────────────────

def check_manual_triggers():
    """
    扫描 publishing/manual_triggers/ 目录。
    Web UI 创建信号文件 manual_trigger_{channel}.json 即可触发立刻上传。
    执行后删除信号文件。
    """
    MANUAL_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)
    for trigger_file in MANUAL_TRIGGER_DIR.glob("manual_trigger_*.json"):
        try:
            data = json.loads(trigger_file.read_text())
            channel = data.get("channel", "").lower()
            if channel not in CHANNELS:
                log.warning(f"Invalid channel in trigger: {trigger_file}")
                trigger_file.unlink()
                continue

            log.info(f"🖱 Manual trigger received for {channel}")
            trigger_file.unlink()  # 先删除，避免重复触发
            upload_one(channel, trigger_source="manual")
            time.sleep(5)  # 短暂间隔
        except Exception as exc:
            log.error(f"Error processing trigger {trigger_file}: {exc}")
            trigger_file.unlink(missing_ok=True)


# ─── 定时上传逻辑 ──────────────────────────────────────────────

def check_scheduled_uploads():
    """检查是否到达上传时间窗口，若是则每个频道上传一条"""
    current = now_et()
    today   = current.strftime("%Y-%m-%d")

    for slot in UPLOAD_SLOTS:
        if not is_upload_slot(current, slot):
            continue
        # 在这个时间窗口内
        for channel in CHANNELS:
            marker = slot_done_marker(today, channel, slot)
            if marker.exists():
                continue  # 已处理
            log.info(f"⏰ Scheduled slot {slot} ET → {channel}")
            upload_one(channel, trigger_source=f"schedule_{slot}")
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
            time.sleep(30)  # 各频道间隔，避免并发


# ─── 主循环 ───────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("Schedule Manager started")
    log.info(f"Timezone : US/Eastern")
    log.info(f"Slots    : {UPLOAD_SLOTS}")
    log.info(f"Channels : {CHANNELS}")
    log.info("=" * 60)

    for ch in CHANNELS:
        (READY_DIR / ch).mkdir(parents=True, exist_ok=True)
        (UPLOADED_DIR / ch).mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_RESULTS.mkdir(parents=True, exist_ok=True)
    SCHEDULE_JOBS.mkdir(parents=True, exist_ok=True)
    MANUAL_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            check_manual_triggers()
            check_scheduled_uploads()
        except Exception as exc:
            log.error(f"Main loop error: {exc}", exc_info=True)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
