#!/usr/bin/env python3
"""
比较两个脚本生成的鉴权URL
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.xunfei.asr_client import XunfeiASRClient
from config_loader import ConfigLoader
import hmac
import base64
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlencode

def generate_auth_url_diagnose(api_key, api_secret, host="iat-api.xfyun.cn"):
    """诊断脚本中的URL生成方法"""
    # 生成RFC1123格式的时间戳
    now = datetime.now(timezone.utc)
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 拼接签名原文
    signature_origin = f"host: {host}\ndate: {date}\nGET /v2/iat HTTP/1.1"
    
    # 使用HMAC-SHA256计算签名
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
    
    # 拼接authorization原文
    authorization_origin = (
        f'api_key="{api_key}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{signature}"'
    )
    
    # Base64编码
    authorization = base64.b64encode(
        authorization_origin.encode('utf-8')
    ).decode(encoding='utf-8')
    
    # 构建完整URL
    params = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    
    return f"wss://{host}/v2/iat?{urlencode(params)}"

async def main():
    # 加载配置
    config_loader = ConfigLoader()
    xunfei_config = config_loader.xunfei_asr
    
    appid = xunfei_config['appid']
    api_key = xunfei_config['api_key']
    api_secret = xunfei_config['api_secret']
    
    # 创建ASR客户端
    asr_client = XunfeiASRClient(
        appid=appid,
        api_key=api_key,
        api_secret=api_secret
    )
    
    # 生成两个URL
    print("生成鉴权URL...")
    print("\n1. ASR客户端生成的URL:")
    url1 = asr_client._generate_auth_url()
    print(url1)
    
    print("\n2. 诊断脚本生成的URL:")
    url2 = generate_auth_url_diagnose(api_key, api_secret)
    print(url2)
    
    print("\n两个URL是否相同:", url1 == url2)
    
    # 测试连接
    print("\n\n测试连接...")
    
    print("\n1. 测试诊断脚本的URL:")
    try:
        import websockets
        async with websockets.connect(url2, open_timeout=10, close_timeout=5) as ws:
            print("✅ 诊断脚本的URL连接成功！")
    except Exception as e:
        print(f"❌ 诊断脚本的URL连接失败: {e}")
    
    print("\n2. 测试ASR客户端的URL:")
    try:
        async with websockets.connect(url1, open_timeout=10, close_timeout=5) as ws:
            print("✅ ASR客户端的URL连接成功！")
    except Exception as e:
        print(f"❌ ASR客户端的URL连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
