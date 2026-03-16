#!/usr/bin/env python3
"""
YouTube Uploader — 调用 YouTube Data API v3 上传视频
使用 OAuth 2.0 认证
"""

import os
import sys
import json
import logging
import httplib2
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger("youtube_uploader")

# OAuth 2.0 scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

# 可重试的 HTTP 状态码
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# 视频分类（YouTube categories）
CATEGORIES = {
    "22": "People & Blogs",
    "24": "Entertainment",
    "28": "Science & Technology",
    "15": "Pets & Animals",
    "1":  "Film & Animation"
}


def get_authenticated_service(oauth_credentials_path: str):
    """
    获取已认证的 YouTube API service（仅使用本地 token，不尝试打开浏览器）

    首次授权请在 PC 上运行: python scripts/oauth_setup.py ch_a
    生成 token 后 Docker 容器会自动使用并静默刷新。
    """
    token_path = oauth_credentials_path.replace(".json", "_token.json")

    # ── 检查 token 文件是否存在 ───────────────────────────────────────
    if not os.path.exists(token_path):
        raise RuntimeError(
            f"Token file not found: {token_path}\n"
            "Please run OAuth setup on your PC first:\n"
            "  python scripts/oauth_setup.py ch_a\n"
            "Then restart the Docker container."
        )

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # ── token 过期则用 refresh_token 静默刷新 ─────────────────────────
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            logger.info("Token expired — refreshing silently...")
            creds.refresh(Request())
            # 保存刷新后的 token
            Path(token_path).write_text(creds.to_json())
            logger.info("Token refreshed and saved.")
        else:
            raise RuntimeError(
                f"Token invalid and cannot be refreshed: {token_path}\n"
                "Please re-run: python scripts/oauth_setup.py ch_a"
            )

    return build("youtube", "v3", credentials=creds)


def do_youtube_upload(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "22",
    privacy_status: str = "public",
    oauth_credentials_path: str = "",
    made_for_kids: bool = False
) -> dict:
    """
    上传视频到 YouTube
    
    返回 YouTube API 的 response（包含 video id 等信息）
    """
    logger.info(f"Preparing to upload: {video_path}")
    logger.info(f"Title: {title}")
    logger.info(f"Privacy: {privacy_status}")
    
    # 确保 #Shorts 标签存在
    if "#Shorts" not in tags:
        tags.append("#Shorts")
    
    # 确保描述中包含 #Shorts
    if "#Shorts" not in description:
        description = description.strip() + "\n\n#Shorts"
    
    # 构建请求体
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
            "embeddable": True,
            "publicStatsViewable": True
        }
    }
    
    # 获取认证的 YouTube service
    youtube = get_authenticated_service(oauth_credentials_path)
    
    # 创建 MediaFileUpload
    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024,  # 1MB chunks
        resumable=True,
        mimetype="video/mp4"
    )
    
    # 发起上传请求
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    
    # 执行 resumable upload
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"Upload progress: {progress}%")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                logger.warning(f"Retriable HTTP error {e.resp.status}: {e.content}")
                raise  # 让上层处理重试
            else:
                logger.error(f"Non-retriable HTTP error {e.resp.status}: {e.content}")
                raise
    
    logger.info(f"✅ Upload complete! Video ID: {response.get('id')}")
    return response


if __name__ == "__main__":
    # 测试用
    print("YouTube Uploader module - import and use do_youtube_upload()")
    print("Required packages: google-api-python-client google-auth google-auth-oauthlib")
