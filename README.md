# 免费 LLM API 收集器

## 功能介绍

这是一个收集国内外免费大型语言模型 API 信息的 Python 工具，包括注册要求、配额限制、支持模型等详细信息。

## 主要功能

1. **国际供应商收集**:
   - OpenAI (免费额度 $5)
   - Anthropic Claude (免费试用)
   - Google Gemini (免费额度)
   - Cohere (免费额度与积分)
   - Hugging Face (免费推理 API)
   - Replicate (免费额度支持 LLM)
   - X.ai (Grok) (免费额度)
   - OpenRouter (免费额度与积分)

2. **国内中国供应商收集**:
   - 百度文心一言 (免费额度)
   - 腾讯混元 (免费额度)
   - 百度 BoostGB (免费额度)

## 运行方法

### 安装依赖
```bash
pip install requests
```

### 运行收集器
```bash
python free_llm_collector.py
```

## 输出文件

运行脚本后将生成以下文件：

1. **`free_llm_providers.json`** - 结构化数据，包含所有供应商的详细信息
2. **`free_llm_providers.md`** - 人类可读的 Markdown 格式文档

## 使用说明

- 程序会自动收集所有 11 个免费 LLM 供应商的信息
- 支持地区分类：国际供应商 8 个，国内供应商 3 个
- 包含完整的注册流程和配额限制信息
- 提供多种导出格式方便使用

## 注册流程

每个供应商都提供了详细的注册步骤，包括：
- 访问官方网站
- 创建账户并验证邮箱
- 申请 API 权限
- 获取 API 密钥
- 开始使用免费额度

## 数据格式

### JSON 格式
```json
{
  "导出日期": "2024-XX-XX XX:XX:XX",
  "供应商总数": 11,
  "供应商列表": [
    {
      "名称": "OpenAI",
      "基础 URL": "https://api.openai.com/v1",
      "是否免费": true,
      "是否需要注册": true,
      "注册链接": "https://platform.openai.com/signup",
      "注册步骤": [...],
      "速率限制": {...},
      "支持模型": [...],
      "描述": "OpenAI 的聊天完成 API...",
      "地区": "international"
    }
  ],
  "统计信息": {
    "国际供应商数量": 8,
    "国内供应商数量": 3,
    "免费供应商数量": 11
  }
}
```

## 版本信息

- **版本**: 1.0
- **语言**: Python 3
- **维护**: 自动更新
- **更新时间**: 实时获取最新信息