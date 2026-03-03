#!/usr/bin/env python3
"""
科大讯飞 ASR 连接诊断工具
"""
import asyncio
import hmac
import base64
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
import socket
import sys

async def test_network():
    """测试网络连通性"""
    print("\n" + "="*60)
    print("1. 测试网络连通性")
    print("="*60)
    
    hosts = [
        "iat-api.xfyun.cn",
        "ws-api.xfyun.cn"
    ]
    
    results = {}
    for host in hosts:
        try:
            # 测试DNS解析
            ip = socket.gethostbyname(host)
            print(f"✅ {host} → {ip}")
            results[host] = {"dns": "ok", "ip": ip}
            
            # 测试端口连通性
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 443))
            sock.close()
            
            if result == 0:
                print(f"   ✅ 端口 443 可达")
                results[host]["port"] = "ok"
            else:
                print(f"   ❌ 端口 443 不可达 (错误码: {result})")
                results[host]["port"] = "failed"
                
        except socket.gaierror as e:
            print(f"❌ {host} DNS解析失败: {e}")
            results[host] = {"dns": "failed", "error": str(e)}
        except Exception as e:
            print(f"❌ {host} 连接测试失败: {e}")
            results[host] = {"error": str(e)}
    
    return results

def generate_auth_url(api_key, api_secret, host="iat-api.xfyun.cn"):
    """生成鉴权URL"""
    # 生成RFC1123格式的时间戳
    now = datetime.now(timezone.utc)
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 拼接签名原文
    signature_origin = f"host: {host}\ndate: {date}\nGET /v2/iat HTTP/1.1"
    
    print(f"\n📝 签名原文:")
    print(signature_origin)
    
    # 使用HMAC-SHA256计算签名
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
    
    print(f"\n🔑 签名 (base64): {signature}")
    
    # 拼接authorization原文
    authorization_origin = (
        f'api_key="{api_key}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{signature}"'
    )
    
    print(f"\n📝 Authorization原文:")
    print(authorization_origin)
    
    # Base64编码
    authorization = base64.b64encode(
        authorization_origin.encode('utf-8')
    ).decode(encoding='utf-8')
    
    print(f"\n🔑 Authorization (base64): {authorization[:100]}...")
    
    # 构建完整URL
    params = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    
    url = f"wss://{host}/v2/iat?{urlencode(params)}"
    return url, date

async def test_websocket_connection(url, timeout=10):
    """测试WebSocket连接"""
    print(f"\n🔗 尝试连接 WebSocket...")
    print(f"URL: {url[:100]}...")
    
    try:
        import websockets
        
        # 设置较长的超时时间（使用open_timeout参数）
        async with websockets.connect(
            url,
            open_timeout=timeout,
            close_timeout=5
        ) as ws:
            print(f"✅ WebSocket连接成功！")
            
            # 等待服务器响应（应该会返回错误，因为没有发送音频）
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"📥 收到服务器消息: {message[:200]}...")
                return True
            except asyncio.TimeoutError:
                print("⏳ 服务器未响应（正常，因为没有发送音频）")
                return True
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket握手失败: HTTP {e.status_code}")
        if hasattr(e, 'headers'):
            print(f"响应头: {dict(e.headers)}")
        return False
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ WebSocket握手失败: {e}")
        return False
    except asyncio.TimeoutError:
        print(f"❌ 连接超时（{timeout}秒）")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*60)
    print("科大讯飞 ASR 连接诊断工具")
    print("="*60)
    
    # 从配置文件读取密钥
    try:
        with open("config/api_keys.json", "r") as f:
            config = json.load(f)
            
        xunfei_config = config.get("xunfei", {}).get("asr", {})
        appid = xunfei_config.get("appid", "")
        api_key = xunfei_config.get("api_key", "")
        api_secret = xunfei_config.get("api_secret", "")
        
        if not all([appid, api_key, api_secret]):
            print("❌ 配置文件中缺少必要的密钥")
            return
            
        print(f"\n✅ 加载配置成功")
        print(f"APPID: {appid}")
        print(f"API Key: {api_key[:10]}...")
        print(f"API Secret: {api_secret[:10]}...")
        
    except FileNotFoundError:
        print("❌ 找不到配置文件: config/api_keys.json")
        return
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return
    
    # 1. 测试网络
    network_results = await test_network()
    
    # 2. 生成鉴权URL并测试连接
    print("\n" + "="*60)
    print("2. 生成鉴权URL并测试连接")
    print("="*60)
    
    # 测试两个不同的主机
    hosts = ["iat-api.xfyun.cn", "ws-api.xfyun.cn"]
    
    for host in hosts:
        print(f"\n{'='*60}")
        print(f"测试主机: {host}")
        print('='*60)
        
        # 生成鉴权URL
        url, date = generate_auth_url(api_key, api_secret, host)
        
        print(f"\n📋 鉴权信息:")
        print(f"Date: {date}")
        print(f"Host: {host}")
        print(f"\n完整URL长度: {len(url)} 字符")
        
        # 测试连接
        success = await test_websocket_connection(url)
        
        if success:
            print(f"\n✅ {host} 连接成功！")
            break
        else:
            print(f"\n❌ {host} 连接失败，尝试下一个...")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
