#!/usr/bin/env python3
"""
Nature Serials AI Daily Report System
自动化获取Nature系列期刊最新论文并生成AI摘要报告
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
import schedule
import time
from typing import List
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

# 导入自定义模块（从src目录）
from src.config import Config
from src.crawler import NatureCrawler
from src.ai_summarizer import AISummarizer
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender
from src.data_models import Article, DailyReport

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NatureDailyReportSystem:
    """Nature 系列期刊 AI 日报系统"""
    
    def __init__(self):
        """初始化系统"""
        # 加载配置
        self.ai_config, self.email_config = Config.load_from_env()
        
        # 初始化各个模块
        self.crawler = NatureCrawler(use_selenium=False)  # 默认不使用Selenium
        self.summarizer = AISummarizer(self.ai_config)
        self.report_generator = ReportGenerator()
        self.email_sender = EmailSender(self.email_config)
        
        logger.info("Nature 系列期刊 AI 日报系统初始化完成")
    
    def run_daily_report(self, target_date=None) -> bool:
        """
        运行日报生成流程
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("开始生成今日Nature系列期刊日报")
            
            # 1. 爬取文章
            logger.info("步骤1: 开始爬取Nature系列期刊文章")
            crawl_results = self.crawler.crawl_all_journals()
            
            # 统计爬取结果
            total_articles = 0
            all_articles = []
            for result in crawl_results:
                if result.success:
                    total_articles += len(result.articles)
                    all_articles.extend(result.articles)
                    logger.info(f"期刊 {result.journal}: 爬取 {len(result.articles)} 篇文章")
                else:
                    logger.error(f"期刊 {result.journal}: 爬取失败 - {result.error_message}")

            # 只保留目标日期的文章
            if target_date is None:
                today = datetime.now().date()
            else:
                today = target_date
            all_articles = [a for a in all_articles if a.publish_date.date() == today]

            if not all_articles:
                logger.warning(f"{today} 无新文章，跳过后续处理")
                return False
            
            logger.info(f"总共爬取到 {total_articles} 篇文章")
            
            # 2. AI分析文章
            logger.info("步骤2: 开始AI分析文章")
            analyzed_articles = self.summarizer.analyze_articles_batch(all_articles)
            logger.info(f"AI分析完成，共分析 {len(analyzed_articles)} 篇文章")
            
            # 3. 生成日报
            logger.info("步骤3: 生成日报")
            daily_report = self.report_generator.generate_daily_report(analyzed_articles)
            
            # 4. 保存报告
            logger.info("步骤4: 保存报告文件")
            # 将target_date转换为字符串格式传递给save_report
            target_date_str = target_date.strftime('%Y-%m-%d') if target_date is not None else None
            report_files = self.report_generator.save_report(daily_report, target_date=target_date_str)
            logger.info(f"报告已保存: {list(report_files.values())}")
            
            # 5. 发送邮件
            if self.email_sender.validate_config() and Config.ENABLE_EMAIL_SENDING:
                logger.info("步骤5: 发送邮件")
                html_content = self.report_generator.generate_html_report(daily_report)
                markdown_content = self.report_generator.generate_markdown_report(daily_report)
                
                # 准备附件
                attachments = []
                if 'markdown' in report_files:
                    attachments.append(report_files['markdown'])
                if 'json' in report_files:
                    attachments.append(report_files['json'])
                
                # 发送邮件
                success = self.email_sender.send_daily_report(
                    html_content=html_content,
                    markdown_content=markdown_content,
                    attachments=attachments
                )
                
                if success:
                    logger.info("邮件发送成功")
                else:
                    logger.error("邮件发送失败")
            else:
                if not Config.ENABLE_EMAIL_SENDING:
                    logger.info("邮件发送功能已禁用，跳过邮件发送")
                else:
                    logger.warning("邮件配置无效，跳过邮件发送")
            
            logger.info("今日Nature系列期刊日报生成完成")
            return True
            
        except Exception as e:
            logger.error(f"生成日报过程中发生错误: {e}")
            return False
    
    def run_test(self):
        """运行测试"""
        logger.info("开始运行系统测试")
        
        # 测试邮件配置
        if self.email_sender.validate_config():
            logger.info("邮件配置验证通过")
            if self.email_sender.send_test_email():
                logger.info("测试邮件发送成功")
            else:
                logger.error("测试邮件发送失败")
        else:
            logger.error("邮件配置验证失败")
        
        # 测试爬虫
        try:
            logger.info("测试爬虫功能")
            test_journal = Config.JOURNALS[0]  # 测试第一个期刊
            result = self.crawler.crawl_journal(test_journal)
            if result.success:
                logger.info(f"爬虫测试成功，获取 {len(result.articles)} 篇文章")
            else:
                logger.error(f"爬虫测试失败: {result.error_message}")
        except Exception as e:
            logger.error(f"爬虫测试异常: {e}")
        
        logger.info("系统测试完成")
    
    def schedule_daily_report(self):
        """设置定时任务"""
        schedule.every().day.at(Config.CRAWL_TIME).do(self.run_daily_report)
        logger.info(f"已设置每日 {Config.CRAWL_TIME} 自动生成日报")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Nature 系列期刊 AI 日报系统')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--schedule', action='store_true', help='启动定时任务')
    parser.add_argument('--once', action='store_true', help='立即运行一次日报生成')
    parser.add_argument('--selenium', action='store_true', help='使用Selenium爬虫')
    parser.add_argument('--date', type=str, default=None, help='指定提取哪天的文章，格式YYYY-MM-DD')
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = NatureDailyReportSystem()
    
    # 根据参数执行相应操作
    if args.test:
        system.run_test()
    elif args.schedule:
        system.schedule_daily_report()
    elif args.once:
        # 解析日期参数
        if args.date:
            try:
                target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            except Exception as e:
                print(f"❌ 日期格式错误: {args.date}，请用YYYY-MM-DD格式")
                return
        else:
            target_date = None
        system.run_daily_report(target_date=target_date)
    else:
        # 默认运行一次
        system.run_daily_report()

if __name__ == "__main__":
    main() 