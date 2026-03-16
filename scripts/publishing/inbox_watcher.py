#!/usr/bin/env python3
"""
Inbox Watcher — 监听 nas_shorts/inbox/ 中的新视频
每10分钟扫描一次，发现完整的视频任务后移动到 ready/ 目录

支持两种放置方式（用户任选其一）：
  方式A（推荐，更简单）: 把视频按任务单上的ID重命名（如 V_A001.mp4）
                        直接拖进 inbox/ch_a/ 根目录即可
                        → 系统自动用文件名中的ID建文件夹并匹配元数据
  方式B（原来方式）:     手动建 V_A001/ 子文件夹，放 video.mp4

⚠️  方式A 的命名规则：文件名必须和任务包里的 video_id 完全一致
    例：TASK_A001 对应 V_A001.mp4，TASK_B003 对应 V_B003.mp4
    这样无论生成顺序如何，元数据永远不会配错。
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# 路径配置
BASE_DIR = Path("/shorts_system")
INBOX_DIR = BASE_DIR / "nas_shorts" / "inbox"
READY_DIR = BASE_DIR / "nas_shorts" / "ready"
FAILED_DIR = BASE_DIR / "nas_shorts" / "failed"
COMPLETED_TASKS_DIR = BASE_DIR / "manual_generation_queue" / "completed"
LOG_DIR = BASE_DIR / "publishing" / "logs"
CONFIG_DIR = BASE_DIR / "config"

# 扫描间隔（秒）
SCAN_INTERVAL = 600  # 10 minutes

# 频道列表
CHANNELS = ["ch_a", "ch_b", "ch_c"]

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "inbox_watcher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("inbox_watcher")


def validate_video_file(video_path: Path) -> bool:
    """验证视频文件是否有效"""
    if not video_path.exists():
        return False
    
    # 检查文件大小（至少 100KB，小于 500MB）
    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb < 0.1:
        logger.warning(f"Video file too small: {video_path} ({size_mb:.2f} MB)")
        return False
    if size_mb > 500:
        logger.warning(f"Video file too large: {video_path} ({size_mb:.2f} MB)")
        return False
    
    # 检查是否为 mp4
    if video_path.suffix.lower() != ".mp4":
        logger.warning(f"Video file not MP4: {video_path}")
        return False
    
    return True


def validate_publish_prep(prep_path: Path) -> bool:
    """验证 publish_prep.json 是否有效"""
    if not prep_path.exists():
        return False
    
    try:
        with open(prep_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_fields = ["title", "description", "tags", "channel"]
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing field '{field}' in {prep_path}")
                return False
        
        # 标题长度检查
        if len(data["title"]) > 100:
            logger.warning(f"Title too long ({len(data['title'])} chars) in {prep_path}")
            return False
        
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {prep_path}: {e}")
        return False


def find_publish_prep(video_id: str, channel: str) -> Path | None:
    """
    查找 publish_prep.json
    优先从视频目录中查找，其次从 completed tasks 中匹配
    """
    # 方法1: 视频目录中直接有 publish_prep.json
    inbox_prep = INBOX_DIR / channel / video_id / "publish_prep.json"
    if inbox_prep.exists():
        return inbox_prep
    
    # 方法2: 从 completed tasks 中匹配
    # V_A001 → TASK_A001
    task_id = "TASK_" + video_id.replace("V_", "")
    task_prep = COMPLETED_TASKS_DIR / task_id / "publish_prep.json"
    if task_prep.exists():
        return task_prep
    
    # 方法3: 从 pending tasks 中查找（用户可能忘了移动task）
    pending_prep = BASE_DIR / "manual_generation_queue" / "pending" / task_id / "publish_prep.json"
    if pending_prep.exists():
        return pending_prep
    
    return None


def process_inbox_item(channel: str, video_dir: Path):
    """处理 inbox 中的单个视频目录"""
    video_id = video_dir.name  # e.g., V_A001
    video_file = video_dir / "video.mp4"
    
    logger.info(f"Processing: {channel}/{video_id}")
    
    # 1. 验证视频文件
    if not validate_video_file(video_file):
        logger.error(f"Invalid video file: {video_file}")
        # 移到 failed
        failed_dest = FAILED_DIR / f"{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(video_dir), str(failed_dest))
        return
    
    # 2. 查找并验证 publish_prep.json
    prep_path = find_publish_prep(video_id, channel)
    if prep_path is None:
        logger.warning(f"No publish_prep.json found for {video_id} — skipping (will retry next scan)")
        return
    
    if not validate_publish_prep(prep_path):
        logger.error(f"Invalid publish_prep.json for {video_id}")
        failed_dest = FAILED_DIR / f"{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(video_dir), str(failed_dest))
        return
    
    # 3. 确保 publish_prep.json 在视频目录中
    local_prep = video_dir / "publish_prep.json"
    if not local_prep.exists():
        shutil.copy2(str(prep_path), str(local_prep))
        logger.info(f"Copied publish_prep.json from {prep_path}")
    
    # 4. 添加 channel 信息到 publish_prep（如果没有）
    with open(local_prep, "r", encoding="utf-8") as f:
        prep_data = json.load(f)
    
    if "channel" not in prep_data or prep_data["channel"] != channel:
        prep_data["channel"] = channel
        with open(local_prep, "w", encoding="utf-8") as f:
            json.dump(prep_data, f, indent=2, ensure_ascii=False)
    
    # 5. 移动到 ready 目录
    ready_dest = READY_DIR / channel / video_id
    ready_dest.parent.mkdir(parents=True, exist_ok=True)
    
    if ready_dest.exists():
        logger.warning(f"Ready destination already exists: {ready_dest} — removing old one")
        shutil.rmtree(str(ready_dest))
    
    shutil.move(str(video_dir), str(ready_dest))
    logger.info(f"✅ Moved {video_id} to ready/{channel}/{video_id}")


def scan_inbox():
    """扫描所有频道的 inbox"""
    
    # ── 方式0：超级大杂烩模式 (Global Inbox) ────────────────
    # 用户把所有文件 (V_A001.mp4, V_B002.mp4, 等) 全部丢进 nas_shorts/inbox/ 根目录
    # 系统根据第三个字母自动分发到对应的 ch_a, ch_b 等子目录
    for item in sorted(INBOX_DIR.iterdir()):
        if item.is_file() and item.suffix.lower() == ".mp4":
            video_id = item.stem  # e.g. "V_A001"
            if len(video_id) >= 3 and video_id.startswith("V_"):
                # 提取频道字母，例如 'A' -> 'a'
                channel_letter = video_id[2].lower()
                target_channel_name = f"ch_{channel_letter}"
                
                if target_channel_name in CHANNELS:
                    target_channel_dir = INBOX_DIR / target_channel_name
                    target_channel_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 移动到频道的收件箱
                    new_path = target_channel_dir / item.name
                    item.rename(new_path)
                    logger.info(f"🔄 Auto-routed root file {item.name} → {target_channel_name}/")
                else:
                    logger.warning(f"Unknown channel identifier '{channel_letter}' in file {item.name}. Skipping.")

    # 扫描各频道的 inbox 处理已被分发好的文件
    for channel in CHANNELS:
        channel_inbox = INBOX_DIR / channel
        if not channel_inbox.exists():
            continue

        # ── 方式A：文件名带ID的 .mp4（如 V_A001.mp4）放在频道根目录 ──
        # 用户把视频改名为 V_A001.mp4 再拖进来，ID 从文件名读取，永不猜错
        for item in sorted(channel_inbox.iterdir()):
            if item.is_file() and item.suffix.lower() == ".mp4":
                # 从文件名提取 video_id（去掉 .mp4 后缀）
                video_id = item.stem  # e.g. "V_A001"
                if not video_id.startswith("V_"):
                    logger.warning(
                        f"Skipping {item.name}: filename must be V_XXXX.mp4 format."
                        f" Please rename it to match the task ID (e.g. V_A001.mp4)"
                    )
                    continue
                # 建对应子文件夹并把文件移入
                target_dir = channel_inbox / video_id
                target_dir.mkdir(exist_ok=True)
                item.rename(target_dir / "video.mp4")
                logger.info(f"📁 {item.name} → {video_id}/video.mp4 (ID from filename)")

        # ── 方式B：用户已建好 V_XXXX/ 子文件夹 ────────────────────────
        for item in sorted(channel_inbox.iterdir()):
            if item.is_dir() and item.name.startswith("V_"):
                try:
                    process_inbox_item(channel, item)
                except Exception as e:
                    logger.error(f"Error processing {item}: {e}", exc_info=True)


def main():
    """主循环"""
    logger.info("=" * 60)
    logger.info("Inbox Watcher started")
    logger.info(f"Watching: {INBOX_DIR}")
    logger.info(f"Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 60)
    
    # 确保必要目录存在
    for channel in CHANNELS:
        (INBOX_DIR / channel).mkdir(parents=True, exist_ok=True)
        (READY_DIR / channel).mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            logger.info("Scanning inbox...")
            scan_inbox()
            logger.info(f"Scan complete. Next scan in {SCAN_INTERVAL // 60} minutes.")
        except Exception as e:
            logger.error(f"Scan error: {e}", exc_info=True)
        
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
