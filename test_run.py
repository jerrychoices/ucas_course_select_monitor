#!/usr/bin/env python3
"""
启动脚本
用于测试重构后的代码
"""

import sys
import os

# 确保添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("项目根目录:", project_root)
print("Python路径:", sys.path[:3])

# 测试导入
try:
    print("\n开始测试导入...")
    
    print("1. 测试数据库模块...")
    from database import CourseDatabase
    print("   ✓ CourseDatabase 导入成功")
    
    print("2. 测试工具模块...")
    from utils import TimeConflictChecker
    print("   ✓ TimeConflictChecker 导入成功")
    
    print("3. 测试导出模块...")
    from export import ScheduleExporter
    print("   ✓ ScheduleExporter 导入成功")
    
    print("4. 测试UI组件...")
    from widgets import MonthViewWidget, WeekViewWidget, DayViewWidget, StatisticsWidget
    print("   ✓ UI组件 导入成功")
    
    print("5. 测试主窗口...")
    from ui import CourseSelectionMainWindow
    print("   ✓ CourseSelectionMainWindow 导入成功")
    
    print("\n✅ 所有模块导入成功！")
    print("\n现在启动主程序...")
    
    # 启动主程序
    from main import main
    main()
    
except ImportError as e:
    print(f"\n❌ 导入错误: {e}")
    print("\n请检查:")
    print("1. requirements.txt 中的依赖是否已安装")
    print("2. 文件路径是否正确")
    print("3. Python路径设置是否正确")
    
except Exception as e:
    print(f"\n❌ 运行错误: {e}")
    import traceback
    traceback.print_exc()
