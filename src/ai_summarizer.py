"""
AI摘要生成模块
使用DeepSeek API对文章进行智能分析和摘要生成
"""
import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

from src.config import AIConfig
from src.data_models import Article, ResearchField

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_summarizer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeepSeekAPI:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """
        初始化DeepSeek API客户端
        
        Args:
            api_key: API密钥
            model: 模型名称
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
    
    def generate_summary(self, title: str, abstract: str, authors: str = "") -> str:
        """
        生成文章摘要
        
        Args:
            title: 文章标题
            abstract: 文章摘要
            authors: 作者信息
            
        Returns:
            str: 生成的摘要
        """
        try:
            prompt = f"""
请对以下学术论文进行智能分析和摘要生成：

标题：{title}
作者：{authors}
摘要：{abstract}

请生成一个简洁、准确的中文摘要，突出研究的核心内容、方法和主要发现。摘要应该：
1. 概括研究背景和目的
2. 描述主要方法和实验设计
3. 总结关键发现和结果
4. 指出研究的创新点和意义

请用中文回答，格式清晰，语言专业。
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return ""
    
    def extract_key_points(self, title: str, abstract: str, summary: str = "") -> List[str]:
        """
        提取关键点
        
        Args:
            title: 文章标题
            abstract: 文章摘要
            summary: 生成的摘要
            
        Returns:
            List[str]: 关键点列表
        """
        try:
            prompt = f"""
请从以下学术论文中提取3-5个关键点：

标题：{title}
摘要：{abstract}
生成的摘要：{summary}

请提取最重要的关键点，每个关键点应该：
1. 简洁明了，突出核心内容
2. 涵盖研究方法、发现或应用
3. 用中文表述，语言专业
4. 按重要性排序

请以列表形式返回，每个关键点一行。
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            content = response.choices[0].message.content.strip()
            
            # 解析关键点
            key_points = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 移除序号和符号
                    line = line.lstrip('0123456789.-*• ')
                    if line:
                        key_points.append(line)
            
            return key_points[:5]  # 最多返回5个关键点
            
        except Exception as e:
            logger.error(f"提取关键点失败: {e}")
            return []

class AISummarizer:
    """AI摘要生成器"""
    
    def __init__(self, ai_config: AIConfig):
        """
        初始化AI摘要生成器
        
        Args:
            ai_config: AI配置
        """
        self.ai_config = ai_config
        # 使用DeepSeekAPI类进行API调用
        self.deepseek_api = DeepSeekAPI(
            api_key=self.ai_config.api_key,
            model=self.ai_config.model
        )
        
        # 研究领域关键词映射
        self.field_keywords = {
            ResearchField.PHOTONICS: ["photonics", "optics", "laser", "optical", "light", "photon", "quantum optics"],
            ResearchField.MATERIALS_SCIENCE: ["materials", "material science", "nanomaterials", "quantum materials", "crystal"],
            ResearchField.NANOTECHNOLOGY: ["nanotechnology", "nano", "nanoparticle", "quantum dot", "nanostructure"],
            ResearchField.ELECTRONICS: ["electronics", "semiconductor", "transistor", "integrated circuit", "quantum computing"],
            ResearchField.BIOTECHNOLOGY: ["biotechnology", "bio", "genetics", "CRISPR", "protein", "DNA", "cell"],
            ResearchField.QUANTUM_PHYSICS: ["quantum", "quantum physics", "quantum mechanics", "entanglement"],
            ResearchField.NEUROSCIENCE: ["neuroscience", "neural", "brain", "neuron", "cognitive"],
            ResearchField.ARTIFICIAL_INTELLIGENCE: ["artificial intelligence", "AI", "machine learning", "deep learning"],
            ResearchField.MACHINE_LEARNING: ["machine learning", "ML", "neural network", "algorithm", "data science"],
            ResearchField.CHEMISTRY: ["chemistry", "chemical", "molecule", "catalyst", "reaction"],
            ResearchField.PHYSICS: ["physics", "physical", "mechanics", "thermodynamics"],
            ResearchField.BIOLOGY: ["biology", "biological", "organism", "evolution", "ecology"]
        }
    
    def analyze_article(self, article: Article) -> Article:
        """
        分析文章并生成摘要
        
        Args:
            article: 文章对象
            
        Returns:
            Article: 包含摘要和关键点的文章对象
        """
        try:
            logger.info(f"开始分析文章: {article.title}")
            
            # 检查文章摘要是否为空
            if not article.abstract or article.abstract.strip() == "":
                logger.warning(f"文章摘要为空: {article.title}")
                article.summary = "摘要生成失败：文章摘要为空"
                article.key_points = ["关键点提取失败：文章摘要为空"]
                article.research_field = ResearchField.OTHER
                return article
            
            # 生成摘要
            summary = self._generate_summary(article)
            article.summary = summary
            
            # 提取关键点
            key_points = self._extract_key_points(article)
            article.key_points = key_points
            
            # 识别研究领域
            research_field = self._identify_research_field(article)
            article.research_field = research_field
            
            logger.info(f"文章分析完成: {article.title}")
            
        except Exception as e:
            logger.error(f"分析文章失败: {article.title}, 错误: {e}")
            # 设置默认值
            article.summary = "摘要生成失败"
            article.key_points = ["关键点提取失败"]
            article.research_field = ResearchField.OTHER
        
        return article
    
    def _generate_summary(self, article: Article) -> str:
        """生成文章摘要"""
        try:
            # 使用DeepSeekAPI的generate_summary方法
            summary = self.deepseek_api.generate_summary(
                title=article.title,
                abstract=article.abstract,
                authors=', '.join(article.authors)
            )
            
            if summary:
                logger.info(f"摘要生成成功: {article.title}")
                return summary
            else:
                logger.error(f"摘要生成失败: API返回空内容 | 文章标题: {article.title} | 摘要: {article.abstract}")
                return "摘要生成失败：API返回空内容"
                
        except Exception as e:
            logger.error(f"生成摘要失败: {e} | 文章标题: {article.title} | 摘要: {article.abstract}")
            return "摘要生成失败"
    
    def _extract_key_points(self, article: Article) -> List[str]:
        """提取关键点"""
        try:
            # 使用DeepSeekAPI的extract_key_points方法
            key_points = self.deepseek_api.extract_key_points(
                title=article.title,
                abstract=article.abstract,
                summary=article.summary if article.summary else ""
            )
            
            if key_points:
                logger.info(f"关键点提取成功: {article.title}")
                return key_points
            else:
                logger.error(f"关键点提取失败: API返回空内容 | 文章标题: {article.title} | 摘要: {article.abstract}")
                return ["关键点提取失败：API返回空内容"]
                
        except Exception as e:
            logger.error(f"提取关键点失败: {e} | 文章标题: {article.title} | 摘要: {article.abstract}")
            return ["关键点提取失败"]
    
    def _identify_research_field(self, article: Article) -> ResearchField:
        """识别研究领域"""
        # 合并标题和摘要进行关键词匹配
        text = f"{article.title} {article.abstract}".lower()
        
        # 计算每个领域的匹配分数
        field_scores = {}
        for field, keywords in self.field_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            field_scores[field] = score
        
        # 找到得分最高的领域
        if field_scores:
            best_field = max(field_scores.items(), key=lambda x: x[1])
            if best_field[1] > 0:
                return best_field[0]
        
        return ResearchField.OTHER
    
    def analyze_articles_batch(self, articles: List[Article]) -> List[Article]:
        """
        批量分析文章
        
        Args:
            articles: 文章列表
            
        Returns:
            List[Article]: 分析后的文章列表
        """
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            logger.info(f"正在分析第 {i+1}/{len(articles)} 篇文章")
            analyzed_article = self.analyze_article(article)
            analyzed_articles.append(analyzed_article)
            
            # 添加延迟避免API限制
            time.sleep(1)
        
        return analyzed_articles
    
    def generate_field_summary(self, articles: List[Article], field: ResearchField) -> str:
        """
        生成特定研究领域的总结
        
        Args:
            articles: 文章列表
            field: 研究领域
            
        Returns:
            str: 领域总结
        """
        field_articles = [article for article in articles if article.research_field == field]
        
        if not field_articles:
            return f"今日{field.value}领域暂无新文章。"
        
        # 构建文章列表文本
        articles_text = "\n".join([f"- {article.title} ({article.journal})" for article in field_articles])
        
        # 使用DeepSeekAPI进行领域总结
        prompt = f"""
请对以下{field.value}领域的Nature期刊文章进行总结，要求：
1. 总结该领域今日的主要研究进展
2. 突出重要的技术突破或发现
3. 分析研究趋势和方向
4. 控制在200字以内

文章列表：
{articles_text}

请生成{field.value}领域总结：
"""
        
        try:
            messages = [
                {"role": "system", "content": f"你是一个{field.value}领域的科研专家，擅长总结研究进展。"},
                {"role": "user", "content": prompt}
            ]
            
            result = self.deepseek_api.chat_completion(messages, max_tokens=400, temperature=self.ai_config.temperature)
            
            if result:
                return result
            else:
                return f"今日{field.value}领域有{len(field_articles)}篇新文章。"
                
        except Exception as e:
            logger.error(f"生成领域总结失败: {e}")
            return f"今日{field.value}领域有{len(field_articles)}篇新文章。" 