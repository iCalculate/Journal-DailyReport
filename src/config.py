"""
Nature 系列期刊 AI 日报系统配置文件
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class JournalConfig:
    """期刊配置"""
    name: str
    url: str
    enabled: bool = True
    keywords: Optional[List[str]] = None

@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    recipients: List[str]
    bcc_recipients: Optional[List[str]] = None

@dataclass
class AIConfig:
    """AI配置"""
    api_key: str
    model: str = "deepseek-chat"
    max_tokens: int = 1000
    temperature: float = 0.7

class Config:
    """主配置类"""
    
    # Nature 系列期刊配置
    JOURNALS = [
        JournalConfig(
            name="Nature",
            url="https://www.nature.com/nature/research-articles",
            keywords=["quantum", "AI", "machine learning", "neuroscience"]
        ),
        JournalConfig(
            name="Nature Communications",
            url="https://www.nature.com/ncomms/research-articles",
            keywords=["interdisciplinary", "cross-disciplinary", "multidisciplinary", "general science"]
        ),
        JournalConfig(
            name="Nature Materials",
            url="https://www.nature.com/nmat/research-articles",
            keywords=["materials", "nanotechnology", "quantum materials"]
        ),
        JournalConfig(
            name="Nature Photonics",
            url="https://www.nature.com/nphoton/research-articles",
            keywords=["photonics", "optics", "laser", "quantum optics"]
        ),
        JournalConfig(
            name="Nature Nanotechnology",
            url="https://www.nature.com/nnano/research-articles",
            keywords=["nanotechnology", "nano", "quantum dots"]
        ),
        JournalConfig(
            name="Nature Electronics",
            url="https://www.nature.com/natelectron/research-articles",
            keywords=["electronics", "semiconductor", "quantum computing"]
        ),
        JournalConfig(
            name="Nature Biotechnology",
            url="https://www.nature.com/nbt/research-articles",
            keywords=["biotechnology", "bio", "genetics", "CRISPR"]
        )
    ]
    
    # 采集配置
    CRAWL_INTERVAL_HOURS = 24  # 采集间隔（小时）
    CRAWL_TIME = "07:00"  # 每天采集时间（北京时间）
    MAX_ARTICLES_PER_JOURNAL = 10  # 每个期刊最多采集文章数
    
    # 文件路径配置
    OUTPUT_DIR = "output"
    LOG_DIR = "logs"
    TEMPLATE_DIR = "templates"
    
    # 报告配置
    REPORT_TITLE = "Nature 系列科研日报"
    SUMMARY_LENGTH = (150, 300)  # 摘要字数范围
    MAX_KEY_POINTS = 5  # 最大关键点数量
    
    # 系统控制配置
    ENABLE_EMAIL_SENDING = True  # 是否启用邮件发送
    ENABLE_LOCAL_TEST = False    # 是否启用本地测试模式
    OUTPUT_FORMAT = "all"        # 输出格式: "markdown", "html", "json", "all"
    
    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置"""
        # AI配置
        ai_config = AIConfig(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
        )
        
        # 邮件配置
        email_config = EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.office365.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("EMAIL_USERNAME", ""),
            password=os.getenv("EMAIL_PASSWORD", ""),
            recipients=os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else [],
            bcc_recipients=os.getenv("EMAIL_BCC", "").split(",") if os.getenv("EMAIL_BCC") else []
        )
        
        # 更新系统控制配置
        cls.ENABLE_EMAIL_SENDING = os.getenv("ENABLE_EMAIL_SENDING", "true").lower() == "true"
        cls.ENABLE_LOCAL_TEST = os.getenv("ENABLE_LOCAL_TEST", "false").lower() == "true"
        cls.OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "all")
        
        return ai_config, email_config

# 创建必要的目录
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
os.makedirs(Config.LOG_DIR, exist_ok=True)
os.makedirs(Config.TEMPLATE_DIR, exist_ok=True)

# 不要在这里设置 openai.api_key 和 openai.base_url，全部由 ai_summarizer.py 动态设置 