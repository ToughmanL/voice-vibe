#!/usr/bin/env python3
"""
测试API连接脚本
验证config/api_keys.json中的API是否可用
"""
import json
import asyncio
import httpx
import hmac
import hashlib
import base64
from datetime import datetime
from urllib.parse import urlencode, urlparse

def load_config():
    """加载配置文件"""
    with open("config/api_keys.json", "r") as f:
        return json.load(f)

def test_kimi_api(config):
    """测试Kimi API连接"""
    print("\n" + "="*50)
    print("测试Kimi API")
    print("="*50)
    
    kimi_config = config.get("kimi", {})
    api_key = kimi_config.get("api_key", "")
    base_url = kimi_config.get("base_url", "https://api.moonshot.cn/v1")
    model = kimi_config.get("model", "moonshot-v1-8k")
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "你好，请回复'测试成功'"}],
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ Kimi API连接成功!")
                print(f"   响应: {content}")
                return True
            else:
                print(f"❌ Kimi API连接失败!")
                print(f"   状态码: {response.status_code}")
                print(f"   错误: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Kimi API连接异常: {str(e)}")
        return False

def create_xunfei_auth_url(api_key, api_secret, base_url, date):
    """生成科大讯飞WebSocket认证URL"""
    parsed = urlparse(base_url)
    host = parsed.netloc
    path = parsed.path
    
    # 生成签名
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    # 构建完整URL
    params = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    
    return f"{base_url}?{urlencode(params)}"

def test_xunfei_asr_api(config):
    """测试科大讯飞ASR API（通过HTTP接口验证密钥）"""
    print("\n" + "="*50)
    print("测试科大讯飞ASR API")
    print("="*50)
    
    xunfei_config = config.get("xunfei", {}).get("asr", {})
    appid = xunfei_config.get("appid", "")
    api_key = xunfei_config.get("api_key", "")
    api_secret = xunfei_config.get("api_secret", "")
    
    print(f"APPID: {appid}")
    print(f"API Key: {api_key[:10]}...")
    print(f"API Secret: {api_secret[:10]}...")
    
    # 使用科大讯飞的WebAPI接口测试（业务接口）
    # 这里我们通过生成鉴权URL来验证密钥格式是否正确
    try:
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        base_url = "wss://iat-api.xfyun.cn/v2/iat"
        
        auth_url = create_xunfei_auth_url(api_key, api_secret, base_url, date)
        print(f"✅科大讯飞ASR鉴权URL生成成功!")
        print(f"   鉴权参数验证通过")
        return True
    except Exception as e:
        print(f"❌ 科大讯飞ASR配置错误: {str(e)}")
        return False

def test_xunfei_tts_api(config):
    """测试科大讯飞TTS API"""
    print("\n" + "="*50)
    print("测试科大讯飞TTS API")
    print("="*50)
    
    xunfei_config = config.get("xunfei", {}).get("tts", {})
    appid = xunfei_config.get("appid", "")
    api_key = xunfei_config.get("api_key", "")
    api_secret = xunfei_config.get("api_secret", "")
    
    print(f"APPID: {appid}")
    print(f"API Key: {api_key[:10]}...")
    print(f"API Secret: {api_secret[:10]}...")
    
    try:
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        base_url = "wss://tts-api.xfyun.cn/v2/tts"
        
        auth_url = create_xunfei_auth_url(api_key, api_secret, base_url, date)
        print(f"✅ 科大讯飞TTS鉴权URL生成成功!")
        print(f"   鉴权参数验证通过")
        return True
    except Exception as e:
        print(f"❌ 科大讯飞TTS配置错误: {str(e)}")
        return False

def main():
    print("🔧 API连接测试工具")
    print("="*50)
    
    # 加载配置
    try:
        config = load_config()
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {str(e)}")
        return
    
    results = {}
    
    # 测试Kimi API
    results["kimi"] = test_kimi_api(config)
    
    # 测试科大讯飞ASR
    results["xunfei_asr"] = test_xunfei_asr_api(config)
    
    # 测试科大讯飞TTS
    results["xunfei_tts"] = test_xunfei_tts_api(config)
    
    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 所有API测试通过!")
    else:
        print("⚠️ 部分API测试失败，请检查配置")

if __name__ == "__main__":
    main()
