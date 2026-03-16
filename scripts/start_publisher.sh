#!/bin/bash
# Publisher 启动脚本：运行 background scanner 和 scheduler
pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 pytz flask

# 手动传视处理进程（后台执行）
python /shorts_system/scripts/publishing/manual_video_processor.py &

# inbox_watcher 在后台运行（扫描inbox，移入ready）
python /shorts_system/scripts/publishing/inbox_watcher.py &

# schedule_manager 在前台运行（定时上传 + 手动触发）
python /shorts_system/scripts/publishing/schedule_manager.py
