"""
邮件发送模块
发送生成的日报到指定邮箱
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from src.config import EmailConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_sender.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailSender:
    """邮件发送器"""
    
    def __init__(self, email_config: EmailConfig):
        """
        初始化邮件发送器
        
        Args:
            email_config: 邮件配置
        """
        self.email_config = email_config
    
    def send_daily_report(self, html_content: str, markdown_content: str, 
                         subject: str = None, attachments: List[str] = None) -> bool:
        """
        发送日报邮件
        
        Args:
            html_content: HTML内容
            markdown_content: Markdown内容
            subject: 邮件主题
            attachments: 附件列表
            
        Returns:
            bool: 发送是否成功
        """
        if not subject:
            subject = f"Nature 系列科研日报 - {datetime.now().strftime('%Y/%m/%d')}"
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_config.username
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 设置收件人
            if self.email_config.recipients:
                msg['To'] = ', '.join(self.email_config.recipients)
            
            # 设置密送
            if self.email_config.bcc_recipients:
                msg['Bcc'] = ', '.join(self.email_config.bcc_recipients)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加纯文本内容（备用）
            text_part = MIMEText(markdown_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加附件
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)
            
            # 发送邮件
            return self._send_email(msg)
            
        except Exception as e:
            logger.error(f"发送日报邮件失败: {e}")
            return False
    
    def send_test_email(self, test_content: str = "这是一封测试邮件") -> bool:
        """
        发送测试邮件
        
        Args:
            test_content: 测试内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_config.username
            msg['Subject'] = Header("Nature 系列期刊 AI 日报系统 - 测试邮件", 'utf-8')
            
            if self.email_config.recipients:
                msg['To'] = ', '.join(self.email_config.recipients)
            
            # 添加HTML内容
            html_content = f"""
            <html>
            <body>
                <h2>Nature 系列期刊 AI 日报系统</h2>
                <p>{test_content}</p>
                <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>如果您收到这封邮件，说明邮件配置正确。</p>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            text_part = MIMEText(test_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            return self._send_email(msg)
            
        except Exception as e:
            logger.error(f"发送测试邮件失败: {e}")
            return False
    
    def _send_email(self, msg: MIMEMultipart) -> bool:
        """
        发送邮件
        
        Args:
            msg: 邮件对象
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 连接SMTP服务器
            server = smtplib.SMTP(self.email_config.smtp_server, self.email_config.smtp_port)
            server.starttls()  # 启用TLS加密
            
            # 登录
            server.login(self.email_config.username, self.email_config.password)
            
            # 获取所有收件人
            recipients = self.email_config.recipients.copy()
            if self.email_config.bcc_recipients:
                recipients.extend(self.email_config.bcc_recipients)
            
            # 发送邮件
            server.sendmail(self.email_config.username, recipients, msg.as_string())
            
            # 关闭连接
            server.quit()
            
            logger.info(f"邮件发送成功，收件人: {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """
        添加附件
        
        Args:
            msg: 邮件对象
            file_path: 文件路径
        """
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(file_path).name}'
            )
            msg.attach(part)
            
            logger.info(f"附件添加成功: {file_path}")
            
        except Exception as e:
            logger.error(f"添加附件失败: {file_path}, 错误: {e}")
    
    def validate_config(self) -> bool:
        """
        验证邮件配置
        
        Returns:
            bool: 配置是否有效
        """
        if not self.email_config.username or not self.email_config.password:
            logger.error("邮箱用户名或密码未配置")
            return False
        
        if not self.email_config.recipients:
            logger.error("收件人列表为空")
            return False
        
        if not self.email_config.smtp_server or not self.email_config.smtp_port:
            logger.error("SMTP服务器配置不完整")
            return False
        
        return True 