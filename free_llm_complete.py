#!/usr/bin/env python3
"""
免费 LLM API 收集器与自动注册器
Free LLM API Collector and Auto-Registration System

本模块提供：
1. 收集国内外免费 LLM API 信息（基础 URL、注册要求、配额限制）
2. 自动注册流程引导（支持 Selenium 浏览器自动化）
3. API 密钥管理与保存
4. 多种导出格式（JSON, Markdown, TXT）
"""

import json
import time
import os
import re
import getpass
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Optional dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("提示: 安装 selenium 以启用自动注册功能: pip install selenium")


@dataclass
class Credential:
    """存储凭据信息"""
    provider: str
    api_key: str = ""
    username: str = ""
    password: str = ""
    email: str = ""
    registration_date: str = ""
    notes: str = ""


@dataclass
class RegistrationResult:
    """注册结果"""
    success: bool
    provider: str
    api_key: str = ""
    message: str = ""
    details: Dict = None


class FreeLLMCollector:
    """免费 LLM 收集器"""
    
    def __init__(self):
        self.providers: List[Dict] = []
        self._collect_all()
    
    def _collect_all(self):
        """收集所有免费 LLM 供应商信息"""
        providers = [
            self._create_provider("OpenAI", "https://api.openai.com/v1", "OpenAI 的聊天完成 API，提供新用户免费额度", 
                                 ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"], 
                                 {"requests_per_minute": 20, "requests_per_day": 3},
                                 "https://platform.openai.com/signup", "international"),
            self._create_provider("Anthropic", "https://api.anthropic.com/v1", "Anthropic 的 Claude 模型，提供免费试用期",
                                 ["claude-2", "claude-instant-1.2"],
                                 {"requests_per_minute": 100, "characters_per_month": 10000},
                                 "https://console.anthropic.com/signup", "international"),
            self._create_provider("Google AI", "https://generativelanguage.googleapis.com/v1beta", "Google 的 Gemini 模型，提供免费 API 额度",
                                 ["gemini-pro", "gemini-pro-vision"],
                                 {"requests_per_minute": 60, "requests_per_day": 100},
                                 "https://makersuite.google.com/app/apikey", "international"),
            self._create_provider("Cohere", "https://api.cohere.com/v1", "Cohere 的语言模型，提供慷慨的免费额度",
                                 ["command", "command-light"],
                                 {"requests_per_minute": 10, "requests_per_day": 1000},
                                 "https://dashboard.cohere.com/sign-up", "international"),
            self._create_provider("Hugging Face", "https://api-inference.huggingface.co/models", "Hugging Face 的免费推理 API，支持开源模型",
                                 ["gpt2", "bloom", "llama2", "vicuna", "falcon"],
                                 {"requests_per_minute": 20, "requests_per_day": 300},
                                 "https://huggingface.co/join", "international"),
            self._create_provider("Replicate", "https://api.replicate.com/v1", "Replicate 的免费额度，支持各种 AI 模型，包括 LLM",
                                 ["llama2", "vicuna", "codellama", "stable-diffusion"],
                                 {"requests_per_day": 1000, "credits_per_day": 10},
                                 "https://replicate.com/sign-up", "international"),
            self._create_provider("X.ai (Grok)", "https://api.x.ai/v1", "X.ai 的 Grok 模型，提供免费额度",
                                 ["grok-beta"],
                                 {"requests_per_minute": 60, "requests_per_day": 1000},
                                 "https://x.ai/signup", "international"),
            self._create_provider("OpenRouter", "https://openrouter.ai/api/v1", "OpenRouter 聚合多个 LLM，提供免费额度",
                                 ["gpt-3.5-turbo", "gpt-4", "claude-2", "gemini-pro", "llama2"],
                                 {"requests_per_day": 100, "requests_per_minute": 20, "credits_per_day": 5},
                                 "https://openrouter.ai/keys", "international"),
            self._create_provider("Opencode", "https://openrouter.ai/api/v1", "Opencode 提供免费额度，支持多种 LLM 模型",
                                 ["gpt-3.5-turbo", "gpt-4", "claude-2", "gemini-pro"],
                                 {"requests_per_day": 100, "requests_per_minute": 20, "credits_per_day": 5},
                                 "https://openrouter.ai/keys", "international"),
            self._create_provider("Cline", "https://api.anthropic.com/v1", "Cline 是 Anthropic Claude 的增强版，提供免费额度",
                                 ["claude-2", "claude-instant-1.2"],
                                 {"requests_per_minute": 100, "characters_per_month": 10000},
                                 "https://console.anthropic.com/signup", "international"),
            self._create_provider("Fireworks AI", "https://api.fireworks.ai/v1", "Fireworks AI 提供多种模型的免费额度",
                                 ["mixtral-8x7b", "llama-3.1-8b", "gemini-pro"],
                                 {"requests_per_minute": 60, "requests_per_day": 100},
                                 "https://api.fireworks.ai/users/sign_up", "international"),
            self._create_provider("Groq", "https://api.groq.com/openai/v1", "Groq 提供超快推理速度的免费额度",
                                 ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://groq.com/login/", "international"),
            self._create_provider("Lambda Labs", "https://api.lam.ai/v1", "Lambda Labs 提供 GPU 加速的 LLM 免费额度",
                                 ["llama-2-70b", "mixtral-8x7b"],
                                 {"requests_per_day": 100, "gpu_minutes_per_day": 200},
                                 "https://cloud.lam.ai/signup", "international"),
            self._create_provider("Together AI", "https://api.together.xyz/v1", "Together AI 提供开源模型免费额度",
                                 ["llama-3-8b-8192", "mixtral-8x7b-instruct-v0.1"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://api.together.xyz/signup", "international"),
            self._create_provider("Poe", "https://api.poe.com/v1", "Poe 提供多模型访问的免费额度",
                                 ["GPT-3.5-Turbo", "Claude-2", "Llama-2-70b"],
                                 {"messages_per_day": 3000, "models_per_day": 10},
                                 "https://poe.com/login", "international"),
            self._create_provider("Anyscale", "https://api.endpoints.anyscale.com/v1", "Anyscale 提供开源模型免费 API",
                                 ["llama-3-8b-8192", "mixtral-8x7b"],
                                 {"requests_per_day": 100, "tokens_per_day": 50000},
                                 "https://app.anyscale.com/signup", "international"),
            self._create_provider("Perplexity AI", "https://api.perplexity.ai", "Perplexity AI 提供搜索增强的 LLM 免费额度",
                                 ["sonar-small", "sonar-medium", "sonar-large"],
                                 {"queries_per_day": 100, "models_per_day": 5},
                                 "https://www.perplexity.ai/", "international"),
            self._create_provider("Mistral AI", "https://api.mistral.ai/v1", "Mistral AI 提供高效开源模型免费额度",
                                 ["mistral-tiny", "mistral-small", "mistral-medium"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://console.mistral.ai/", "international"),
            self._create_provider("DeepSeek", "https://api.deepseek.com/v1", "DeepSeek 提供高性能开源模型免费额度",
                                 ["deepseek-chat", "deepseek-coder"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://platform.deepseek.com/api_keys", "international"),
            self._create_provider("Qwen", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation", "Qwen 大模型提供免费额度",
                                 ["qwen-7b-chat", "qwen-14b-chat"],
                                 {"requests_per_minute": 20, "requests_per_day": 100},
                                 "https://dashscope.console.aliyun.com/", "international"),
            # 国内供应商
            self._create_provider("百度文心", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/api/completionsPro?charset=utf-8&ack=1", 
                                 "百度旗舰中文 LLM 文心一言，提供国内免费额度",
                                 ["ernie-bot", "ernie-bot-turbo"],
                                 {"requests_per_day": 500, "tokens_per_day": 20000},
                                 "https://aip.baidubce.com/", "domestic"),
            self._create_provider("腾讯混元", "https://api.hunyuan.tencent.com/", "腾讯旗舰中文 LLM 混元，提供国内免费额度",
                                 ["hunyuan-standard", "hunyuan-lite"],
                                 {"requests_per_day": 1000, "tokens_per_day": 100000},
                                 "https://hunyuan.cloud.tencent.com/", "domestic"),
            self._create_provider("百度 BoostGB", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/api/completionsPro?charset=utf-8&ack=1",
                                 "百度旗舰模型 BoostGB，提供国内免费额度",
                                 ["boostgb"],
                                 {"requests_per_day": 1000, "tokens_per_day": 50000},
                                 "https://aip.baidubce.com/", "domestic"),
            self._create_provider("阿里通义千问", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 "阿里云通义千问大模型，提供国内免费额度",
                                 ["qwen-7b-chat", "qwen-14b-chat", "qwen-72b-chat"],
                                 {"requests_per_minute": 20, "requests_per_day": 100},
                                 "https://dashscope.console.aliyun.com/", "domestic"),
            self._create_provider("智谱AI", "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                                 "智谱 AI 大模型，提供国内免费额度",
                                 ["glm-4", "glm-3-turbo"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://open.bigmodel.cn/", "domestic"),
            self._create_provider("MiniMax", "https://api.minimaxi.com/v1/text/chatcompletion_v2",
                                 "MiniMax 大模型，提供国内免费额度",
                                 ["abab6.5-chat", "abab5.5-chat"],
                                 {"requests_per_minute": 20, "requests_per_day": 100},
                                 "https://api.minimaxi.com/", "domestic"),
            self._create_provider("讯飞星火", "https://spark-api.cn-huabei-1.xf-yun.com/v1/chat/completions",
                                 "讯飞星火认知大模型，提供国内免费额度",
                                 ["spark-lite", "spark-pro"],
                                 {"requests_per_minute": 20, "requests_per_day": 100},
                                 "https://console.xfyun.cn/", "domestic"),
        ]
        
        self.providers = providers
    
    def _create_provider(self, name: str, base_url: str, description: str, 
                        models: List[str], rate_limits: Dict, 
                        registration_url: str, region: str) -> Dict:
        """创建供应商信息字典"""
        return {
            "name": name,
            "base_url": base_url,
            "is_free": True,
            "registration_required": True,
            "registration_url": registration_url,
            "registration_steps": self._get_registration_steps(name, registration_url),
            "rate_limits": rate_limits,
            "supported_models": models,
            "description": description,
            "region": region
        }
    
    def _get_registration_steps(self, name: str, url: str) -> List[str]:
        """获取供应商的注册步骤"""
        steps_map = {
            "openai": ["访问 OpenAI 平台注册页面", "使用邮箱和密码创建账户", "验证邮箱地址", "申请免费额度", "等待审批"],
            "anthropic": ["在 Anthropic 控制台注册", "创建账户", "验证邮箱", "申请免费试用"],
            "google": ["访问 Google AI Studio", "创建 Google 账户或登录", "获取 API 密钥", "启用所需 API", "开始免费使用"],
            "baidu": ["访问百度 AI 平台", "创建百度账户或登录", "申请 API 权限", "获取 API 密钥", "使用免费额度"],
            "tencent": ["访问腾讯混元入口", "创建腾讯账户或登录", "申请 API 权限", "获取 API 密钥", "使用免费额度"],
        }
        
        for key, steps in steps_map.items():
            if key in name.lower() or key in url.lower():
                return steps
        
        return ["访问注册页面", "创建账户", "验证邮箱", "申请 API 权限", "获取 API 密钥"]
    
    def get_international_providers(self) -> List[Dict]:
        """获取国际供应商"""
        return [p for p in self.providers if p["region"] == "international"]
    
    def get_domestic_providers(self) -> List[Dict]:
        """获取国内供应商"""
        return [p for p in self.providers if p["region"] == "domestic"]
    
    def export_to_json(self, filename: str = "free_llm_providers.json"):
        """导出到 JSON 文件"""
        data = {
            "导出日期": datetime.now().isoformat(),
            "供应商总数": len(self.providers),
            "供应商列表": self.providers,
            "统计信息": {
                "国际供应商数量": len(self.get_international_providers()),
                "国内供应商数量": len(self.get_domestic_providers()),
                "免费供应商数量": len([p for p in self.providers if p["is_free"]])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已导出到 {filename}")
        return filename
    
    def export_to_markdown(self, filename: str = "free_llm_providers.md"):
        """导出到 Markdown 文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 免费大型语言模型供应商\n\n")
            f.write(f"*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## 概述\n")
            f.write(f"- 供应商总数: {len(self.providers)}\n")
            f.write(f"- 国际供应商: {len(self.get_international_providers())}\n")
            f.write(f"- 国内供应商: {len(self.get_domestic_providers())}\n\n")
            
            # 国际供应商
            f.write("## 国际供应商\n\n")
            for provider in self.get_international_providers():
                f.write(f"### {provider['name']}\n")
                f.write(f"{provider['description']}\n\n")
                f.write(f"- **基础 URL**: {provider['base_url']}\n")
                f.write(f"- **注册链接**: [{provider['registration_url']}]({provider['registration_url']})\n")
                f.write(f"- **支持模型**: {', '.join(provider['supported_models'])}\n")
                f.write(f"- **速率限制**: {json.dumps(provider['rate_limits'], indent=2, ensure_ascii=False)}\n\n")
            
            # 国内供应商
            f.write("## 国内供应商\n\n")
            for provider in self.get_domestic_providers():
                f.write(f"### {provider['name']}\n")
                f.write(f"{provider['description']}\n\n")
                f.write(f"- **基础 URL**: {provider['base_url']}\n")
                f.write(f"- **注册链接**: [{provider['registration_url']}]({provider['registration_url']})\n")
                f.write(f"- **支持模型**: {', '.join(provider['supported_models'])}\n")
                f.write(f"- **速率限制**: {json.dumps(provider['rate_limits'], indent=2, ensure_ascii=False)}\n\n")
        
        print(f"Markdown 数据已导出到 {filename}")
        return filename


class FreeLLMAutoRegister:
    """LLM 自动注册器"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.credentials: List[Credential] = []
        self.results: List[RegistrationResult] = []
        self.driver = None
        
        # 注册配置
        self.provider_configs = self._get_provider_configs()
    
    def _get_provider_configs(self) -> Dict[str, Dict]:
        """获取所有供应商的注册配置"""
        return {
            "openai": {
                "name": "OpenAI",
                "url": "https://platform.openai.com/signup",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "申请免费额度"],
                "auto_possible": False,  # 需要人工
                "fields": ["email", "password"]
            },
            "anthropic": {
                "name": "Anthropic",
                "url": "https://console.anthropic.com/signup",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "申请试用"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            "google_ai": {
                "name": "Google AI",
                "url": "https://makersuite.google.com/app/apikey",
                "type": "web",
                "steps": ["访问 AI Studio", "登录 Google", "创建 API Key"],
                "auto_possible": True,
                "fields": ["google_email"]
            },
            "huggingface": {
                "name": "Hugging Face",
                "url": "https://huggingface.co/join",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "生成 Token"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "openrouter": {
                "name": "OpenRouter",
                "url": "https://openrouter.ai/keys",
                "type": "web",
                "steps": ["访问密钥页面", "创建账户", "生成 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "opencode": {
                "name": "Opencode",
                "url": "https://openrouter.ai/keys",
                "type": "web",
                "steps": ["访问 OpenRouter", "创建账户", "生成 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "cline": {
                "name": "Cline",
                "url": "https://console.anthropic.com/signup",
                "type": "web",
                "steps": ["访问 Anthropic", "创建账户", "获取 API Key"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            "groq": {
                "name": "Groq",
                "url": "https://groq.com/login/",
                "type": "web",
                "steps": ["访问登录页面", "创建账户", "获取 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "cohere": {
                "name": "Cohere",
                "url": "https://dashboard.cohere.com/sign-up",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "获取 API Key"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            "replicate": {
                "name": "Replicate",
                "url": "https://replicate.com/sign-up",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "获取 Token"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            "deepseek": {
                "name": "DeepSeek",
                "url": "https://platform.deepseek.com/api_keys",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "验证邮箱", "获取 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "mistral": {
                "name": "Mistral AI",
                "url": "https://console.mistral.ai/",
                "type": "web",
                "steps": ["访问控制台", "创建账户", "获取 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "fireworks": {
                "name": "Fireworks AI",
                "url": "https://api.fireworks.ai/users/sign_up",
                "type": "web",
                "steps": ["访问注册页面", "创建账户", "获取 API Key"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            # 国内供应商
            "baidu_wenxin": {
                "name": "百度文心",
                "url": "https://aip.baidubce.com/",
                "type": "web_chinese",
                "steps": ["访问百度 AI 平台", "登录百度账户", "申请 API 权限", "获取密钥"],
                "auto_possible": False,  # 国内通常需要人工
                "fields": ["email", "password"]
            },
            "tencent_hunyuan": {
                "name": "腾讯混元",
                "url": "https://hunyuan.cloud.tencent.com/",
                "type": "web_chinese",
                "steps": ["访问腾讯混元", "登录腾讯账户", "申请 API 权限", "获取密钥"],
                "auto_possible": False,
                "fields": ["email", "password"]
            },
            "ali_tongyi": {
                "name": "阿里通义千问",
                "url": "https://dashscope.console.aliyun.com/",
                "type": "web_chinese",
                "steps": ["访问阿里云控制台", "登录阿里云账户", "开通服务", "获取 API Key"],
                "auto_possible": True,
                "fields": ["aliyun_email", "password"]
            },
            "zhipu_ai": {
                "name": "智谱AI",
                "url": "https://open.bigmodel.cn/",
                "type": "web_chinese",
                "steps": ["访问智谱开放平台", "注册账户", "实名认证", "获取 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            },
            "minimax": {
                "name": "MiniMax",
                "url": "https://api.minimaxi.com/",
                "type": "web_chinese",
                "steps": ["访问 MiniMax 平台", "手机号注册", "实名认证", "获取 API Key"],
                "auto_possible": True,
                "fields": ["phone", "password"]
            },
            "iflytek": {
                "name": "讯飞星火",
                "url": "https://console.xfyun.cn/",
                "type": "web_chinese",
                "steps": ["访问讯飞开放平台", "创建开发者账号", "实名认证", "获取 API Key"],
                "auto_possible": True,
                "fields": ["email", "password"]
            }
        }
    
    def register_provider(self, provider_key: str) -> RegistrationResult:
        """尝试自动注册指定供应商"""
        if provider_key not in self.provider_configs:
            return RegistrationResult(
                success=False,
                provider=provider_key,
                message="未知的供应商配置"
            )
        
        config = self.provider_configs[provider_key]
        result = RegistrationResult(
            success=False,
            provider=config["name"]
        )
        
        try:
            # 检查是否支持自动化
            if not config["auto_possible"]:
                result.message = f"{config['name']} 注册需要人工验证，请手动访问: {config['url']}"
                result.details = {"url": config["url"], "steps": config["steps"]}
                return result
            
            # 尝试自动注册
            if SELENIUM_AVAILABLE:
                self._auto_register(provider_key, config, result)
            else:
                result.message = f"Selenium 未安装，无法自动注册 {config['name']}。请安装: pip install selenium"
                result.details = {"url": config["url"], "steps": config["steps"]}
        
        except Exception as e:
            result.message = f"注册过程出错: {str(e)}"
        
        return result
    
    def _auto_register(self, provider_key: str, config: Dict, result: RegistrationResult):
        """自动注册流程"""
        try:
            # 配置浏览器
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 尝试启动浏览器
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                result.message = f"无法启动浏览器: {str(e)}\n请手动访问: {config['url']}"
                return
            
            try:
                # 访问注册页面
                self.driver.get(config["url"])
                time.sleep(3)
                
                # 根据注册步骤进行操作
                for step in config["steps"]:
                    if "访问" in step:
                        # 已通过 driver.get 访问
                        continue
                    elif "创建账户" in step or "创建" in step:
                        try:
                            sign_up_btn = self.driver.find_element(
                                By.XPATH, 
                                "//button[contains(text(), 'Sign up') or contains(text(), 'Register') or contains(text(), '创建') or contains(text(), '注册')]"
                            )
                            sign_up_btn.click()
                            time.sleep(2)
                        except:
                            pass
                    
                    elif "验证邮箱" in step or "验证" in step:
                        result.message = f"{config['name']} 需要邮箱验证，请完成后继续"
                        break
                    
                    elif "获取 API Key" in step or "获取" in step:
                        try:
                            create_key_btn = self.driver.find_element(
                                By.XPATH,
                                "//button[contains(text(), 'Create') or contains(text(), '创建') or contains(text(), 'Generate') or contains(text(), '生成')]"
                            )
                            create_key_btn.click()
                            time.sleep(2)
                            
                            # 尝试提取 API Key
                            page_source = self.driver.page_source
                            api_key_match = re.search(r'(sk-|api-)[a-zA-Z0-9]{20,}', page_source)
                            if api_key_match:
                                result.api_key = api_key_match.group(0)
                                result.success = True
                                result.message = f"成功获取 {config['name']} API Key"
                        except:
                            result.message = f"无法自动获取 API Key，请手动访问: {config['url']}"
                
                if not result.api_key:
                    result.message = f"注册流程完成，请手动访问: {config['url']} 获取 API Key"
                
            finally:
                if self.driver:
                    self.driver.quit()
        
        except Exception as e:
            result.message = f"自动注册出错: {str(e)}"
    
    def save_credentials(self, filename: str = "llm_credentials.json"):
        """保存凭据到文件"""
        credentials_data = [asdict(cred) for cred in self.credentials]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(credentials_data, f, ensure_ascii=False, indent=2)
        
        print(f"凭据已保存到: {filename}")
        return filename
    
    def save_api_keys(self, filename: str = "api_keys.txt"):
        """保存 API Key 到文本文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# LLM API 密钥列表\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# 请妥善保管以下 API 密钥，不要泄露\n\n")
            
            for cred in self.credentials:
                if cred.api_key:
                    f.write(f"[{cred.provider}]\n")
                    f.write(f"API_KEY={cred.api_key}\n")
                    if cred.username:
                        f.write(f"USERNAME={cred.username}\n")
                    if cred.email:
                        f.write(f"EMAIL={cred.email}\n")
                    f.write("\n")
        
        print(f"API 密钥已保存到: {filename}")
        return filename
    
    def add_credential_manually(self):
        """手动添加凭据"""
        print("\n" + "="*50)
        print("手动添加 API 凭据")
        print("="*50)
        
        provider = input("供应商名称: ").strip()
        api_key = getpass.getpass("API 密钥: ").strip()
        username = input("用户名 (选填): ").strip()
        email = input("邮箱 (选填): ").strip()
        notes = input("备注 (选填): ").strip()
        
        cred = Credential(
            provider=provider,
            api_key=api_key,
            username=username if username else "",
            password="",
            email=email if email else "",
            registration_date=datetime.now().isoformat(),
            notes=notes
        )
        
        self.credentials.append(cred)
        print(f"✅ 成功添加 {provider} 的凭据")
        return cred


def main():
    """主函数"""
    print("=" * 60)
    print("欢迎使用免费 LLM API 收集器与自动注册器")
    print("=" * 60)
    print()
    print("请选择操作模式:")
    print("1. 收集免费 LLM API 信息")
    print("2. 自动注册并获取 API Key")
    print("3. 手动添加 API 凭据")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        # 收集信息
        print("\n正在收集免费 LLM API 信息...")
        collector = FreeLLMCollector()
        collector.export_to_json()
        collector.export_to_markdown()
        print("\n" + "="*60)
        print("收集完成！")
        print(f"国际供应商: {len(collector.get_international_providers())} 个")
        print(f"国内供应商: {len(collector.get_domestic_providers())} 个")
        print(f"总计: {len(collector.providers)} 个供应商")
        print("="*60)
    
    elif choice == "2":
        # 自动注册
        print("\n开始自动注册流程...")
        registrar = FreeLLMAutoRegister(headless=True)
        
        print("\n可用的供应商:")
        for key, config in registrar.provider_configs.items():
            auto_status = "✅ 自动" if config["auto_possible"] else "⚠️ 人工"
            region = "🌎 国际" if config["type"] == "web" else "🇨🇳 国内"
            print(f"  {config['name']}: {auto_status} {region} - {config['url']}")
        
        print("\n输入要注册的供应商名称 (多个用逗号分隔，或输入 'all' 注册全部):")
        provider_input = input("供应商列表: ").strip()
        
        if provider_input.lower() == "all":
            provider_keys = list(registrar.provider_configs.keys())
        else:
            provider_keys = [p.strip().lower().replace(" ", "_") for p in provider_input.split(",")]
        
        for provider_key in provider_keys:
            if provider_key in registrar.provider_configs:
                print(f"\n处理: {registrar.provider_configs[provider_key]['name']}...")
                result = registrar.register_provider(provider_key)
                registrar.results.append(result)
                
                if result.success:
                    print(f"  ✅ {result.provider}: {result.message}")
                    cred = Credential(
                        provider=result.provider,
                        api_key=result.api_key,
                        registration_date=datetime.now().isoformat()
                    )
                    registrar.credentials.append(cred)
                else:
                    print(f"  ⚠️ {result.provider}: {result.message}")
            else:
                print(f"未知供应商: {provider_key}")
        
        # 保存凭据
        if registrar.credentials:
            registrar.save_credentials("llm_credentials.json")
            registrar.save_api_keys("api_keys.txt")
        
        # 生成报告
        print("\n" + "="*60)
        print("注册报告")
        print("="*60)
        successful = sum(1 for r in registrar.results if r.success)
        print(f"总处理: {len(registrar.results)} 个供应商")
        print(f"成功: {successful} 个")
        print(f"失败/跳过: {len(registrar.results) - successful} 个")
    
    elif choice == "3":
        # 手动添加
        registrar = FreeLLMAutoRegister()
        cred = registrar.add_credential_manually()
        registrar.credentials.append(cred)
        registrar.save_credentials("llm_credentials.json")
    
    elif choice == "4":
        print("感谢使用！")
        return
    
    else:
        print("无效选项，请重新运行程序")


if __name__ == "__main__":
    main()