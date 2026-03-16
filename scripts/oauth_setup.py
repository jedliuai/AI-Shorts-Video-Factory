#!/usr/bin/env python3
"""
OAuth 首次授权脚本 — 在 PC 上运行一次，生成 token 文件
之后 Docker 容器会自动用这个 token 上传视频，不再需要浏览器

用法：
  python oauth_setup.py ch_a
  python oauth_setup.py ch_b
  python oauth_setup.py ch_c
"""

import sys
import os
from pathlib import Path

CREDENTIALS_DIR = Path(__file__).parent.parent / "config" / "credentials"

CHANNEL_OAUTH = {
    "ch_a": "ch_a_oauth.json",
    "ch_b": "ch_b_oauth.json",
    "ch_c": "ch_c_oauth.json",
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def setup_oauth(channel: str):
    from google_auth_oauthlib.flow import InstalledAppFlow

    oauth_file = CREDENTIALS_DIR / CHANNEL_OAUTH[channel]
    token_file = CREDENTIALS_DIR / CHANNEL_OAUTH[channel].replace(".json", "_token.json")

    if not oauth_file.exists():
        print(f"\n❌ 找不到 OAuth 凭据文件: {oauth_file}")
        print("请先从 Google Cloud Console 下载 OAuth 2.0 Client ID JSON 文件")
        print(f"并命名为: {CHANNEL_OAUTH[channel]}")
        print(f"放入: {CREDENTIALS_DIR}")
        sys.exit(1)

    print(f"\n🔐 为 {channel.upper()} 进行 OAuth 授权...")
    print(f"   凭据文件: {oauth_file}")
    print(f"   Token 将保存到: {token_file}")
    print("\n⚡ 即将打开浏览器，请登录对应的 Google 账号并授权...\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(oauth_file), SCOPES)
    creds = flow.run_local_server(port=8085, prompt="consent", access_type="offline")

    # 保存 token
    token_file.write_text(creds.to_json())
    print(f"\n✅ 授权成功！Token 已保存到:")
    print(f"   {token_file}")
    print("\n现在 Docker 容器可以自动上传视频了，无需再次授权。")
    print("( Token 过期时会自动刷新，无需重新授权 )")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CHANNEL_OAUTH:
        print("用法: python oauth_setup.py <频道>")
        print("频道: ch_a / ch_b / ch_c")
        print("\n示例:")
        print("  python oauth_setup.py ch_a")
        sys.exit(1)

    channel = sys.argv[1]
    setup_oauth(channel)
