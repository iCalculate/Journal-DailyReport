"""
Nature 系列期刊数据采集模块
"""
import requests
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from src.config import Config, JournalConfig
from src.data_models import Article, ArticleType, CrawlResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{Config.LOG_DIR}/crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NatureCrawler:
    """Nature期刊爬虫类"""
    
    def __init__(self, use_selenium: bool = False):
        """
        初始化爬虫
        
        Args:
            use_selenium: 是否使用Selenium（用于需要JS渲染的页面）
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """设置Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            self.driver.implicitly_wait(10)
        except Exception as e:
            logger.error(f"Failed to setup Selenium: {e}")
            self.use_selenium = False
    
    def crawl_journal(self, journal_config: JournalConfig) -> CrawlResult:
        """
        爬取指定期刊的文章
        
        Args:
            journal_config: 期刊配置
            
        Returns:
            CrawlResult: 爬取结果
        """
        logger.info(f"开始爬取期刊: {journal_config.name}")
        
        try:
            if self.use_selenium:
                articles = self._crawl_with_selenium(journal_config)
            else:
                articles = self._crawl_with_requests(journal_config)
            
            # 过滤最近的文章（最近7天）
            recent_articles = self._filter_recent_articles(articles)
            
            logger.info(f"期刊 {journal_config.name} 爬取完成，获取 {len(recent_articles)} 篇最近文章")
            
            return CrawlResult(
                journal=journal_config.name,
                articles=recent_articles,
                success=True
            )
            
        except Exception as e:
            logger.error(f"爬取期刊 {journal_config.name} 失败: {e}")
            return CrawlResult(
                journal=journal_config.name,
                articles=[],
                success=False,
                error_message=str(e)
            )
    
    def _crawl_with_requests(self, journal_config: JournalConfig) -> List[Article]:
        """使用requests爬取文章"""
        articles = []
        
        try:
            response = self.session.get(journal_config.url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Nature期刊的文章选择器
            article_selectors = [
                'article[data-test="article"]',
                '.c-article-item',
                '.c-card',
                '[data-testid="article"]'
            ]
            
            article_elements = []
            for selector in article_selectors:
                article_elements = soup.select(selector)
                if article_elements:
                    break
            
            if not article_elements:
                # 尝试其他选择器
                article_elements = soup.find_all('div', class_=lambda x: x and 'article' in x.lower())
            
            for element in article_elements[:Config.MAX_ARTICLES_PER_JOURNAL]:
                try:
                    article = self._parse_article_element(element, journal_config.name)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"解析文章元素失败: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"请求期刊页面失败: {e}")
            raise
        
        return articles
    
    def _crawl_with_selenium(self, journal_config: JournalConfig) -> List[Article]:
        """使用Selenium爬取文章"""
        articles = []
        
        try:
            self.driver.get(journal_config.url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # 滚动页面以加载更多内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # 查找文章元素
            article_elements = self.driver.find_elements(By.TAG_NAME, "article")
            
            if not article_elements:
                article_elements = self.driver.find_elements(By.CSS_SELECTOR, ".c-article-item")
            
            for element in article_elements[:Config.MAX_ARTICLES_PER_JOURNAL]:
                try:
                    article = self._parse_selenium_element(element, journal_config.name)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"解析Selenium元素失败: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Selenium爬取失败: {e}")
            raise
        
        return articles
    
    def _parse_article_element(self, element, journal_name: str) -> Optional[Article]:
        """解析文章元素"""
        try:
            # 提取标题
            title_element = element.find('h3') or element.find('h2') or element.find('h1')
            if not title_element:
                title_element = element.find('a', class_=lambda x: x and 'title' in x.lower())
            
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            if not title:
                return None
            
            # 提取链接
            link_element = element.find('a')
            if not link_element:
                return None
            
            url = link_element.get('href')
            if not url:
                return None
            
            if not url.startswith('http'):
                url = urljoin('https://www.nature.com', url)
            
            # 提取作者 - 改进版本
            authors = self._extract_authors_from_element(element)
            
            # 如果列表页面没有找到作者，尝试访问文章详情页
            if not authors:
                authors = self._extract_authors_from_article_page(url)
            
            # 提取发布时间
            date_element = element.find('time') or element.find('span', class_=lambda x: x and 'date' in x.lower())
            publish_date = datetime.now()
            if date_element:
                date_text = date_element.get('datetime') or date_element.get_text(strip=True)
                try:
                    publish_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                except:
                    pass
            
            # 提取文章类型
            article_type = ArticleType.RESEARCH_ARTICLE
            type_element = element.find('span', class_=lambda x: x and 'type' in x.lower())
            if type_element:
                type_text = type_element.get_text(strip=True)
                for art_type in ArticleType:
                    if art_type.value.lower() in type_text.lower():
                        article_type = art_type
                        break
            
            # 提取摘要
            abstract = ""
            # 尝试多种摘要选择器
            abstract_keywords = ['abstract', 'summary', 'description', 'content']
            
            for keyword in abstract_keywords:
                try:
                    abstract_element = element.find('p', class_=lambda x: x and keyword in x.lower())
                    if abstract_element:
                        abstract = abstract_element.get_text(strip=True)
                        if abstract:
                            break
                except:
                    continue
            
            # 如果还是没找到，尝试查找包含特定关键词的段落
            if not abstract:
                try:
                    paragraphs = element.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 50:  # 摘要通常比较长
                            abstract = text
                            break
                except:
                    pass
            
            return Article(
                title=title,
                authors=authors,
                journal=journal_name,
                url=url,
                abstract=abstract,
                publish_date=publish_date,
                article_type=article_type
            )
            
        except Exception as e:
            logger.warning(f"解析文章元素时出错: {e}")
            return None
    
    def _extract_authors_from_element(self, element) -> List[str]:
        """从文章元素中提取作者信息"""
        authors = []
        
        # 尝试多种作者选择器
        author_selectors = [
            'a[data-test="author"]',
            'a[class*="author"]',
            'span[class*="author"]',
            '.c-article-item__authors a',
            '.c-article-item__authors span',
            '[data-test="author"]',
            '.c-article-authors a',
            '.c-article-authors span',
            'a[data-track-action="author"]',
            'span[data-track-action="author"]'
        ]
        
        for selector in author_selectors:
            try:
                elements = element.select(selector)
                for elem in elements:
                    author = elem.get_text(strip=True)
                    # 过滤掉非作者信息
                    if (author and len(author) > 2 and 
                        author not in authors and 
                        author not in ['Author notes', 'Search author on:', 'Google Scholar', 
                                     'View author publications', 'Reprints and permissions',
                                     'Language editing services', 'Guide to authors',
                                     'Editorial policies', 'Nature portfolio policies',
                                     'Research data', 'Language editing', 'Scientific editing']):
                        authors.append(author)
            except:
                continue
        
        # 如果还是没找到作者，尝试查找包含作者关键词的文本
        if not authors:
            try:
                # 查找包含作者关键词的文本
                author_text = element.get_text()
                if 'et al.' in author_text:
                    # 提取et al.之前的作者
                    parts = author_text.split('et al.')
                    if parts:
                        author_part = parts[0].strip()
                        # 简单的作者提取逻辑
                        potential_authors = [name.strip() for name in author_part.split(',') if name.strip()]
                        authors.extend(potential_authors[:3])  # 最多取前3个作者
            except:
                pass
        
        return authors
    
    def _extract_authors_from_article_page(self, url: str) -> List[str]:
        """从文章详情页提取作者信息"""
        authors = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尝试多种作者选择器
            author_selectors = [
                'a[data-test="author"]',
                'a[class*="author"]',
                'span[class*="author"]',
                '.c-article-authors a',
                '.c-article-authors span',
                '[data-test="author"]',
                'a[data-track-action="author"]',
                'span[data-track-action="author"]'
            ]
            
            for selector in author_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        author = elem.get_text(strip=True)
                        # 过滤掉非作者信息
                        if (author and len(author) > 2 and 
                            author not in authors and 
                            author not in ['Author notes', 'Search author on:', 'Google Scholar', 
                                         'View author publications', 'Reprints and permissions',
                                         'Language editing services', 'Guide to authors',
                                         'Editorial policies', 'Nature portfolio policies',
                                         'Research data', 'Language editing', 'Scientific editing']):
                            authors.append(author)
                except:
                    continue
            
            # 限制作者数量，避免过多
            if len(authors) > 10:
                authors = authors[:10]
            
        except Exception as e:
            logger.warning(f"从文章页面提取作者失败 {url}: {e}")
        
        return authors
    
    def _parse_selenium_element(self, element, journal_name: str) -> Optional[Article]:
        """解析Selenium元素"""
        try:
            # 提取标题
            title_element = element.find_element(By.CSS_SELECTOR, 'h3, h2, h1')
            title = title_element.text.strip()
            
            if not title:
                return None
            
            # 提取链接
            link_element = element.find_element(By.TAG_NAME, 'a')
            url = link_element.get_attribute('href')
            
            if not url:
                return None
            
            # 提取作者
            authors = []
            # 尝试多种作者选择器
            author_selectors = [
                'a[class*="author"]',
                'span[class*="author"]',
                '.c-article-item__authors a',
                '.c-article-item__authors span',
                '[data-test="author"]',
                'a[href*="author"]'
            ]
            
            for selector in author_selectors:
                try:
                    author_elements = element.find_all('a', class_=lambda x: x and 'author' in x.lower())
                    for author_elem in author_elements:
                        author = author_elem.text.strip()
                        if author and author not in authors:
                            authors.append(author)
                except:
                    continue
            
            # 如果还是没找到作者，尝试其他方法
            if not authors:
                try:
                    # 查找包含作者关键词的文本
                    author_text = element.get_text()
                    if 'et al.' in author_text:
                        # 提取et al.之前的作者
                        parts = author_text.split('et al.')
                        if parts:
                            author_part = parts[0].strip()
                            # 简单的作者提取逻辑
                            potential_authors = [name.strip() for name in author_part.split(',') if name.strip()]
                            authors.extend(potential_authors[:3])  # 最多取前3个作者
                except:
                    pass
            
            # 提取发布时间
            publish_date = datetime.now()
            try:
                date_element = element.find_element(By.TAG_NAME, 'time')
                date_text = date_element.get_attribute('datetime')
                if date_text:
                    publish_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
            except:
                pass
            
            # 提取文章类型
            article_type = ArticleType.RESEARCH_ARTICLE
            try:
                type_element = element.find_element(By.CSS_SELECTOR, 'span[class*="type"]')
                type_text = type_element.text.strip()
                for art_type in ArticleType:
                    if art_type.value.lower() in type_text.lower():
                        article_type = art_type
                        break
            except:
                pass
            
            # 提取摘要
            abstract = ""
            # 尝试多种摘要选择器
            abstract_keywords = ['abstract', 'summary', 'description', 'content']
            
            for keyword in abstract_keywords:
                try:
                    abstract_element = element.find('p', class_=lambda x: x and keyword in x.lower())
                    if abstract_element:
                        abstract = abstract_element.get_text(strip=True)
                        if abstract:
                            break
                except:
                    continue
            
            # 如果还是没找到，尝试查找包含特定关键词的段落
            if not abstract:
                try:
                    paragraphs = element.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 50:  # 摘要通常比较长
                            abstract = text
                            break
                except:
                    pass
            
            return Article(
                title=title,
                authors=authors,
                journal=journal_name,
                url=url,
                abstract=abstract,
                publish_date=publish_date,
                article_type=article_type
            )
            
        except Exception as e:
            logger.warning(f"解析Selenium元素时出错: {e}")
            return None
    
    def _filter_recent_articles(self, articles: List[Article]) -> List[Article]:
        """过滤最近的文章（最近7天）"""
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_articles = []
        
        for article in articles:
            if article.publish_date >= cutoff_date:
                recent_articles.append(article)
        
        return recent_articles
    
    def crawl_all_journals(self) -> List[CrawlResult]:
        """爬取所有启用的期刊"""
        results = []
        
        for journal_config in Config.JOURNALS:
            if journal_config.enabled:
                result = self.crawl_journal(journal_config)
                results.append(result)
                
                # 添加延迟避免被封
                time.sleep(2)
        
        return results
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass 