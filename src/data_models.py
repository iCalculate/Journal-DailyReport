"""
数据模型定义
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ArticleType(Enum):
    """文章类型枚举"""
    RESEARCH_ARTICLE = "Research Article"
    NEWS = "News"
    EDITORIAL = "Editorial"
    PERSPECTIVE = "Perspective"
    REVIEW = "Review"
    LETTER = "Letter"
    BRIEF_COMMUNICATION = "Brief Communication"
    OTHER = "Other"

class ResearchField(Enum):
    """研究领域枚举"""
    PHOTONICS = "光电子学"
    MATERIALS_SCIENCE = "材料科学"
    NANOTECHNOLOGY = "纳米技术"
    ELECTRONICS = "电子学"
    BIOTECHNOLOGY = "生物技术"
    QUANTUM_PHYSICS = "量子物理"
    NEUROSCIENCE = "神经科学"
    ARTIFICIAL_INTELLIGENCE = "人工智能"
    MACHINE_LEARNING = "机器学习"
    CHEMISTRY = "化学"
    PHYSICS = "物理学"
    BIOLOGY = "生物学"
    OTHER = "其他"

@dataclass
class Article:
    """文章数据模型"""
    title: str
    authors: List[str]
    journal: str
    url: str
    abstract: str
    publish_date: datetime
    article_type: ArticleType
    doi: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    research_field: Optional[ResearchField] = None
    content_preview: Optional[str] = None
    corresponding_author: Optional[str] = None  # 通讯作者
    author_affiliations: List[str] = field(default_factory=list)  # 作者单位列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "authors": self.authors,
            "journal": self.journal,
            "url": self.url,
            "abstract": self.abstract,
            "publish_date": self.publish_date.isoformat(),
            "article_type": self.article_type.value,
            "doi": self.doi,
            "keywords": self.keywords,
            "summary": self.summary,
            "key_points": self.key_points,
            "research_field": self.research_field.value if self.research_field else None,
            "content_preview": self.content_preview,
            "corresponding_author": self.corresponding_author,
            "author_affiliations": self.author_affiliations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """从字典创建文章对象"""
        return cls(
            title=data["title"],
            authors=data["authors"],
            journal=data["journal"],
            url=data["url"],
            abstract=data["abstract"],
            publish_date=datetime.fromisoformat(data["publish_date"]),
            article_type=ArticleType(data["article_type"]),
            doi=data.get("doi"),
            keywords=data.get("keywords", []),
            summary=data.get("summary"),
            key_points=data.get("key_points", []),
            research_field=ResearchField(data["research_field"]) if data.get("research_field") else None,
            content_preview=data.get("content_preview"),
            corresponding_author=data.get("corresponding_author"),
            author_affiliations=data.get("author_affiliations", [])
        )

@dataclass
class DailyReport:
    """日报数据模型"""
    date: datetime
    title: str
    articles: List[Article] = field(default_factory=list)
    total_articles: int = 0
    journals_covered: List[str] = field(default_factory=list)
    
    def add_article(self, article: Article):
        """添加文章到日报"""
        self.articles.append(article)
        self.total_articles += 1
        if article.journal not in self.journals_covered:
            self.journals_covered.append(article.journal)
    
    def get_articles_by_journal(self, journal: str) -> List[Article]:
        """按期刊获取文章"""
        return [article for article in self.articles if article.journal == journal]
    
    def get_articles_by_field(self, field: ResearchField) -> List[Article]:
        """按研究领域获取文章"""
        return [article for article in self.articles if article.research_field == field]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "date": self.date.isoformat(),
            "title": self.title,
            "articles": [article.to_dict() for article in self.articles],
            "total_articles": self.total_articles,
            "journals_covered": self.journals_covered
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyReport':
        """从字典创建日报对象"""
        return cls(
            date=datetime.fromisoformat(data["date"]),
            title=data["title"],
            articles=[Article.from_dict(article_data) for article_data in data["articles"]],
            total_articles=data["total_articles"],
            journals_covered=data["journals_covered"]
        )

@dataclass
class CrawlResult:
    """爬取结果数据模型"""
    journal: str
    articles: List[Article] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    crawl_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "journal": self.journal,
            "articles": [article.to_dict() for article in self.articles],
            "success": self.success,
            "error_message": self.error_message,
            "crawl_time": self.crawl_time.isoformat()
        } 