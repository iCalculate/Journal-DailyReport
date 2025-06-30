"""
报告生成模块
将分析后的文章生成结构化的日报
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

from src.config import Config
from src.data_models import Article, DailyReport, ResearchField

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/report_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.template_env = Environment(
            loader=FileSystemLoader(Config.TEMPLATE_DIR),
            autoescape=True
        )
        
        # 创建默认模板
        self._create_default_templates()
    
    def _create_default_templates(self):
        """创建默认模板文件"""
        # Markdown模板 - 只按期刊分类
        markdown_template = """# {{ report.title }} - {{ report.date.strftime('%Y/%m/%d') }}

## 📊 今日概览
- **总文章数**: {{ report.total_articles }} 篇
- **覆盖期刊**: {{ report.journals_covered|length }} 个

## 🔬 按期刊分类

{% for journal in report.journals_covered %}
### {{ journal }}
{% set journal_articles = report.get_articles_by_journal(journal) %}
{% for article in journal_articles %}
#### {{ article.title }}
- **期刊**: {{ article.journal }}
- **作者**: {{ article.authors|join(', ') if article.authors else '作者信息未获取' }}
{% if article.corresponding_author %}
- **通讯作者**: {{ article.corresponding_author }}
{% endif %}
{% if article.author_affiliations %}
- **作者单位**: {{ article.author_affiliations|join('; ') }}
{% endif %}
- **文章类型**: {{ article.article_type.value }}
- **发布日期**: {{ article.publish_date.strftime('%Y-%m-%d') }}
- **原文链接**: [{{ article.url }}]({{ article.url }})

**摘要**: {{ article.summary or '摘要生成失败' }}

{% if article.key_points and article.key_points[0] != "关键点提取失败" %}
**关键贡献点**:
{% for point in article.key_points %}
- {{ point }}
{% endfor %}
{% endif %}

---
{% endfor %}
{% endfor %}

---
*本报告由 Nature 系列期刊 AI 日报系统自动生成*
*生成时间: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*
"""
        
        # HTML模板
        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }} - {{ report.date.strftime('%Y/%m/%d') }}</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }
        h3 { color: #2980b9; margin-top: 25px; }
        .overview { background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .overview ul { list-style: none; padding: 0; }
        .overview li { margin: 10px 0; font-weight: bold; }
        .article { border: 1px solid #ddd; margin: 15px 0; padding: 20px; border-radius: 8px; background: #fafafa; }
        .article-title { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .article-title a { color: #3498db; text-decoration: none; }
        .article-title a:hover { text-decoration: underline; }
        .article-meta { color: #7f8c8d; font-size: 14px; margin: 10px 0; }
        .article-summary { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 3px solid #3498db; }
        .key-points { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .key-points ul { margin: 5px 0; }
        .field-stats { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }
        .stat-item { background: #3498db; color: white; padding: 10px 15px; border-radius: 20px; font-size: 14px; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ report.title }} - {{ report.date.strftime('%Y/%m/%d') }}</h1>
        
        <div class="overview">
            <h2>📊 今日概览</h2>
            <ul>
                <li>总文章数: {{ report.total_articles }} 篇</li>
                <li>覆盖期刊: {{ report.journals_covered|length }} 个</li>
            </ul>
        </div>

        <h2>🔬 按期刊分类</h2>
        {% for journal in report.journals_covered %}
        <h3>{{ journal }}</h3>
        {% set journal_articles = report.get_articles_by_journal(journal) %}
        {% for article in journal_articles %}
        <div class="article">
            <div class="article-title">
                <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
            </div>
            <div class="article-meta">
                作者: {{ article.authors|join(', ') }} | 
                类型: {{ article.article_type.value }} | 
                期刊: {{ article.journal }}
            </div>
            <div class="article-summary">
                {{ article.summary or '摘要生成失败' }}
            </div>
            {% if article.key_points %}
            <div class="key-points">
                <strong>关键点:</strong>
                <ul>
                    {% for point in article.key_points %}
                    <li>{{ point }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        {% endfor %}
        {% endfor %}

        <div class="footer">
            本报告由 Nature 系列期刊 AI 日报系统自动生成<br>
            生成时间: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}
        </div>
    </div>
</body>
</html>"""
        
        # 保存模板文件
        with open(os.path.join(Config.TEMPLATE_DIR, 'report.md.j2'), 'w', encoding='utf-8') as f:
            f.write(markdown_template)
        
        with open(os.path.join(Config.TEMPLATE_DIR, 'report.html.j2'), 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    def generate_daily_report(self, articles: List[Article], title: str = None) -> DailyReport:
        """
        生成日报
        
        Args:
            articles: 文章列表
            title: 报告标题
            
        Returns:
            DailyReport: 日报对象
        """
        if not title:
            title = Config.REPORT_TITLE
        
        report = DailyReport(
            date=datetime.now(),
            title=title
        )
        
        # 添加文章到日报
        for article in articles:
            report.add_article(article)
        
        return report
    
    def generate_markdown_report(self, report: DailyReport) -> str:
        """
        生成Markdown格式的报告
        
        Args:
            report: 日报对象
            
        Returns:
            str: Markdown格式的报告内容
        """
        try:
            template = self.template_env.get_template('report.md.j2')
            
            # 准备模板数据
            field_articles = defaultdict(list)
            field_stats = defaultdict(int)
            
            for article in report.articles:
                if article.research_field:
                    field_articles[article.research_field].append(article)
                    field_stats[article.research_field] += 1
            
            context = {
                'report': report,
                'field_articles': dict(field_articles),
                'field_stats': dict(field_stats),
                'datetime': datetime
            }
            
            return template.render(context)
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            return self._generate_fallback_markdown(report)
    
    def generate_html_report(self, report: DailyReport) -> str:
        """
        生成HTML格式的报告
        
        Args:
            report: 日报对象
            
        Returns:
            str: HTML格式的报告内容
        """
        try:
            template = self.template_env.get_template('report.html.j2')
            
            # 准备模板数据
            field_articles = defaultdict(list)
            field_stats = defaultdict(int)
            
            for article in report.articles:
                if article.research_field:
                    field_articles[article.research_field].append(article)
                    field_stats[article.research_field] += 1
            
            context = {
                'report': report,
                'field_articles': dict(field_articles),
                'field_stats': dict(field_stats),
                'datetime': datetime
            }
            
            return template.render(context)
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return self._generate_fallback_html(report)
    
    def save_report(self, report: DailyReport, output_dir: str = None, target_date: Optional[str] = None) -> Dict[str, str]:
        """
        保存报告到文件
        
        Args:
            report: 日报对象
            output_dir: 输出目录
            target_date: 目标日期字符串 (YYYY-MM-DD)
            
        Returns:
            Dict[str, str]: 文件路径字典
        """
        if not output_dir:
            output_dir = Config.OUTPUT_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用目标日期或报告日期生成文件名
        if target_date:
            date_str = target_date.replace('-', '')
        else:
            date_str = report.date.strftime('%Y%m%d')
        
        files = {}
        
        try:
            # 生成Markdown报告
            if Config.OUTPUT_FORMAT in ["markdown", "all"]:
                markdown_content = self.generate_markdown_report(report)
                markdown_path = os.path.join(output_dir, f'nature_daily_report_{date_str}.md')
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                files['markdown'] = markdown_path
            
            # 生成HTML报告
            if Config.OUTPUT_FORMAT in ["html", "all"]:
                html_content = self.generate_html_report(report)
                html_path = os.path.join(output_dir, f'nature_daily_report_{date_str}.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                files['html'] = html_path
            
            # 保存JSON数据
            if Config.OUTPUT_FORMAT in ["json", "all"]:
                json_path = os.path.join(output_dir, f'nature_daily_report_{date_str}.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
                files['json'] = json_path
            
            logger.info(f"报告已保存到: {output_dir}")
            logger.info(f"输出格式: {Config.OUTPUT_FORMAT}")
            logger.info(f"生成文件: {list(files.keys())}")
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
        
        return files
    
    def _generate_fallback_markdown(self, report: DailyReport) -> str:
        """生成备用Markdown报告"""
        content = f"# {report.title} - {report.date.strftime('%Y/%m/%d')}\n\n"
        content += f"总文章数: {report.total_articles} 篇\n\n"
        
        for article in report.articles:
            content += f"## {article.title}\n"
            content += f"- 期刊: {article.journal}\n"
            content += f"- 作者: {', '.join(article.authors)}\n"
            content += f"- 链接: {article.url}\n"
            if article.summary:
                content += f"- 摘要: {article.summary}\n"
            content += "\n"
        
        return content
    
    def _generate_fallback_html(self, report: DailyReport) -> str:
        """生成备用HTML报告"""
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report.title} - {report.date.strftime('%Y/%m/%d')}</title>
</head>
<body>
    <h1>{report.title} - {report.date.strftime('%Y/%m/%d')}</h1>
    <p>总文章数: {report.total_articles} 篇</p>
"""
        
        for article in report.articles:
            content += f"""
    <h2>{article.title}</h2>
    <p>期刊: {article.journal}</p>
    <p>作者: {', '.join(article.authors)}</p>
    <p><a href="{article.url}">原文链接</a></p>
"""
            if article.summary:
                content += f"    <p>摘要: {article.summary}</p>\n"
        
        content += "</body></html>"
        return content 