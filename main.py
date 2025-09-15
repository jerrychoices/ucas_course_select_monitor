#!/usr/bin/env python3
"""
UCAS课程选择模拟器
重构后的模块化版本
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    try:
        # 创建QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("UCAS课程选择模拟器")
        app.setApplicationVersion("2.0.0")
        
        # 设置高DPI支持
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 导入并创建主窗口
        from ui import CourseSelectionMainWindow
        
        window = CourseSelectionMainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖包已正确安装")
        print("运行: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"程序运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
