#!/bin/bash
# 快速 API 测试

echo "============================================================"
echo "AI 语音匹配平台 - 快速测试"
echo "============================================================"

echo ""
echo "1. 健康检查..."
curl -s http://localhost:8000/health | jq .

echo ""
echo "2. 测试匹配接口..."
curl -s -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "profile": {
      "age": 25,
      "gender": "male",
      "interests": ["music", "coding"],
      "bio": "程序员"
    },
    "text": "你好"
  }' | jq .

echo ""
echo "============================================================"
echo "✅ 测试完成"
echo "============================================================"
echo ""
echo "🌐 Web 界面: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
