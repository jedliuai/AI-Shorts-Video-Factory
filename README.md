> **Chatgpt代充：[aishopvip.com](https://aishopvip.com)**

# 🎬 AI Shorts Factory V5
**An Autonomous, Data-Driven YouTube Shorts Generation & Publishing Matrix**  
*(全自动且基于数据驱动的 YouTube Shorts 矩阵生成与发布系统)*

---

## 🌟 Overview (项目简介)
**AI Shorts Factory V5** is a complete end-to-end automation system designed to maintain multiple YouTube channel matrices. It seamlessly integrates multi-agent prompt engineering, auto-publishing, closed-loop analytics, and manual user override features.

本系统是一套为维持 YouTube 多频道矩阵运作而设计的全端自动化架构。它将多智能体（Multi-Agent）提示词工程、自动发布、数据闭环分析以及极简的用户干预（Manual Drop）无缝集成。

### 🚀 Key Features (核心特性)
1. **Multi-Channel Matrix (多频道隔离管控)**: 
   - Dynamically manages multiple independent channels (`ch_a`, `ch_b`, `ch_c`).
   - Each channel has its own configurations, analytics, and upload schedules.
2. **Global Inbox & Intelligent Routing (全局收件箱与智能路由)**: 
   - Drop newly created AI videos (e.g., `V_A010.mp4`) directly into the `inbox/` root. The system automatically parses the ID, builds the channel structure, matches the metadata, and queues it for release.
3. **Manual Drop VIP Pipeline (自定义极简发布通道)**: 
   - Want to upload a non-system-generated video? Drop your video and a simple 3-line `.txt` file into `manual_drop/`. The processor will auto-generate complex system metrics and insert it into the global schedule.
4. **Data-Driven Optimization (数据闭环闭源)**: 
   - The ecosystem features a `Trend Scout` agent that fetches high-performing 100k+ benchmarks from YouTube, and a `Performance Analyst` that pulls daily metrics of your own videos to strictly refine the `Prompt Builder` agent.
5. **NAS Docker Deployment (纯净后台运行)**:
   - Designed to run silently 24/7 on a NAS via Docker Compose, handling OAuth 2.0 renewals and multi-slot scheduling (e.g., 11:30, 19:30, 21:30 ET).

---

## 📂 Architecture (系统架构)

```text
📁 shorts_system 
 ├── 📁 agents/                 # Multi-Agent Prompts (Prompt Builder, Trend Scout, etc.)
 ├── 📁 analytics/              # (Git-Ignored) Daily fetched YouTube metrics & summaries
 ├── 📁 config/                 # Channel niches, target audiences, and platform rules
 ├── 📁 credentials/            # (Git-Ignored) OAuth 2.0 client secrets & tokens
 ├── 📁 docker/                 # Dockerfile & docker-compose.yml 
 ├── 📁 manual_generation_queue/# (Git-Ignored) Pending and completed AI tasks
 ├── 📁 memory/                 # Agent memory (Winning hooks, losing concepts, niche rankings)
 ├── 📁 nas_shorts/             # (Git-Ignored) The core video pipeline
 │    ├── inbox/                # Global drop zone for system-generated videos
 │    ├── manual_drop/          # The 3-step pipeline for non-system videos
 │    ├── ready/                # Staged for upload
 │    ├── uploaded/             # Successfully published videos archive
 │    └── failed/               # Errored videos needing attention
 └── 📁 scripts/                # The python backend engine
      ├── 📁 publishing/        # inbox_watcher.py, schedule_manager.py, manual_video_processor.py
      ├── generate_recent_tasks.py # Translates agent thoughts into actionable tasks
      └── fetch_analytics.py    # Pulls API data daily
```

---

## 🛠️ Quick Start (快速开始)

### 1. Prerequisites (前置准备)
- Generate your OAuth 2.0 Desktop App credentials via Google Cloud Console.
- Save `client_secret.json` to the `credentials/` folder.
- Follow YouTube API guidelines.

### 2. Deployment (部署)
This project relies on Docker for robust, continuous running.
```bash
cd docker/
# Start the publisher, schedule manager, and manual video processor
docker-compose up -d shorts-publisher
# Optional: start analytics data fetching
docker-compose up -d shorts-analytics
```

### 3. Pipeline Instructions (使用指北)

**A. Sytem Generated Video Pipeline (系统标准流程):**
1. Run `python scripts/generate_recent_tasks.py`.
2. Generate videos externally using your preferred video AI (e.g., Seedance 2.0) using the outputted PROMPT text.
3. Rename the `.mp4` file to match the task ID (e.g. `V_C010.mp4`).
4. Drop the `.mp4` anywhere into the `nas_shorts/inbox/` folder. The system will handle the rest.

**B. Manual User Video Pipeline (极简私人上传通道):**
1. Copy your completely custom `.mp4` into `nas_shorts/manual_drop/[channel]/`.
2. Create a `.txt` file with the **exact same name**.
3. Inside the `.txt` file, paste three simple lines:
   ```text
   Title: Your absolutely amazing title #shorts
   Desc: This is the description shown on youtube.
   Tags: tag1, tag2, epic
   ```
4. The backend processor will automatically detect it and ingest it into the formal queue.

---

## ⚠️ Privacy & Security (安全警告)
A robust `.gitignore` has been included. It forcibly isolates the `credentials/` and heavy video directories out of source control. **Never force-add your API secrets to a public repository.**

*Built with ♥️ by an enthusiastic AI engineer & prompt architect.*
