#!/bin/bash
# Analytics 启动脚本：同时运行频道数据抓取 和 外部趋势抓取
pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 pytz

# 频道自己的数据（播放量/点赞/完播率）每6小时抓一次
python /shorts_system/scripts/analytics/fetch_analytics.py &

# 外部热门趋势（YouTube 搜索结果）每24小时抓一次
python /shorts_system/scripts/analytics/trend_fetcher.py
