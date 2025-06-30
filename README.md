# Nature 系列期刊 AI 日报系统

[English Version (README.en.md)](./README.en.md)

---

## 目录
- [项目简介](#项目简介)
- [主要功能](#主要功能)
- [安装与环境配置](#安装与环境配置)
- [快速开始](#快速开始)
- [命令行参数说明](#命令行参数说明)
- [环境变量说明](#环境变量说明)
- [输出与报告格式](#输出与报告格式)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

本项目为 Nature 系列期刊自动化 AI 日报系统，支持自动爬取 Nature 及其子刊（如 Nature Communications、Materials、Photonics 等）最新文章，利用 DeepSeek API 进行智能摘要与关键点提取，自动生成结构化日报（Markdown/HTML），并支持邮件推送。

---

## 主要功能
- 支持多期刊自动采集、定时任务
- DeepSeek API 智能摘要与要点提取
- 支持自定义日期生成日报
- 支持 Markdown/HTML/JSON 多格式输出
- 邮件推送（支持多收件人、密送）
- 日志记录与错误追踪
- 支持按期刊分类展示，包含作者、通讯作者、作者单位等信息

---

## 安装与环境配置

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd NatureSerials
   ```
2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
3. **配置环境变量**
   - 复制 `env_example.txt` 为 `.env`，并填写你的 DeepSeek API Key、邮箱等信息。
   - 或直接设置系统环境变量。

---

## 快速开始

### 立即生成当天日报
```bash
python main.py --once
```

### 生成指定日期的日报（如 2025-06-27）
```bash
python main.py --once --date 2025-06-27
```

### 启动定时任务（每天定时自动生成）
```bash
python main.py --schedule
```

### 运行系统测试
```bash
python test_system.py
```

---

## 命令行参数说明
| 参数 | 说明 |
|------|------|
| --once | 立即生成一次日报 |
| --date YYYY-MM-DD | 指定生成哪天的日报（不指定则为当天） |
| --schedule | 启动定时任务（按配置时间自动生成） |
| --test | 运行系统测试 |
| --selenium | 使用 Selenium 爬虫（如遇反爬可用） |

---

## 环境变量说明
| 变量名 | 说明 |
|--------|------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 |
| DEEPSEEK_MODEL | 使用的模型（默认 deepseek-chat）|
| SMTP_SERVER | 邮箱SMTP服务器 |
| SMTP_PORT | 邮箱端口（如587）|
| EMAIL_USERNAME | 邮箱用户名 |
| EMAIL_PASSWORD | 邮箱密码 |
| EMAIL_RECIPIENTS | 收件人列表（逗号分隔）|
| EMAIL_BCC | 密送收件人列表（可选）|
| ENABLE_EMAIL_SENDING | 是否启用邮件发送（true/false）|
| OUTPUT_FORMAT | 输出格式（markdown/html/json/all）|

---

## 输出与报告格式
- **Markdown/HTML/JSON** 文件自动保存在 `output/` 目录
- 文件名格式：`nature_daily_report_YYYYMMDD.md`（与日报日期一致）
- Markdown 报告示例：

```markdown
# Nature 系列科研日报 - 2025/06/27

## 📊 今日概览
- **总文章数**: 10 篇
- **覆盖期刊**: 3 个

## 🔬 按期刊分类

### Nature Communications
#### 文章标题示例
- **期刊**: Nature Communications
- **作者**: 张三, 李四, 王五
- **通讯作者**: 张三
- **作者单位**: 清华大学; 北京大学
- **文章类型**: Research Article
- **发布日期**: 2025-06-27
- **原文链接**: [https://www.nature.com/xxx](https://www.nature.com/xxx)

**摘要**: ...

**关键贡献点**:
- 贡献点1
- 贡献点2

---
```

---

## 常见问题
1. **爬虫未获取到新文章**
   - 检查网络连接，或目标期刊当天无新文章
2. **AI摘要/关键点生成失败**
   - 检查 DeepSeek API Key 是否正确、配额是否充足
   - 查看 `logs/ai_summarizer.log` 日志
3. **邮件发送失败**
   - 检查邮箱配置、SMTP端口、防火墙
4. **如何只生成Markdown？**
   - 设置环境变量 `OUTPUT_FORMAT=markdown`

---

## 贡献指南
- 欢迎提交 Issue 和 Pull Request
- 建议先在 dev 分支开发和测试
- 代码需通过 `test_system.py` 测试

---

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。 