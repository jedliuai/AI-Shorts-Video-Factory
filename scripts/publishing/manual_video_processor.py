#!/usr/bin/env python3
"""
Manual Video Processor
Allows users to drop custom videos into `nas_shorts/manual_drop/ch_x/`.
The user must provide a simplistic `.txt` file with the same base name.
Format:
Title: My Title
Desc: My Description
Tags: fun, shorts

The script will convert this into a system-ready V_Mxxx (Manual) task 
and move it to `nas_shorts/inbox/ch_x/`.
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path("/shorts_system")
MANUAL_DROP_DIR = BASE_DIR / "nas_shorts" / "manual_drop"
INBOX_DIR = BASE_DIR / "nas_shorts" / "inbox"
LOG_DIR = BASE_DIR / "publishing" / "logs"

CHANNELS = ["ch_a", "ch_b", "ch_c"]
SCAN_INTERVAL = 300  # 5 minutes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "manual_processor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("manual_processor")

def get_next_manual_id(channel: str) -> str:
    """Generate a sequential ID like M_A001 based on existing inbox/ready/completed contents."""
    # We will look for M_A, M_B, M_C prefix depending on channel
    chan_char = channel.split('_')[1].upper() # A, B, C
    prefix = f"V_{chan_char}M" # e.g., V_AM
    
    highest = 0
    # Scan inbox
    chan_inbox = INBOX_DIR / channel
    if chan_inbox.exists():
        for item in chan_inbox.iterdir():
            if item.name.startswith(prefix):
                try:
                    num = int(item.name.replace(prefix, ""))
                    highest = max(highest, num)
                except ValueError:
                    pass
                    
    # Scan ready
    chan_ready = BASE_DIR / "nas_shorts" / "ready" / channel
    if chan_ready.exists():
        for item in chan_ready.iterdir():
            if item.name.startswith(prefix):
                try:
                    num = int(item.name.replace(prefix, ""))
                    highest = max(highest, num)
                except ValueError:
                    pass
    
    # Next ID
    return f"{prefix}{highest + 1:03d}"

def parse_txt_to_json(txt_path: Path, channel: str) -> dict:
    """Parse the simplified TXT file into a valid publish_prep dictionary."""
    data = {
        "title": "My Awesome AI Video #shorts",
        "description": "Check out this video! #shorts",
        "tags": ["shorts"],
        "privacy_status": "public",
        "made_for_kids": False,
        "channel": channel
    }
    
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        lineStr = str(line.strip())
        lower_line = lineStr.lower()
        if lower_line.startswith("title:"):
            title = lineStr[6:].strip()
            if len(title) > 0:
                data["title"] = title[:100]  # Max 100 chars
        elif lower_line.startswith("desc:"):
            data["description"] = lineStr[5:].strip()
        elif lower_line.startswith("tags:"):
            # tags: abc, def, ghi
            tag_str = lineStr[5:].strip()
            tags = [t.strip() for t in tag_str.split(",") if t.strip()]
            if tags:
                data["tags"] = tags
                
    return data

def scan_manual_drops():
    for channel in CHANNELS:
        drop_dir = MANUAL_DROP_DIR / channel
        if not drop_dir.exists():
            continue
            
        # Find MP4 files
        for mp4_file in drop_dir.glob("*.mp4"):
            txt_file = mp4_file.with_suffix(".txt")
            
            if not txt_file.exists():
                logger.warning(f"Found {mp4_file.name} but missing matching {txt_file.name}. Waiting for TXT file.")
                continue
                
            logger.info(f"Processing manual drop: {mp4_file.name} in {channel}")
            
            try:
                # 1. Generate new ID
                new_id = get_next_manual_id(channel) # e.g. V_AM001
                
                # 2. Parse TXT to JSON
                prep_data = parse_txt_to_json(txt_file, channel)
                
                # 3. Create target directory in INBOX
                target_dir = INBOX_DIR / channel / new_id
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # 4. Move MP4 to video.mp4
                shutil.move(str(mp4_file), str(target_dir / "video.mp4"))
                
                # 5. Write JSON
                with open(target_dir / "publish_prep.json", "w", encoding="utf-8") as f:
                    json.dump(prep_data, f, ensure_ascii=False, indent=2)
                    
                # 6. Delete TXT
                txt_file.unlink()
                
                logger.info(f"✅ Successfully processed {mp4_file.name} -> Inbox as {new_id}")
                
            except Exception as e:
                logger.error(f"Failed to process {mp4_file.name}: {e}")

def main():
    logger.info("=" * 60)
    logger.info("Manual Video Processor started")
    logger.info(f"Watching: {MANUAL_DROP_DIR}")
    logger.info("=" * 60)
    
    # Ensure dirs exist
    for channel in CHANNELS:
        (MANUAL_DROP_DIR / channel).mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            scan_manual_drops()
        except Exception as e:
            logger.error(f"Scan error: {e}", exc_info=True)
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
