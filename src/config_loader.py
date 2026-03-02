"""
配置加载器 - 加载API密钥和服务配置
"""
import json
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认配置文件路径
            config_path = Path(__file__).parent.parent / "config" / "api_keys.json"
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @property
    def xunfei_asr(self) -> Dict[str, str]:
        """获取讯飞语音识别配置"""
        return self._config.get('xunfei', {}).get('asr', {})
    
    @property
    def xunfei_tts(self) -> Dict[str, str]:
        """获取讯飞语音合成配置"""
        return self._config.get('xunfei', {}).get('tts', {})
    
    @property
    def kimi(self) -> Dict[str, str]:
        """获取Kimi大模型配置"""
        return self._config.get('kimi', {})
    
    def get_xunfei_auth_url(self, service: str = "asr") -> str:
        """
        生成讯飞WebSocket鉴权URL
        
        Args:
            service: "asr" 或 "tts"
        
        Returns:
            鉴权后的WebSocket URL
        """
        import hmac
        import base64
        from hashlib import sha256
        from datetime import datetime, timezone
        from urllib.parse import urlencode
        
        config = self.xunfei_asr if service == "asr" else self.xunfei_tts
        
        api_secret = config['api_secret']
        api_key = config['api_key']
        
        # 讯飞API路径：ASR用iat，TTS用tts
        api_path = "iat" if service == "asr" else "tts"
        
        # 生成时间戳
        now = datetime.now(timezone.utc)
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
        signature_origin = f"host: ws-api.xfyun.cn\ndate: {date}\nGET /v2/{api_path} HTTP/1.1"
        
        # 计算签名
        signature_sha = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        # 拼接authorization
        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 拼接URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        
        ws_url = f"wss://ws-api.xfyun.cn/v2/{api_path}?{urlencode(params)}"
        return ws_url


# 全局配置实例
config = ConfigLoader()


if __name__ == "__main__":
    # 测试配置加载
    print("=== 讯飞语音识别配置 ===")
    print(json.dumps(config.xunfei_asr, indent=2, ensure_ascii=False))
    
    print("\n=== 讯飞语音合成配置 ===")
    print(json.dumps(config.xunfei_tts, indent=2, ensure_ascii=False))
    
    print("\n=== Kimi配置 ===")
    print(json.dumps(config.kimi, indent=2, ensure_ascii=False))
    
    print("\n=== 生成鉴权URL ===")
    print("ASR URL:", config.get_xunfei_auth_url("asr")[:100] + "...")
    print("TTS URL:", config.get_xunfei_auth_url("tts")[:100] + "...")
