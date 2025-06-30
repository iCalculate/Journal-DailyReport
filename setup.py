"""
Nature 系列期刊 AI 日报系统设置脚本
帮助用户快速配置和部署系统
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🌐 Nature 系列期刊 AI 日报系统")
    print("=" * 60)
    print("一个自动化抓取 Nature 及其子刊每日发布的新文章，")
    print("利用 DeepSeek API 对文章进行总结分析，")
    print("最终生成结构化日报内容并自动发送至指定邮箱的科研动态推送系统。")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    else:
        print(f"✅ Python版本检查通过: {sys.version}")
        return True

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    print("📁 创建必要的目录...")
    directories = ["output", "logs", "templates"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True

def setup_environment():
    """设置环境变量"""
    print("⚙️ 设置环境变量...")
    
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("⚠️  .env文件已存在，跳过创建")
        return True
    
    if not env_example.exists():
        print("❌ env_example.txt文件不存在")
        return False
    
    # 复制示例文件
    shutil.copy(env_example, env_file)
    print("✅ 已创建.env文件")
    
    print("\n📝 请编辑.env文件，填写以下配置:")
    print("1. DeepSeek API密钥 (DEEPSEEK_API_KEY)")
    print("2. 邮箱配置 (SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD等)")
    print("3. 收件人列表 (EMAIL_RECIPIENTS)")
    
    return True

def run_tests():
    """运行系统测试"""
    print("🧪 运行系统测试...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 系统测试通过")
            return True
        else:
            print("❌ 系统测试失败")
            print("错误信息:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def show_usage():
    """显示使用说明"""
    print("\n🚀 系统设置完成！")
    print("\n📖 使用说明:")
    print("1. 编辑.env文件，配置API密钥和邮箱信息")
    print("2. 运行测试: python test_system.py")
    print("3. 立即运行一次: python main.py --once")
    print("4. 启动定时任务: python main.py --schedule")
    print("5. 查看帮助: python main.py --help")
    
    print("\n📧 邮件配置示例:")
    print("Outlook邮箱:")
    print("  SMTP_SERVER=smtp.office365.com")
    print("  SMTP_PORT=587")
    print("  EMAIL_USERNAME=your_email@outlook.com")
    print("  EMAIL_PASSWORD=your_password")
    
    print("\nGmail邮箱:")
    print("  SMTP_SERVER=smtp.gmail.com")
    print("  SMTP_PORT=587")
    print("  EMAIL_USERNAME=your_email@gmail.com")
    print("  EMAIL_PASSWORD=your_app_password")
    
    print("\n📁 输出文件:")
    print("- output/: 生成的报告文件")
    print("- logs/: 系统日志文件")
    print("- templates/: 报告模板文件")
    
    print("\n🔗 相关链接:")
    print("- DeepSeek API: https://www.deepseek.com/")
    print("- 项目文档: README.md")
    print("- 问题反馈: 请提交Issue")

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 创建目录
    if not create_directories():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 设置环境变量
    if not setup_environment():
        return False
    
    # 运行测试
    if not run_tests():
        print("⚠️ 系统测试失败，但安装已完成")
        print("请检查配置后重新运行测试")
    
    # 显示使用说明
    show_usage()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 系统设置完成！")
        else:
            print("\n❌ 系统设置失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断设置")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 设置过程中发生错误: {e}")
        sys.exit(1) 