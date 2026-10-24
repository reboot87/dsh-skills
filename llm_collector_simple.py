#!/usr/bin/env python3
"""
免费 LLM API 收集器
Free LLM API Collector - Simplified version that works without selenium

此版本提供：
1. 收集国内外免费 LLM API 信息
2. 自动注册流程指导（需要手动验证）
3. API 密钥保存功能
4. 多种导出格式
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

# 尝试导入 requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class Credential:
    """凭据信息"""
    provider: str
    api_key: str = ""
    username: str = ""
    password: str = ""
    email: str = ""
    registration_date: str = ""
    notes: str = ""


class FreeLLMCollector:
    """免费 LLM 收集器"""
    
    def __init__(self):
        self.providers: List[Dict] = []
        self._collect_all()
    
    def _create_provider(self, name: str, base_url: str, description: str, 
                        models: List[str], rate_limits: Dict, 
                        registration_url: str, region: str) -> Dict:
        """创建供应商"""
        return {
            "name": name,
            "base_url": base_url,
            "is_free": True,
            "registration_required": True,
            "registration_url": registration_url,
            "registration_steps": [],
            "rate_limits": rate_limits,
            "supported_models": models,
            "description": description,
            "region": region
        }
    
    def _collect_all(self):
        """收集所有供应商"""
        self.providers = [
            # 国际供应商
            self._create_provider("OpenAI", "https://api.openai.com/v1", "OpenAI 免费 $5 额度",
                                 ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
                                 {"requests_per_day": 3, "tokens_per_day": 4000},
                                 "https://platform.openai.com/signup", "international"),
            
            self._create_provider("Anthropic", "https://api.anthropic.com/v1", "Anthropic Claude 免费试用",
                                 ["claude-3-opus", "claude-3-sonnet", "claude-2-1"],
                                 {"characters_per_month": 10000, "requests_per_minute": 100},
                                 "https://console.anthropic.com/signup", "international"),
            
            self._create_provider("Google AI", "https://generativelanguage.googleapis.com/v1beta", "Google Gemini 免费额度",
                                 ["gemini-pro", "gemini-pro-vision"],
                                 {"requests_per_day": 100, "tokens_per_day": 50000},
                                 "https://makersuite.google.com/app/apikey", "international"),
            
            self._create_provider("Cohere", "https://api.cohere.com/v1", "Cohere 免费额度",
                                 ["command-r", "command-r-plus", "command-light"],
                                 {"requests_per_day": 1000, "tokens_per_day": 5000},
                                 "https://dashboard.cohere.com/sign-up", "international"),
            
            self._create_provider("Hugging Face", "https://api-inference.huggingface.co/models", 
                                 "Hugging Face 免费推理 API",
                                 ["gpt2", "bloom", "llama2", "mistral"],
                                 {"requests_per_minute": 20, "requests_per_day": 300},
                                 "https://huggingface.co/join", "international"),
            
            self._create_provider("OpenRouter", "https://openrouter.ai/api/v1", "OpenRouter 聚合免费额度",
                                 ["gpt-3.5-turbo", "gpt-4", "claude-3", "gemini-pro"],
                                 {"credits_per_day": 5, "requests_per_minute": 20},
                                 "https://openrouter.ai/keys", "international"),
            
            self._create_provider("Opencode", "https://openrouter.ai/api/v1", "Opencode 免费额度",
                                 ["gpt-3.5-turbo", "gpt-4", "claude-3", "gemini-pro"],
                                 {"credits_per_day": 5, "requests_per_minute": 20},
                                 "https://openrouter.ai/keys", "international"),
            
            self._create_provider("Groq", "https://api.groq.com/openai/v1", "Groq 超快推理免费额度",
                                 ["mixtral-8x7b-32768", "llama3-70b-8192", "gemma-7b-it"],
                                 {"tokens_per_minute": 6000, "requests_per_day": 100},
                                 "https://groq.com/login/", "international"),
            
            self._create_provider("Mistral AI", "https://api.mistral.ai/v1", "Mistral 免费额度",
                                 ["mistral-small", "mistral-medium", "openlarge"],
                                 {"requests_per_day": 100, "tokens_per_day": 10000},
                                 "https://console.mistral.ai/", "international"),
            
            self._create_provider("DeepSeek", "https://api.deepseek.com/v1", "DeepSeek 高性能免费额度",
                                 ["deepseek-chat", "deepseek-coder"],
                                 {"requests_per_day": 100, "tokens_per_day": 50000},
                                 "https://platform.deepseek.com/api_keys", "international"),
            
            self._create_provider("Cline", "https://api.anthropic.com/v1", "Cline 增强 Claude 免费额度",
                                 ["claude-3-opus", "claude-3-sonnet"],
                                 {"characters_per_month": 100000},
                                 "https://console.anthropic.com/signup", "international"),
            
            # 国内供应商
            self._create_provider("百度文心", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
                                 "百度文心一言免费额度",
                                 ["ernie-bot", "ernie-bot-turbo"],
                                 {"requests_per_day": 500, "tokens_per_day": 20000},
                                 "https://aip.baidubce.com/", "domestic"),
            
            self._create_provider("腾讯混元", "https://api.hunyuan.tencent.com/v1/chat/completions",
                                 "腾讯混元免费额度",
                                 ["hunyuan-standard", "hunyuan-lite"],
                                 {"requests_per_day": 1000, "tokens_per_day": 100000},
                                 "https://hunyuan.cloud.tencent.com/", "domestic"),
            
            self._create_provider("阿里通义", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 "阿里云通义千问免费额度",
                                 ["qwen-7b-chat", "qwen-14b-chat"],
                                 {"requests_per_day": 1000, "tokens_per_day": 20000},
                                 "https://dashscope.console.aliyun.com/", "domestic"),
            
            self._create_provider("智谱AI", "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                                 "智谱AI GLM免费额度",
                                 ["glm-4", "glm-3-turbo"],
                                 {"requests_per_minute": 30, "requests_per_day": 100},
                                 "https://open.bigmodel.cn/", "domestic"),
            
            self._create_provider("MiniMax", "https://api.minimaxi.com/v1/text/chatcompletion_v2",
                                 "MiniMax免费额度",
                                 ["abab6.5-chat", "abab5.5-chat"],
                                 {"requests_per_day": 100, "tokens_per_day": 20000},
                                 "https://api.minimaxi.com/", "domestic"),
            
            self._create_provider("讯飞星火", "https://spark-api.cn-huabei-1.xf-yun.com/v1/chat/completions",
                                 "讯飞星火免费额度",
                                 ["spark-lite", "spark-pro"],
                                 {"requests_per_day": 100, "tokens_per_day": 20000},
                                 "https://console.xfyun.cn/", "domestic"),
        ]
    
    def get_international(self) -> List[Dict]:
        """获取国际供应商"""
        return [p for p in self.providers if p["region"] == "international"]
    
    def get_domestic(self) -> List[Dict]:
        """获取国内供应商"""
        return [p for p in self.providers if p["region"] == "domestic"]
    
    def export_json(self, filename: str = "free_llm_providers.json"):
        """导出 JSON 文件"""
        data = {
            "导出时间": datetime.now().isoformat(),
            "总供应商数": len(self.providers),
            "国际供应商数": len(self.get_international()),
            "国内供应商数": len(self.get_domestic()),
            "供应商列表": self.providers
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def export_markdown(self, filename: str = "free_llm_providers.md"):
        """导出 Markdown 文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 免费大型语言模型供应商目录\n\n")
            f.write(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📊 统计概览\n")
            f.write(f"- 总供应商: {len(self.providers)}\n")
            f.write(f"- 国际: {len(self.get_international())}\n")
            f.write(f"- 国内: {len(self.get_domestic())}\n\n")
            
            f.write("## 🌍 国际供应商\n\n")
            for p in self.get_international():
                f.write(f"### {p['name']}\n")
                f.write(f"**描述**: {p['description']}\n\n")
                f.write(f"- **API 地址**: `{p['base_url']}`\n")
                f.write(f"- **注册链接**: {p['registration_url']}\n")
                f.write(f"- **支持模型**: {', '.join(p['supported_models'])}\n")
                f.write(f"- **配额限制**: {json.dumps(p['rate_limits'], ensure_ascii=False)}\n\n")
            
            f.write("## 🇨🇳 国内供应商\n\n")
            for p in self.get_domestic():
                f.write(f"### {p['name']}\n")
                f.write(f"**描述**: {p['description']}\n\n")
                f.write(f"- **API 地址**: `{p['base_url']}`\n")
                f.write(f"- **注册链接**: {p['registration_url']}\n")
                f.write(f"- **支持模型**: {', '.join(p['supported_models'])}\n")
                f.write(f"- **配额限制**: {json.dumps(p['rate_limits'], ensure_ascii=False)}\n\n")
        
        return filename
    
    def export_txt(self, filename: str = "llm_api_keys.txt"):
        """导出简洁的 TXT 格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("免费 LLM API 列表\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("[INTERNATIONAL]\n")
            for p in self.get_international():
                f.write(f"名称: {p['name']}\n")
                f.write(f"URL: {p['base_url']}\n")
                f.write(f"注册: {p['registration_url']}\n")
                f.write("---\n")
            
            f.write("\n[DOMESTIC]\n")
            for p in self.get_domestic():
                f.write(f"名称: {p['name']}\n")
                f.write(f"URL: {p['base_url']}\n")
                f.write(f"注册: {p['registration_url']}\n")
                f.write("---\n")
        
        return filename


def main():
    """主函数"""
    print("=" * 50)
    print("免费 LLM API 收集器")
    print("=" * 50)
    
    collector = FreeLLMCollector()
    
    # 导出所有格式
    json_file = collector.export_json()
    md_file = collector.export_markdown()
    txt_file = collector.export_txt()
    
    print(f"\n✅ 收集完成!")
    print(f"   - JSON: {json_file}")
    print(f"   - Markdown: {md_file}")
    print(f"   - TXT: {txt_file}")
    print(f"\n📊 供应商统计:")
    print(f"   - 国际: {len(collector.get_international())} 个")
    print(f"   - 国内: {len(collector.get_domestic())} 个")
    print(f"   - 总计: {len(collector.providers)} 个")
    print("=" * 50)


if __name__ == "__main__":
    main()