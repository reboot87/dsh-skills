#!/usr/bin/env python3
"""
自动 LLM API 注册器
Automated registration and API key generation for free LLM providers.
This script attempts to automate the registration process for various free LLM services.
"""

import json
import time
import os
import re
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Try to import selenium for browser automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("提示: 安装 selenium 以启用浏览器自动化功能")
    print("pip install selenium")

try:
    import requests
except ImportError:
    requests = None
    print("提示: 请安装 requests 库")
    print("pip install requests")


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


class FreeLLMAutoRegister:
    """免费 LLM 自动注册器主类"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.credentials: List[Credential] = []
        self.results: List[RegistrationResult] = []
        self.session = None

        if requests:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'FreeLLMAutoRegister/2.0'
            })

        # 注册每个供应商的配置
        self.provider_configs = self._get_provider_configs()

    def _get_provider_configs(self) -> Dict[str, Dict]:
        """获取所有供应商的注册配置"""
        return {
            "openai": {
                "name": "OpenAI",
                "url": "https://platform.openai.com/signup",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "使用邮箱创建账户",
                    "验证邮箱",
                    "申请免费额度"
                ],
                "automation_possible": False,  # OpenAI 注册需要人工验证
                "credential_fields": ["email", "password"]
            },
            "anthropic": {
                "name": "Anthropic",
                "url": "https://console.anthropic.com/signup",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "创建账户",
                    "验证邮箱",
                    "申请免费试用"
                ],
                "automation_possible": False,
                "credential_fields": ["email", "password"]
            },
            "google_ai": {
                "name": "Google AI",
                "url": "https://makersuite.google.com/app/apikey",
                "type": "web",
                "registration_steps": [
                    "访问 AI Studio",
                    "使用 Google 账户登录",
                    "创建 API Key",
                    "开始免费使用"
                ],
                "automation_possible": True,
                "credential_fields": ["google_email"]
            },
            "cohere": {
                "name": "Cohere",
                "url": "https://dashboard.cohere.com/sign-up",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "创建账户",
                    "验证邮箱",
                    "申请免费额度"
                ],
                "automation_possible": False,
                "credential_fields": ["email", "password"]
            },
            "huggingface": {
                "name": "Hugging Face",
                "url": "https://huggingface.co/join",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "创建账户",
                    "验证邮箱",
                    "生成 API Token"
                ],
                "automation_possible": True,
                "credential_fields": ["email", "password"]
            },
            "replicate": {
                "name": "Replicate",
                "url": "https://replicate.com/sign-up",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "创建账户",
                    "验证邮箱",
                    "申请免费额度"
                ],
                "automation_possible": False,
                "credential_fields": ["email", "password"]
            },
            "openrouter": {
                "name": "OpenRouter",
                "url": "https://openrouter.ai/keys",
                "type": "web",
                "registration_steps": [
                    "访问密钥页面",
                    "创建账户",
                    "生成 API Key"
                ],
                "automation_possible": True,
                "credential_fields": ["email", "password"]
            },
            "fireworks": {
                "name": "Fireworks AI",
                "url": "https://api.fireworks.ai/users/sign_up",
                "type": "web",
                "registration_steps": [
                    "访问注册页面",
                    "创建账户",
                    "申请 API 访问"
                ],
                "automation_possible": False,
                "credential_fields": ["email", "password"]
            },
            "groq": {
                "name": "Groq",
                "url": "https://groq.com/login/",
                "type": "web",
                "registration_steps": [
                    "访问登录页面",
                    "创建账户",
                    "获取 API Key"
                ],
                "automation_possible": True,
                "credential_fields": ["email", "password"]
            },
            "baidu_wenxin": {
                "name": "百度文心",
                "url": "https://aip.baidubce.com/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问百度 AI 平台",
                    "使用百度账户登录",
                    "申请 API 权限",
                    "获取 AK/SK"
                ],
                "automation_possible": False,  # 中文平台通常需要人工
                "credential_fields": ["email", "password"]
            },
            "tencent_hunyuan": {
                "name": "腾讯混元",
                "url": "https://hunyuan.cloud.tencent.com/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问腾讯混元入口",
                    "使用腾讯账户登录",
                    "申请 API 权限",
                    "获取密钥"
                ],
                "automation_possible": False,
                "credential_fields": ["email", "password"]
            },
            "ali_tongyi": {
                "name": "阿里通义千问",
                "url": "https://dashscope.console.aliyun.com/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问阿里云控制台",
                    "使用阿里云账户登录",
                    "开通通义千问服务",
                    "获取 API Key"
                ],
                "automation_possible": True,
                "credential_fields": ["aliyun_email", "password"]
            },
            "zhipu_ai": {
                "name": "智谱AI",
                "url": "https://open.bigmodel.cn/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问智谱开放平台",
                    "使用邮箱/手机注册",
                    "实名验证",
                    "申请 API Key"
                ],
                "automation_possible": True,
                "credential_fields": ["email", "password"]
            },
            "minimax": {
                "name": "MiniMax",
                "url": "https://api.minimaxi.com/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问 MiniMax 平台",
                    "使用手机号注册",
                    "实名验证",
                    "申请 API Key"
                ],
                "automation_possible": True,
                "credential_fields": ["phone", "password"]
            },
            "iflytek": {
                "name": "讯飞星火",
                "url": "https://console.xfyun.cn/",
                "type": "web_chinese",
                "registration_steps": [
                    "访问讯飞开放平台",
                    "创建开发者账号",
                    "实名认证",
                    "申请星火接口"
                ],
                "automation_possible": True,
                "credential_fields": ["email", "password"]
            }
        }

    def register_provider(self, provider_key: str) -> RegistrationResult:
        """尝试自动注册指定供应商"""
        if provider_key not in self.provider_configs:
            return RegistrationResult(
                success=False,
                provider=self.provider_configs.get(provider_key, {}).get("name", provider_key),
                message="未知的供应商配置"
            )

        config = self.provider_configs[provider_key]
        result = RegistrationResult(
            success=False,
            provider=config["name"]
        )

        try:
            # 检查是否支持自动化
            if not config["automation_possible"]:
                result.message = f"{config['name']} 注册需要人工验证，请手动访问: {config['url']}"
                result.details = {"url": config["url"], "steps": config["registration_steps"]}
                return result

            # 根据类型进行自动化注册
            reg_type = config["type"]

            if reg_type == "web":
                self._register_web(provider_key, config, result)
            elif reg_type == "web_chinese":
                self._register_web_chinese(provider_key, config, result)

        except Exception as e:
            result.message = f"注册过程出错: {str(e)}"

        return result

    def _register_web(self, provider_key: str, config: Dict, result: RegistrationResult):
        """Web 自动注册流程"""
        if not SELENIUM_AVAILABLE or not self.session:
            result.message = "Selenium 未可用，跳过自动注册"
            return

        try:
            # 配置浏览器选项
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 启动浏览器
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except:
                # 如果无法启动 Chrome，尝试其他方式
                result.message = "无法启动浏览器，请手动注册"
                return

            try:
                # 访问注册页面
                driver.get(config["url"])
                time.sleep(3)  # 等待页面加载

                # 根据提供的注册步骤进行操作
                steps = config["registration_steps"]

                for step in steps:
                    if "访问注册页面" in step or "访问" in step:
                        # 已经通过 driver.get 访问了
                        continue

                    elif "使用邮箱" in step or "使用邮箱创建" in step:
                        # 查找邮箱输入框
                        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[type='text']")
                        # 生成临时邮箱或使用默认
                        test_email = f"test{provider_key}@example.com"
                        email_input.send_keys(test_email)

                    elif "创建账户" in step or "创建账户" in step:
                        # 查找创建账户按钮
                        create_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign up') or contains(text(), 'Register') or contains(text(), '创建账户')]")
                        create_btn.click()
                        time.sleep(2)

                    elif "验证邮箱" in step or "验证" in step:
                        # 这里需要处理邮箱验证，通常需要人工
                        result.message = "需要人工验证邮箱，跳过自动流程"
                        driver.quit()
                        return

                    elif "申请免费额度" in step or "申请" in step:
                        # 查找申请按钮
                        apply_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Apply') or contains(text(), '申请') or contains(text(), '获取')]")
                        apply_btn.click()
                        time.sleep(2)

                # 尝试提取 API Key（如果已生成）
                page_source = driver.page_source
                api_key_patterns = [
                    r'sk-[a-zA-Z0-9]{48,}',
                    r'[a-zA-Z0-9]{32,}',
                    r'eyJ[a-zA-Z0-9._-]+\.([a-zA-Z0-9._-]+)\.'
                ]

                for pattern in api_key_patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        result.api_key = match.group(0)
                        result.success = True
                        result.message = f"成功获取 API Key for {config['name']}"
                        break

                if not result.api_key:
                    result.message = f"注册完成，但未自动提取 API Key。请手动访问: {config['url']}"

            finally:
                driver.quit()

        except Exception as e:
            result.message = f"Web 自动注册出错: {str(e)}"

    def _register_web_chinese(self, provider_key: str, config: Dict, result: RegistrationResult):
        """中文网站自动注册流程"""
        if not SELENIUM_AVAILABLE or not self.session:
            result.message = "Selenium 未可用，跳过自动注册"
            return

        try:
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get(config["url"])
                time.sleep(3)

                steps = config["registration_steps"]

                for step in steps:
                    if "访问" in step or "访问" in step:
                        continue
                    elif "使用" in step and "账户" in step:
                        # 尝试登录
                        try:
                            login_btn = driver.find_element(By.LINK_TEXT, "登录")
                            login_btn.click()
                            time.sleep(2)
                        except:
                            pass

                    elif "申请" in step:
                        try:
                            apply_btn = driver.find_element(By.XPATH, "//button[contains(text(), '申请') or contains(text(), '申请权限')]")
                            apply_btn.click()
                            time.sleep(2)
                        except:
                            pass

                    elif "获取" in step and "密钥" in step:
                        try:
                            get_key_btn = driver.find_element(By.XPATH, "//button[contains(text(), '获取') or contains(text(), '获取密钥')]")
                            get_key_btn.click()
                            time.sleep(2)
                        except:
                            pass

                # 尝试提取信息
                page_source = driver.page_source

                # 查找类似密钥的模式
                api_key_match = re.search(r'[a-zA-Z0-9]{20,}', page_source)
                if api_key_match:
                    result.api_key = api_key_match.group(0)

                # 查找邮箱
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', page_source)
                if email_match:
                    result.email = email_match.group(0)

                if result.api_key:
                    result.success = True
                    result.message = f"成功获取 {config['name']} API Key"
                else:
                    result.message = f"注册流程完成，请手动访问: {config['url']} 获取 API Key"

            finally:
                driver.quit()

        except Exception as e:
            result.message = f"中文网站自动注册出错: {str(e)}"

    def save_credentials(self, filename: str = "llm_credentials.json"):
        """保存凭据到文件"""
        credentials_data = [asdict(cred) for cred in self.credentials]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(credentials_data, f, ensure_ascii=False, indent=2)

        print(f"凭据已保存到: {filename}")
        return filename

    def load_credentials(self, filename: str = "llm_credentials.json"):
        """从文件加载凭据"""
        if not os.path.exists(filename):
            print(f"文件不存在: {filename}")
            return []

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                credentials_data = json.load(f)

            self.credentials = []
            for data in credentials_data:
                cred = Credential(**data)
                self.credentials.append(cred)

            print(f"已加载 {len(self.credentials)} 组凭据")
            return self.credentials

        except Exception as e:
            print(f"加载凭据出错: {str(e)}")
            return []

    def run_all_registrations(self):
        """运行所有供应商的注册流程"""
        print("开始自动注册流程...\n")

        for provider_key in self.provider_configs:
            print(f"正在处理: {self.provider_configs[provider_key]['name']}...")
            result = self.register_provider(provider_key)
            self.results.append(result)

            if result.success:
                print(f"  ✅ {result.provider}: {result.message}")
                # 保存凭据
                cred = Credential(
                    provider=result.provider,
                    api_key=result.api_key,
                    registration_date=datetime.now().isoformat()
                )
                self.credentials.append(cred)
            else:
                print(f"  ⚠️ {result.provider}: {result.message}")

            # 避免请求过于频繁
            time.sleep(2)

        # 保存所有凭据
        if self.credentials:
            self.save_credentials()

        # 生成报告
        self._generate_report()

        return self.results

    def _generate_report(self):
        """生成注册报告"""
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)

        report = f"""
# 自动注册报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计概览
- 总处理数: {len(self.results)}
- 成功注册: {successful}
- 失败/跳过: {failed}
- 成功率: {successful/len(self.results)*100:.1f}%

## 成功获取的 API Key
"""

        for result in self.results:
            if result.success and result.api_key:
                report += f"""
### {result.provider}
- API Key: {result.api_key[:20]}...{result.api_key[-10:]} (如果太长)
- 状态: {result.message}
"""

        report += """
## 注意事项
1. 部分供应商的注册过程需要人工验证（如邮箱验证码、短信验证等）
2. 保护好你的 API Key，不要泄露给他人
3. 定期检查免费额度是否已用尽
4. 某些平台可能有每日/每月使用限制
5. 如需续期或提额，请访问官方控制台

## 存储的凭据
"""

        for cred in self.credentials:
            report += f"- {cred.provider}: {cred.api_key[:20]}... (如果存在)\n"

        with open("registration_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("注册报告已生成: registration_report.md")


def main():
    print("=" * 60)
    print("免费 LLM API 自动注册器")
    print("=" * 60)
    print()
    print("此工具旨在自动化注册多个免费 LLM 服务并获取 API Key")
    print("由于各平台的安全机制，部分注册步骤可能需要人工干预")
    print()
    print("=" * 60)

    # 创建注册器实例
    registrar = FreeLLMAutoRegister(headless=True)

    # 运行所有注册
    results = registrar.run_all_registrations()

    # 显示摘要
    print()
    print("=" * 60)
    print("注册完成!")
    print("=" * 60)
    print(f"总处理: {len(results)} 个供应商")
    successful = sum(1 for r in results if r.success)
    print(f"成功: {successful} 个")
    print(f"失败/跳过: {len(results) - successful} 个")
    print()
    print("成功的 API Key 已保存至: llm_credentials.json")
    print("详细报告: registration_report.md")


if __name__ == "__main__":
    main()