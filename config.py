# 配置文件
# 程序运行的各项配置参数

import os

# 数据库配置
DATABASE_PATH = "ucas_courses_new.db"

# 应用配置
APP_NAME = "UCAS课程选择模拟器"
APP_VERSION = "2.0.0"

# 界面配置
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1000
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800

# 学期配置
SEMESTER_START_DATE = "2025-09-01"  # 学期开始日期
MAX_CREDITS = 30  # 建议最大学分

# 导出配置
EXPORT_DIR = "exports"  # 默认导出目录
SUPPORTED_EXPORT_FORMATS = {
    'csv': 'CSV文件 (*.csv)',
    'xlsx': 'Excel文件 (*.xlsx)', 
    'pdf': 'PDF文件 (*.pdf)',
    'json': 'JSON文件 (*.json)'
}

# 时间节次映射
TIME_SLOTS = {
    1: "08:00-08:50", 2: "09:00-09:50", 3: "10:10-11:00", 4: "11:10-12:00",
    5: "14:00-14:50", 6: "15:00-15:50", 7: "16:10-17:00", 8: "17:10-18:00",
    9: "19:00-19:50", 10: "20:00-20:50", 11: "21:00-21:50"
}

# 星期映射
WEEKDAYS = {
    1: "周一", 2: "周二", 3: "周三", 4: "周四",
    5: "周五", 6: "周六", 7: "周日"
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 创建导出目录
def ensure_export_dir():
    """确保导出目录存在"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        
# 获取导出文件路径
def get_export_path(filename):
    """获取导出文件的完整路径"""
    ensure_export_dir()
    return os.path.join(EXPORT_DIR, filename)
