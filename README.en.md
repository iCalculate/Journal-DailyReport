# Nature Series Journals AI Daily Report System

[中文版 (README.md)](./README.md)

---

## Table of Contents
- [Project Overview](#project-overview)
- [Main Features](#main-features)
- [Installation & Environment Setup](#installation--environment-setup)
- [Quick Start](#quick-start)
- [Command Line Arguments](#command-line-arguments)
- [Environment Variables](#environment-variables)
- [Output & Report Format](#output--report-format)
- [FAQ](#faq)
- [Contribution Guide](#contribution-guide)
- [License](#license)

---

## Project Overview

This project is an automated AI daily report system for Nature series journals. It supports automatic crawling of the latest articles from Nature and its sub-journals (such as Nature Communications, Materials, Photonics, etc.), uses the DeepSeek API for intelligent summarization and key point extraction, and automatically generates structured daily reports (Markdown/HTML) with optional email delivery.

---

## Main Features
- Multi-journal automatic crawling and scheduling
- DeepSeek API for intelligent summarization and key point extraction
- Custom date support for report generation
- Supports Markdown/HTML/JSON output formats
- Email delivery (multiple recipients, BCC supported)
- Logging and error tracking
- Journal-based classification, including author, corresponding author, and affiliation information

---

## Installation & Environment Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd NatureSerials
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Copy `env_example.txt` to `.env` and fill in your DeepSeek API Key, email, etc.
   - Or set environment variables directly in your system.

---

## Quick Start

### Generate today's daily report
```bash
python main.py --once
```

### Generate report for a specific date (e.g., 2025-06-27)
```bash
python main.py --once --date 2025-06-27
```

### Start scheduled task (auto-generate daily)
```bash
python main.py --schedule
```

### Run system tests
```bash
python test_system.py
```

---

## Command Line Arguments
| Argument | Description |
|----------|-------------|
| --once | Generate a daily report immediately |
| --date YYYY-MM-DD | Specify which day's report to generate (default: today) |
| --schedule | Start scheduled task (auto-generate at configured time) |
| --test | Run system tests |
| --selenium | Use Selenium crawler (for anti-crawling pages) |

---

## Environment Variables
| Variable | Description |
|----------|-------------|
| DEEPSEEK_API_KEY | DeepSeek API key |
| DEEPSEEK_MODEL | Model to use (default: deepseek-chat) |
| SMTP_SERVER | Email SMTP server |
| SMTP_PORT | Email port (e.g., 587) |
| EMAIL_USERNAME | Email username |
| EMAIL_PASSWORD | Email password |
| EMAIL_RECIPIENTS | Recipients (comma-separated) |
| EMAIL_BCC | BCC recipients (optional) |
| ENABLE_EMAIL_SENDING | Enable email sending (true/false) |
| OUTPUT_FORMAT | Output format (markdown/html/json/all) |

---

## Output & Report Format
- **Markdown/HTML/JSON** files are saved in the `output/` directory
- Filename format: `nature_daily_report_YYYYMMDD.md` (matches report date)
- Markdown report example:

```markdown
# Nature Series Science Daily Report - 2025/06/27

## 📊 Overview
- **Total articles**: 10
- **Journals covered**: 3

## 🔬 By Journal

### Nature Communications
#### Example Article Title
- **Journal**: Nature Communications
- **Authors**: Zhang San, Li Si, Wang Wu
- **Corresponding Author**: Zhang San
- **Affiliations**: Tsinghua University; Peking University
- **Article Type**: Research Article
- **Publish Date**: 2025-06-27
- **Original Link**: [https://www.nature.com/xxx](https://www.nature.com/xxx)

**Summary**: ...

**Key Contributions**:
- Point 1
- Point 2

---
```

---

## FAQ
1. **No new articles found by crawler**
   - Check your network or there may be no new articles for the selected date
2. **AI summary/key point generation failed**
   - Check if your DeepSeek API Key is correct and quota is sufficient
   - See `logs/ai_summarizer.log` for details
3. **Email sending failed**
   - Check email configuration, SMTP port, firewall
4. **How to generate only Markdown?**
   - Set environment variable `OUTPUT_FORMAT=markdown`

---

## Contribution Guide
- Pull requests and issues are welcome
- Please develop and test on the dev branch first
- Code must pass `test_system.py`

---

## License

This project is licensed under the MIT License. See LICENSE for details. 