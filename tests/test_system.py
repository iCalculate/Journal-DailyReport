#!/usr/bin/env python3
"""
System test for Nature Serials AI Daily Report
Tests the complete workflow from crawling to report generation
"""
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.crawler import NatureCrawler
from src.ai_summarizer import AISummarizer
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender
from src.data_models import Article, ArticleType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_system():
    """系统级功能验证"""
    logger.info("开始系统级功能测试...")
    # 1. 配置加载
    ai_config, email_config = Config.load_from_env()
    assert ai_config.api_key, "AI配置未加载"
    # 2. 爬虫采集
    crawler = NatureCrawler(use_selenium=False)
    journal = Config.JOURNALS[0]
    result = crawler.crawl_journal(journal)
    assert result.success, f"爬虫采集失败: {result.error_message}"
    assert result.articles, "未采集到文章"
    # 3. AI摘要
    summarizer = AISummarizer(ai_config)
    article = result.articles[0]
    analyzed = summarizer.analyze_article(article)
    assert analyzed.summary and analyzed.summary != "摘要生成失败", "AI摘要生成失败"
    # 4. 报告生成
    generator = ReportGenerator()
    report = generator.generate_daily_report([analyzed], title="系统测试日报")
    md = generator.generate_markdown_report(report)
    assert "系统测试日报" in md, "Markdown报告生成失败"
    # 5. 邮件配置验证
    sender = EmailSender(email_config)
    assert sender.validate_config() is not None, "邮件配置验证失败"
    logger.info("✅ 系统级功能测试全部通过！")

if __name__ == "__main__":
    test_system() 