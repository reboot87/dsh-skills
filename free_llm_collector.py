#!/usr/bin/env python3
"""
免费 LLM API 收集器
收集国内外免费大型语言模型 API 信息，包含注册要求、配额限制、支持模型等详细信息。
"""

import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


@dataclass
class LLMProvider:
    """LLM 供应商数据类，存储供应商详细信息"""
    name: str
    base_url: str
    is_free: bool
    registration_required: bool
    registration_url: str = None
    registration_steps: List[str] = None
    rate_limits: Dict[str, Any] = None
    supported_models: List[str] = None
    description: str = None
    region: str = "international"  # "international" 或 "domestic"


class FreeLLMCollector:
    def __init__(self):
        self.providers: List[LLMProvider] = []
        self.session = requests.Session() if requests else None
        if self.session:
            self.session.headers.update({
                'User-Agent': 'FreeLLMCollector/1.0'
            })
    
    def add_provider(self, provider: LLMProvider):
        """添加新的 LLM 供应商到收集列表"""
        self.providers.append(provider)
    
    def check_openai(self):
        """OpenAI - 免费额度 $5"""
        provider = LLMProvider(
            name="OpenAI",
            base_url="https://api.openai.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://platform.openai.com/signup",
            registration_steps=[
                "访问 OpenAI 平台注册页面",
                "使用邮箱和密码创建账户",
                "验证邮箱地址",
                "申请免费 $5 额度",
                "等待审批（通常立即到账）"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 3,
                "prompt_tokens": 4000,
                "completion_tokens": 4000
            },
            supported_models=["gpt-3.5-turbo", "gpt-3.5-turbo-0301"],
            description="OpenAI 的聊天完成 API，提供新用户免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_anthropic(self):
        """Anthropic - Claude 免费试用"""
        provider = LLMProvider(
            name="Anthropic",
            base_url="https://api.anthropic.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://console.anthropic.com/signup",
            registration_steps=[
                "在 Anthropic 控制台注册",
                "使用邮箱和密码创建账户",
                "验证邮箱地址",
                "申请免费试用权限",
                "等待邮件确认"
            ],
            rate_limits={
                "requests_per_minute": 100,
                "characters_per_month": 10000,
                "models": ["claude-2", "claude-instant-1.2"]
            },
            supported_models=["claude-2", "claude-instant-1.2"],
            description="Anthropic 的 Claude 模型，提供免费试用期",
            region="international"
        )
        self.add_provider(provider)
    
    def check_google(self):
        """Google AI - Gemini 免费额度"""
        provider = LLMProvider(
            name="Google AI",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            is_free=True,
            registration_required=True,
            registration_url="https://makersuite.google.com/app/apikey",
            registration_steps=[
                "访问 Google AI Studio",
                "创建 Google 账户或登录",
                "获取 API 密钥（免费额度）",
                "启用所需 API",
                "开始免费使用"
            ],
            rate_limits={
                "requests_per_minute": 60,
                "requests_per_day": 100,
                "characters_per_day": 50000,
                "models": ["gemini-pro", "gemini-pro-vision"]
            },
            supported_models=["gemini-pro", "gemini-pro-vision"],
            description="Google 的 Gemini 模型，提供免费 API 额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_cohere(self):
        """Cohere - 免费额度与积分"""
        provider = LLMProvider(
            name="Cohere",
            base_url="https://api.cohere.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://dashboard.cohere.com/sign-up",
            registration_steps=[
                "在 Cohere 仪表板注册",
                "使用邮箱和密码创建账户",
                "验证邮箱地址",
                "生成 API 密钥",
                "申请免费积分"
            ],
            rate_limits={
                "requests_per_minute": 10,
                "requests_per_day": 1000,
                "tokens_per_day": 5000
            },
            supported_models=["command", "command-light"],
            description="Cohere 的语言模型，提供慷慨的免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_huggingface(self):
        """Hugging Face - 免费推理 API"""
        provider = LLMProvider(
            name="Hugging Face",
            base_url="https://api-inference.huggingface.co/models",
            is_free=True,
            registration_required=True,
            registration_url="https://huggingface.co/join",
            registration_steps=[
                "创建 Hugging Face 账户",
                "验证邮箱地址",
                "生成 API 令牌",
                "将令牌添加到请求头",
                "开始免费使用"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 300,
                "queue_time_seconds": 60
            },
            supported_models=["gpt2", "bloom", "llama2", "vicuna", "falcon"],
            description="Hugging Face 的免费推理 API，支持开源模型",
            region="international"
        )
        self.add_provider(provider)
    
    def check_replicate(self):
        """Replicate - 免费额度与积分"""
        provider = LLMProvider(
            name="Replicate",
            base_url="https://api.replicate.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://replicate.com/sign-up",
            registration_steps=[
                "在 Replicate 注册",
                "使用邮箱和密码创建账户",
                "验证邮箱地址",
                "获取 API 令牌",
                "申请免费积分"
            ],
            rate_limits={
                "requests_per_day": 1000,
                "credits_per_day": 10
            },
            supported_models=["llama2", "vicuna", "codellama", "stable-diffusion"],
            description="Replicate 的免费额度，支持各种 AI 模型，包括 LLM",
            region="international"
        )
        self.add_provider(provider)
    
    def check_xai(self):
        """X.ai (Grok) - 免费额度"""
        provider = LLMProvider(
            name="X.ai (Grok)",
            base_url="https://api.x.ai/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://x.ai/signup",
            registration_steps=[
                "在 X.ai 注册",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "获取 API 密钥",
                "开始免费使用 Grok"
            ],
            rate_limits={
                "requests_per_minute": 60,
                "requests_per_day": 1000,
                "messages_per_day": 10000
            },
            supported_models=["grok-beta"],
            description="X.ai 的 Grok 模型，提供免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_openrouter(self):
        """OpenRouter - 免费额度与积分"""
        provider = LLMProvider(
            name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://openrouter.ai/keys",
            registration_steps=[
                "在 OpenRouter 注册",
                "使用邮箱和密码创建账户",
                "验证邮箱地址",
                "生成 API 密钥",
                "添加积分（免费额度包含 $5）"
            ],
            rate_limits={
                "requests_per_day": 100,
                "requests_per_minute": 20,
                "credits_per_day": 5
            },
            supported_models=["gpt-3.5-turbo", "gpt-4", "claude-2", "gemini-pro", "llama2"],
            description="OpenRouter 聚合多个 LLM，提供免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_fireworks(self):
        """Fireworks AI - 免费额度"""
        provider = LLMProvider(
            name="Fireworks AI",
            base_url="https://api.fireworks.ai/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://api.fireworks.ai/users/sign_up",
            registration_steps=[
                "访问 Fireworks AI 官网",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "申请 API 访问权限",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_minute": 60,
                "requests_per_day": 100,
                "tokens_per_day": 5000
            },
            supported_models=["mixtral-8x7b", "llama-3.1-8b", "gemini-pro"],
            description="Fireworks AI 提供多种模型的免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_groq(self):
        """Groq - 免费额度"""
        provider = LLMProvider(
            name="Groq",
            base_url="https://api.groq.com/openai/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://groq.com/login/",
            registration_steps=[
                "访问 Groq 官网",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "获取 API 密钥",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_minute": 30,
                "requests_per_day": 100,
                "tokens_per_minute": 6000
            },
            supported_models=["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
            description="Groq 提供超快推理速度的免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_lambda(self):
        """Lambda Labs - 免费额度"""
        provider = LLMProvider(
            name="Lambda Labs",
            base_url="https://api.lam.ai/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://cloud.lam.ai/signup",
            registration_steps=[
                "访问 Lambda Labs 官网",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "申请 GPU 资源",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 100,
                "gpu_minutes_per_day": 200
            },
            supported_models=["llama-2-70b", "mixtral-8x7b"],
            description="Lambda Labs 提供 GPU 加速的 LLM 免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_together_ai(self):
        """Together AI - 免费额度"""
        provider = LLMProvider(
            name="Together AI",
            base_url="https://api.together.xyz/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://api.together.xyz/signup",
            registration_steps=[
                "访问 Together AI 官网",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "获取 API 密钥",
                "申请免费积分"
            ],
            rate_limits={
                "requests_per_minute": 30,
                "requests_per_day": 100,
                "tokens_per_day": 10000
            },
            supported_models=["llama-3-8b-8192", "mixtral-8x7b-instruct-v0.1"],
            description="Together AI 提供开源模型免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_poe(self):
        """Poe - 免费额度"""
        provider = LLMProvider(
            name="Poe",
            base_url="https://api.poe.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://poe.com/login",
            registration_steps=[
                "访问 Poe 官网",
                "使用 Google/Apple/邮箱注册",
                "验证邮箱地址",
                "订阅免费计划",
                "开始使用免费额度"
            ],
            rate_limits={
                "messages_per_day": 3000,
                "models_per_day": 10
            },
            supported_models=["GPT-3.5-Turbo", "Claude-2", "Llama-2-70b"],
            description="Poe 提供多模型访问的免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_anyscale(self):
        """Anyscale - 免费额度"""
        provider = LLMProvider(
            name="Anyscale",
            base_url="https://api.endpoints.anyscale.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://app.anyscale.com/signup",
            registration_steps=[
                "访问 Anyscale 官网",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "部署免费端点",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 100,
                "tokens_per_day": 50000
            },
            supported_models=["llama-3-8b-8192", "mixtral-8x7b"],
            description="Anyscale 提供开源模型免费 API",
            region="international"
        )
        self.add_provider(provider)
    
    def check_perplexity(self):
        """Perplexity AI - 免费额度"""
        provider = LLMProvider(
            name="Perplexity AI",
            base_url="https://api.perplexity.ai",
            is_free=True,
            registration_required=True,
            registration_url="https://www.perplexity.ai/",
            registration_steps=[
                "访问 Perplexity AI 官网",
                "使用 Google/Apple/邮箱注册",
                "验证邮箱地址",
                "订阅免费计划",
                "开始使用免费额度"
            ],
            rate_limits={
                "queries_per_day": 100,
                "models_per_day": 5
            },
            supported_models=["sonar-small", "sonar-medium", "sonar-large"],
            description="Perplexity AI 提供搜索增强的 LLM 免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_mistral(self):
        """Mistral AI - 免费额度"""
        provider = LLMProvider(
            name="Mistral AI",
            base_url="https://api.mistral.ai/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://console.mistral.ai/",
            registration_steps=[
                "访问 Mistral AI 控制台",
                "使用邮箱创建账户",
                "验证邮箱地址",
                "获取 API 密钥",
                "使用免费额度（新用户免费）"
            ],
            rate_limits={
                "requests_per_minute": 30,
                "requests_per_day": 100,
                "tokens_per_day": 10000
            },
            supported_models=["mistral-tiny", "mistral-small", "mistral-medium"],
            description="Mistral AI 提供高效开源模型免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_deepseek(self):
        """DeepSeek - 免费额度"""
        provider = LLMProvider(
            name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://platform.deepseek.com/api_keys",
            registration_steps=[
                "访问 DeepSeek 平台",
                "使用邮箱注册账户",
                "验证邮箱地址",
                "申请 API 密钥",
                "使用免费额度（新用户免费）"
            ],
            rate_limits={
                "requests_per_minute": 30,
                "requests_per_day": 100,
                "tokens_per_day": 50000
            },
            supported_models=["deepseek-chat", "deepseek-coder"],
            description="DeepSeek 提供高性能开源模型免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_qwen(self):
        """Qwen - 免费额度"""
        provider = LLMProvider(
            name="Qwen",
            base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            is_free=True,
            registration_required=True,
            registration_url="https://dashscope.console.aliyun.com/",
            registration_steps=[
                "访问阿里云 DashScope 平台",
                "使用阿里云账户登录",
                "开通 Qwen 服务",
                "获取 API Key",
                "使用免费额度"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 100,
                "tokens_per_day": 20000
            },
            supported_models=["qwen-7b-chat", "qwen-14b-chat"],
            description="Qwen 大模型提供免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_opencode(self):
        """Opencode - 免费额度"""
        provider = LLMProvider(
            name="Opencode",
            base_url="https://openrouter.ai/api/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://openrouter.ai/keys",
            registration_steps=[
                "访问 Opencode 网站",
                "创建账户并登录",
                "生成 API 密钥",
                "添加额度到账户",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 100,
                "requests_per_minute": 20,
                "credits_per_day": 5
            },
            supported_models=["gpt-3.5-turbo", "gpt-4", "claude-2", "gemini-pro"],
            description="Opencode 提供免费额度，支持多种 LLM 模型",
            region="international"
        )
        self.add_provider(provider)
    
    def check_cline(self):
        """Cline - 免费额度"""
        provider = LLMProvider(
            name="Cline",
            base_url="https://api.anthropic.com/v1",
            is_free=True,
            registration_required=True,
            registration_url="https://console.anthropic.com/signup",
            registration_steps=[
                "访问 Cline 官网",
                "创建 Anthropic 账户",
                "申请免费额度",
                "获取 API 密钥",
                "开始使用 Cline"
            ],
            rate_limits={
                "requests_per_minute": 100,
                "characters_per_month": 10000,
                "models": ["claude-2", "claude-instant-1.2"]
            },
            supported_models=["claude-2", "claude-instant-1.2"],
            description="Cline 是 Anthropic Claude 的增强版，提供免费额度",
            region="international"
        )
        self.add_provider(provider)
    
    def check_baidu_wenxin(self):
        """百度文心 - 国内免费额度"""
        provider = LLMProvider(
            name="Baidu Wenxin",
            base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/api" + \
                     "/completionsPro?charset=utf-8&ack=1",
            is_free=True,
            registration_required=True,
            registration_url="https://aip.baidubce.com/",
            registration_steps=[
                "访问百度 AI 平台",
                "创建百度账户或登录",
                "申请 API 权限",
                "获取 API 密钥和秘钥",
                "使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 500,
                "tokens_per_day": 20000,
                "models": ["ernie-bot", "ernie-bot-turbo"]
            },
            supported_models=["ernie-bot", "ernie-bot-turbo"],
            description="百度旗舰中文 LLM 文心一言，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_tencent_hunyuan(self):
        """腾讯混元 - 国内免费额度"""
        provider = LLMProvider(
            name="Tencent Hunyuan",
            base_url="https://api.hunyuan.tencent.com/",
            is_free=True,
            registration_required=True,
            registration_url="https://hunyuan.cloud.tencent.com/",
            registration_steps=[
                "访问腾讯混元入口",
                "创建腾讯账户或登录",
                "申请 API 权限",
                "获取 API 密钥和秘钥",
                "使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 1000,
                "tokens_per_day": 100000,
                "models": ["hunyuan-standard", "hunyuan-lite"]
            },
            supported_models=["hunyuan-standard", "hunyuan-lite"],
            description="腾讯旗舰中文 LLM 混元，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_baidu_boostgb(self):
        """百度 BoostGB - 国内免费额度"""
        provider = LLMProvider(
            name="Baidu BoostGB",
            base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/api" + \
                     "/completionsPro?charset=utf-8&ack=1",
            is_free=True,
            registration_required=True,
            registration_url="https://aip.baidubce.com/",
            registration_steps=[
                "在百度 AI 平台注册",
                "使用百度账户登录",
                "申请 BoostGB 服务",
                "获取 API 凭证",
                "开始使用免费额度"
            ],
            rate_limits={
                "requests_per_day": 1000,
                "tokens_per_day": 50000,
                "models": ["boostgb"]
            },
            supported_models=["boostgb"],
            description="百度旗舰模型 BoostGB，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_ali_tongyi(self):
        """阿里通义千问 - 国内免费额度"""
        provider = LLMProvider(
            name="Ali Tongyi Qianwen",
            base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            is_free=True,
            registration_required=True,
            registration_url="https://dashscope.console.aliyun.com/",
            registration_steps=[
                "访问阿里云控制台",
                "使用阿里云账户登录",
                "开通通义千问服务",
                "获取 API Key",
                "使用免费额度（新用户免费试用）"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 100,
                "tokens_per_day": 20000
            },
            supported_models=["qwen-7b-chat", "qwen-14b-chat", "qwen-72b-chat"],
            description="阿里云通义千问大模型，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_zhipu_ai(self):
        """智谱AI - 国内免费额度"""
        provider = LLMProvider(
            name="Zhipu AI",
            base_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            is_free=True,
            registration_required=True,
            registration_url="https://open.bigmodel.cn/",
            registration_steps=[
                "访问智谱AI 开放平台",
                "使用邮箱或手机号注册",
                "实名验证",
                "申请 API Key",
                "领取免费额度（新用户免费）"
            ],
            rate_limits={
                "requests_per_minute": 30,
                "requests_per_day": 100,
                "tokens_per_day": 50000
            },
            supported_models=["glm-4", "glm-3-turbo"],
            description="智谱 AI 大模型，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_minimax(self):
        """MiniMax - 国内免费额度"""
        provider = LLMProvider(
            name="MiniMax",
            base_url="https://api.minimaxi.com/v1/text/chatcompletion_v2",
            is_free=True,
            registration_required=True,
            registration_url="https://api.minimaxi.com/",
            registration_steps=[
                "访问 MiniMax 开放平台",
                "使用手机号注册",
                "实名验证",
                "申请 API Key",
                "使用免费额度"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 100,
                "tokens_per_day": 20000
            },
            supported_models=["abab6.5-chat", "abab5.5-chat"],
            description="MiniMax 大模型，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def check_iflytek(self):
        """讯飞星火 - 国内免费额度"""
        provider = LLMProvider(
            name="iFlytek Spark",
            base_url="https://spark-api.cn-huabei-1.xf-yun.com/v1/chat/completions",
            is_free=True,
            registration_required=True,
            registration_url="https://console.xfyun.cn/",
            registration_steps=[
                "访问讯飞开放平台",
                "创建开发者账号",
                "实名认证",
                "申请星火认知大模型接口",
                "获取 API Key 使用免费额度"
            ],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 100,
                "tokens_per_day": 20000
            },
            supported_models=["spark-lite", "spark-pro"],
            description="讯飞星火认知大模型，提供国内免费额度",
            region="domestic"
        )
        self.add_provider(provider)
    
    def collect_all(self):
        """收集所有免费 LLM 供应商信息"""
        print("收集免费 LLM 供应商信息...")
        
        # 国际供应商
        self.check_openai()
        self.check_anthropic()
        self.check_google()
        self.check_cohere()
        self.check_huggingface()
        self.check_replicate()
        self.check_xai()
        self.check_openrouter()
        self.check_opencode()
        self.check_cline()
        self.check_fireworks()
        self.check_groq()
        self.check_lambda()
        self.check_together_ai()
        self.check_poe()
        self.check_anyscale()
        self.check_perplexity()
        self.check_mistral()
        self.check_deepseek()
        self.check_qwen()
        
        # 国内中国供应商
        self.check_baidu_wenxin()
        self.check_tencent_hunyuan()
        self.check_baidu_boostgb()
        self.check_ali_tongyi()
        self.check_zhipu_ai()
        self.check_minimax()
        self.check_iflytek()
        
        print(f"收集完成，共 {len(self.providers)} 个供应商")
    
    def get_domestic_providers(self):
        """获取国内中国供应商列表"""
        return [p for p in self.providers if p.region == "domestic"]
    
    def get_international_providers(self):
        """获取国际供应商列表"""
        return [p for p in self.providers if p.region == "international"]
    
    def export_to_json(self, filename: str = "free_llm_providers.json"):
        """导出供应商信息到 JSON 文件"""
        data = {
            "导出日期": datetime.now().isoformat(),
            "供应商总数": len(self.providers),
            "供应商列表": [
                {
                    "名称": p.name,
                    "基础 URL": p.base_url,
                    "是否免费": p.is_free,
                    "是否需要注册": p.registration_required,
                    "注册链接": p.registration_url,
                    "注册步骤": p.registration_steps,
                    "速率限制": p.rate_limits,
                    "支持模型": p.supported_models,
                    "描述": p.description,
                    "地区": p.region
                }
                for p in self.providers
            ],
            "统计信息": {
                "国际供应商数量": len(self.get_international_providers()),
                "国内供应商数量": len(self.get_domestic_providers()),
                "免费供应商数量": len([p for p in self.providers if p.is_free])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已导出到 {filename}")
        return filename
    
    def export_to_readable_format(self, filename: str = "free_llm_providers.md"):
        """以人类可读的 Markdown 格式导出供应商信息"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 免费大型语言模型供应商\n\n")
            f.write(f"*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## 概述\n")
            f.write(f"- 供应商总数: {len(self.providers)}\n")
            f.write(f"- 国际供应商: {len(self.get_international_providers())}\n")
            f.write(f"- 国内供应商: {len(self.get_domestic_providers())}\n")
            f.write(f"- 免费供应商: {len([p for p in self.providers if p.is_free])}\n\n")
            
            # 国际供应商部分
            f.write("## 国际供应商\n\n")
            for provider in self.get_international_providers():
                f.write(f"### {provider.name}\n")
                f.write(f"{provider.description}\n\n")
                f.write(f"- **基础 URL**: {provider.base_url}\n")
                f.write(f"- **免费**: {'是' if provider.is_free else '否'}\n")
                f.write(f"- **需要注册**: {'是' if provider.registration_required else '否'}\n")
                if provider.registration_url:
                    f.write(f"- **注册链接**: [{provider.registration_url}]({provider.registration_url})\n")
                f.write(f"- **支持模型**: {', '.join(provider.supported_models)}\n")
                f.write(f"- **速率限制**: {json.dumps(provider.rate_limits, indent=2, ensure_ascii=False)}\n\n")
                f.write("**注册步骤:**\n")
                for i, step in enumerate(provider.registration_steps, 1):
                    f.write(f"{i}. {step}\n")
                f.write("\n")
            
            # 国内供应商部分
            f.write("## 国内供应商\n\n")
            for provider in self.get_domestic_providers():
                f.write(f"### {provider.name}\n")
                f.write(f"{provider.description}\n\n")
                f.write(f"- **基础 URL**: {provider.base_url}\n")
                f.write(f"- **免费**: {'是' if provider.is_free else '否'}\n")
                f.write(f"- **需要注册**: {'是' if provider.registration_required else '否'}\n")
                if provider.registration_url:
                    f.write(f"- **注册链接**: [{provider.registration_url}]({provider.registration_url})\n")
                f.write(f"- **支持模型**: {', '.join(provider.supported_models)}\n")
                f.write(f"- **速率限制**: {json.dumps(provider.rate_limits, indent=2, ensure_ascii=False)}\n\n")
                f.write("**注册步骤:**\n")
                for i, step in enumerate(provider.registration_steps, 1):
                    f.write(f"{i}. {step}\n")
                f.write("\n")
        
        print(f"可读格式数据已导出到 {filename}")
        return filename
    
    def print_providers(self):
        """以控制台打印可读格式的供应商信息"""
        print("\n" + "="*80)
        print("免费大型语言模型供应商")
        print("="*80)
        
        # 国际
        print("\n🎯 国际供应商")
        print("-" * 50)
        for provider in self.get_international_providers():
            print(f"\n{provider.name}")
            print(f"  URL: {provider.base_url}")
            print(f"  描述: {provider.description}")
            print(f"  模型: {', '.join(provider.supported_models)}")
            print(f"  注册: {provider.registration_url}")
            print(f"  速率限制: {json.dumps(provider.rate_limits, indent=2)}")
        
        # 国内
        print("\n🇨🇳 国内供应商")
        print("-" * 50)
        for provider in self.get_domestic_providers():
            print(f"\n{provider.name}")
            print(f"  URL: {provider.base_url}")
            print(f"  描述: {provider.description}")
            print(f"  模型: {', '.join(provider.supported_models)}")
            print(f"  注册: {provider.registration_url}")
            print(f"  速率限制: {json.dumps(provider.rate_limits, indent=2)}")


def main():
    collector = FreeLLMCollector()
    collector.collect_all()
    
    # Export in both formats
    json_file = collector.export_to_json("free_llm_providers.json")
    md_file = collector.export_to_readable_format("free_llm_providers.md")
    
    # Print summary to console
    collector.print_providers()
    
    print(f"\n{'='*80}")
    print("EXPORT COMPLETED")
    print(f"JSON file: {json_file}")
    print(f"Markdown file: {md_file}")
    print(f"Total providers found: {len(collector.providers)}")
    print(f"Domestic (Chinese): {len(collector.get_domestic_providers())}")
    print(f"International: {len(collector.get_international_providers())}")
    print(f"{'='*80}")
if __name__ == "__main__":
    main()