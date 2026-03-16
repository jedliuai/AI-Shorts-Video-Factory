#!/usr/bin/env python3
"""
AI Shorts Factory — Web Dashboard (单文件版，无需模板)
访问: http://192.168.5.21:9527
"""

import json
from pathlib import Path
from datetime import datetime
import pytz
from flask import Flask, jsonify, request

app = Flask(__name__)

BASE_DIR = Path("/shorts_system")
READY_DIR          = BASE_DIR / "nas_shorts" / "ready"
UPLOADED_DIR       = BASE_DIR / "nas_shorts" / "uploaded"
UPLOAD_RESULTS     = BASE_DIR / "publishing" / "upload_results"
MANUAL_TRIGGER_DIR = BASE_DIR / "publishing" / "manual_triggers"

ET = pytz.timezone("US/Eastern")
CHANNELS = ["ch_a", "ch_b", "ch_c"]
CHANNEL_NAMES = {
    "ch_a": "🐾 AI Animal Stories",
    "ch_b": "🌌 AI Fantasy Worlds",
    "ch_c": "🧠 Micro Knowledge",
}

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Shorts Factory</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#0d1117;color:#e6edf3;min-height:100vh;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;padding-bottom:16px;border-bottom:1px solid #30363d}
h1{font-size:1.3rem;font-weight:700}h1 span{color:#58a6ff}
#clock{font-size:.8rem;color:#8b949e;background:#161b22;padding:6px 14px;border-radius:20px;border:1px solid #30363d}
.slots{display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap}
.slot{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:5px 12px;font-size:.78rem;color:#8b949e}
.slot strong{color:#58a6ff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:18px;transition:border-color .2s}
.card:hover{border-color:#58a6ff}
.ch-name{font-weight:600;font-size:.95rem;margin-bottom:14px}
.stats{display:flex;gap:10px;margin-bottom:14px}
.stat{flex:1;background:#0d1117;border-radius:8px;padding:10px;text-align:center}
.stat-val{font-size:1.4rem;font-weight:700;color:#58a6ff}
.stat-lbl{font-size:.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em}
.btn{width:100%;padding:10px;border:none;border-radius:8px;background:linear-gradient(135deg,#1f6feb,#388bfd);color:#fff;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:8px}
.btn:hover:not(:disabled){background:linear-gradient(135deg,#388bfd,#58a6ff);transform:translateY(-1px);box-shadow:0 4px 16px rgba(88,166,255,.3)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn.busy{background:linear-gradient(135deg,#d29922,#e3b341)}
.no-ready{font-size:.75rem;color:#8b949e;text-align:center;padding:8px}
.recent{margin-top:12px;border-top:1px solid #30363d;padding-top:10px}
.recent-title{font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;color:#8b949e;margin-bottom:6px}
.up-item{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(48,54,61,.4);font-size:.76rem}
.up-item:last-child{border:none}
.dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.dot.success{background:#3fb950}.dot.failed{background:#f85149}
.up-item a{color:#58a6ff;text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}
.up-item a:hover{text-decoration:underline}
.toast{position:fixed;bottom:20px;right:20px;padding:10px 18px;border-radius:10px;font-size:.82rem;font-weight:500;opacity:0;transform:translateY(8px);transition:all .3s;pointer-events:none;z-index:9999}
.toast.show{opacity:1;transform:translateY(0)}
.toast.ok{background:#3fb950;color:#000}.toast.err{background:#f85149;color:#fff}
</style>
</head>
<body>
<header>
  <h1>🎬 AI Shorts <span>Factory</span></h1>
  <div id="clock">Loading...</div>
</header>
<div class="slots" id="slots"></div>
<div class="grid" id="grid">Loading...</div>
<div class="toast" id="toast"></div>
<script>
const SLOTS=['11:30','19:30','21:30'];
document.getElementById('slots').innerHTML=
  '<span style="font-size:.78rem;color:#8b949e;line-height:30px">⏰ Scheduled (ET):</span>'+
  SLOTS.map(s=>`<div class="slot"><strong>${s}</strong></div>`).join('');

async function loadStatus(){
  const r=await fetch('/api/status');
  const d=await r.json();
  document.getElementById('clock').textContent=d.now_et;
  document.getElementById('grid').innerHTML=d.channels.map(ch=>cardHTML(ch)).join('');
}

function cardHTML(ch){
  const hasReady=ch.ready_count>0;
  const recents=ch.recent_uploads.map(r=>`
    <div class="up-item">
      <div class="dot ${r.status}"></div>
      ${r.url?`<a href="${r.url}" target="_blank" title="${r.title}">${r.title||r.video_id}</a>`
              :`<span style="color:#8b949e">${r.title||r.video_id}</span>`}
    </div>`).join('');
  return`<div class="card" id="card-${ch.channel}">
    <div class="ch-name">${ch.name}</div>
    <div class="stats">
      <div class="stat"><div class="stat-val">${ch.ready_count}</div><div class="stat-lbl">Ready</div></div>
      <div class="stat"><div class="stat-val">${ch.uploaded_count}</div><div class="stat-lbl">Uploaded</div></div>
    </div>
    ${hasReady
      ?`<button class="btn" onclick="trigger('${ch.channel}')">⚡ Upload Now</button>`
      :`<div class="no-ready">No videos in queue</div>`}
    ${recents?`<div class="recent"><div class="recent-title">Recent</div>${recents}</div>`:''}
  </div>`;
}

async function trigger(ch){
  const btn=document.querySelector(`#card-${ch} .btn`);
  if(btn){btn.disabled=true;btn.textContent='⏳ Triggering…';btn.classList.add('busy')}
  try{
    const r=await fetch('/api/trigger_upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channel:ch})});
    const d=await r.json();
    toast(r.ok?`✅ Triggered for ${ch}`:`❌ ${d.error}`,r.ok?'ok':'err');
  }catch(e){toast('❌ Network error','err')}
  setTimeout(loadStatus,1000);
}

function toast(msg,type){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className=`toast ${type} show`;
  setTimeout(()=>t.className='toast',3500);
}

loadStatus();
setInterval(loadStatus,30000);
</script>
</body>
</html>"""


def count_items(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for d in directory.iterdir() if d.is_dir())


def get_channel_status(channel: str) -> dict:
    ready_count    = count_items(READY_DIR / channel)
    uploaded_count = count_items(UPLOADED_DIR / channel)

    recent_uploads = []
    if UPLOAD_RESULTS.exists():
        results = sorted(UPLOAD_RESULTS.glob("upload_result_*.json"),
                         key=lambda f: f.stat().st_mtime, reverse=True)
        for r in results[:5]:
            try:
                data = json.loads(r.read_text())
                if data.get("channel") == channel:
                    recent_uploads.append({
                        "video_id": data.get("video_id", ""),
                        "title":    data.get("title", ""),
                        "url":      data.get("youtube_url", ""),
                        "status":   data.get("status", ""),
                    })
                    if len(recent_uploads) >= 3:
                        break
            except Exception:
                continue

    return {
        "channel":        channel,
        "name":           CHANNEL_NAMES.get(channel, channel),
        "ready_count":    ready_count,
        "uploaded_count": uploaded_count,
        "recent_uploads": recent_uploads,
    }


@app.route("/")
def index():
    return HTML


@app.route("/api/status")
def api_status():
    return jsonify({
        "now_et":   datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
        "channels": [get_channel_status(ch) for ch in CHANNELS],
    })


@app.route("/api/trigger_upload", methods=["POST"])
def trigger_upload():
    data    = request.get_json() or {}
    channel = data.get("channel", "").lower()

    if channel not in CHANNELS:
        return jsonify({"error": f"Invalid channel: {channel}"}), 400

    ready_dir = READY_DIR / channel
    if not ready_dir.exists() or not any(ready_dir.iterdir()):
        return jsonify({"error": "No videos ready for this channel"}), 400

    MANUAL_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)
    trigger_file = MANUAL_TRIGGER_DIR / f"manual_trigger_{channel}.json"
    trigger_file.write_text(json.dumps({
        "channel":      channel,
        "triggered_at": datetime.now(ET).isoformat(),
        "triggered_by": "dashboard"
    }))
    return jsonify({"success": True, "message": f"Upload triggered for {channel}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9527, debug=False)
