#!/usr/bin/env python3
"""
AI Shorts Factory — Web Dashboard
提供：系统状态概览 + 手动立即上传按钮
运行在 NAS Docker 中，通过浏览器访问 http://192.168.5.21:8080
"""

import json
import os
from pathlib import Path
from datetime import datetime
import pytz
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = Path("/shorts_system")
READY_DIR         = BASE_DIR / "nas_shorts" / "ready"
UPLOADED_DIR      = BASE_DIR / "nas_shorts" / "uploaded"
FAILED_DIR        = BASE_DIR / "nas_shorts" / "failed"
UPLOAD_RESULTS    = BASE_DIR / "publishing" / "upload_results"
MANUAL_TRIGGER_DIR = BASE_DIR / "publishing" / "manual_triggers"

ET = pytz.timezone("US/Eastern")
CHANNELS = ["ch_a", "ch_b", "ch_c"]
CHANNEL_NAMES = {
    "ch_a": "🐾 AI Animal Stories",
    "ch_b": "🌌 AI Fantasy Worlds",
    "ch_c": "🧠 Micro Knowledge",
}
UPLOAD_SLOTS_ET = ["11:30", "19:30", "21:30"]


def count_items(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for d in directory.iterdir() if d.is_dir())


def get_channel_status(channel: str) -> dict:
    ready_count    = count_items(READY_DIR / channel)
    uploaded_count = count_items(UPLOADED_DIR / channel)

    # 最近上传记录
    recent_uploads = []
    if UPLOAD_RESULTS.exists():
        results = sorted(
            UPLOAD_RESULTS.glob(f"upload_result_{channel.upper().replace('_', '_')}*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        for r in results[:3]:
            try:
                data = json.loads(r.read_text())
                if data.get("channel") == channel:
                    recent_uploads.append({
                        "video_id": data.get("video_id", ""),
                        "title": data.get("title", ""),
                        "url": data.get("youtube_url", ""),
                        "status": data.get("status", ""),
                        "uploaded_at": data.get("uploaded_at", ""),
                    })
            except Exception:
                continue

    # 检查当前手动触发是否正在进行
    trigger_file = MANUAL_TRIGGER_DIR / f"manual_trigger_{channel}.json"
    is_triggering = trigger_file.exists()

    return {
        "channel": channel,
        "name": CHANNEL_NAMES.get(channel, channel),
        "ready_count": ready_count,
        "uploaded_count": uploaded_count,
        "recent_uploads": recent_uploads,
        "is_triggering": is_triggering,
    }


@app.route("/")
def index():
    now_et = datetime.now(ET)
    statuses = [get_channel_status(ch) for ch in CHANNELS]
    return render_template(
        "index.html",
        statuses=statuses,
        upload_slots=UPLOAD_SLOTS_ET,
        now_et=now_et.strftime("%Y-%m-%d %H:%M:%S ET"),
    )


@app.route("/api/status")
def api_status():
    """API端点，供前端轮询刷新状态"""
    statuses = [get_channel_status(ch) for ch in CHANNELS]
    return jsonify({
        "now_et": datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
        "channels": statuses,
    })


@app.route("/api/trigger_upload", methods=["POST"])
def trigger_upload():
    """
    手动触发上传端点
    POST /api/trigger_upload  body: {"channel": "ch_a"}
    写入信号文件 → schedule_manager.py 检测到后立即执行上传
    """
    data = request.get_json()
    channel = data.get("channel", "").lower()

    if channel not in CHANNELS:
        return jsonify({"error": f"Invalid channel: {channel}"}), 400

    # 检查是否有视频待上传
    ready_dir = READY_DIR / channel
    if not any(ready_dir.iterdir()) if ready_dir.exists() else True:
        return jsonify({"error": "No videos ready for this channel"}), 400

    # 写入触发文件
    MANUAL_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)
    trigger_file = MANUAL_TRIGGER_DIR / f"manual_trigger_{channel}.json"
    trigger_file.write_text(json.dumps({
        "channel": channel,
        "triggered_at": datetime.now(ET).isoformat(),
        "triggered_by": "dashboard"
    }))

    return jsonify({"success": True, "message": f"Upload triggered for {channel}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9527, debug=False)
