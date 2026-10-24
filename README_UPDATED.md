# Free LLM API Collector - Updated

## Overview

This is an updated version with significantly more LLM providers covering both domestic and international free API services.

## International Providers (20 providers)

1. **OpenAI** - Free $5 credit for new users
2. **Anthropic** - Claude free trial
3. **Google AI** - Gemini free tier
4. **Cohere** - Free credits
5. **Hugging Face** - Free inference API for open-source models
6. **Replicate** - Free credits for various models
7. **X.ai (Grok)** - Free tier access
8. **OpenRouter** - Aggregated LLMs with free tier
9. **Opencode** - Multiple model access with free quota
10. **Cline** - Enhanced Claude with free tier
11. **Fireworks AI** - Free quota for various models
12. **Groq** - Ultra-fast inference with free quota
13. **Lambda Labs** - GPU-accelerated inference free quota
14. **Together AI** - Open-source models free quota
15. **Poe** - Multi-model access free quota
16. **Anyscale** - Free endpoints for open-source models
17. **Perplexity AI** - Search-enhanced LLM free quota
18. **Mistral AI** - Efficient open-source models free quota
19. **DeepSeek** - High-performance models free quota
20. **Qwen** - Alibaba's open-source models free quota

## Domestic Chinese Providers (7 providers)

1. **Baidu Wenxin** (文心一言) - Baidu's flagship Chinese LLM
2. **Tencent Hunyuan** (腾讯混元) - Tencent's Chinese LLM
3. **Baidu BoostGB** - Baidu's specialized model
4. **Ali Tongyi Qianwen** (通义千问) - Alibaba's Chinese LLM
5. **Zhipu AI** (智谱AI) - Zhipu AI's GLM models
6. **MiniMax** (MiniMax) - MiniMax's ABAB models
7. **iFlytek Spark** (讯飞星火) - iFlytek's cognitive model

## Usage Instructions

1. Install Python 3.x if not already installed
2. Install required dependencies:
   ```
   pip install requests
   ```
3. Run the collector:
   ```
   python free_llm_collector.py
   ```
4. Check generated output files:
   - `free_llm_providers.json` - structured data
   - `free_llm_providers.md` - human-readable documentation

## Features

- Complete provider information including:
  - Registration URLs
  - Registration steps (in Chinese)
  - Base URLs for API access
  - Supported models
  - Rate limits and quotas
  - Regional classification

- Comprehensive coverage:
  - 20 international providers
  - 7 domestic Chinese providers
  - Total: 27 providers

## Additional Notes

- Each provider includes detailed registration steps
- Rate limits are regularly updated
- Some providers may have waitlists for free quotas
- Registration typically requires email verification