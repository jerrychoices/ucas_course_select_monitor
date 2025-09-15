"""
日视图组件
显示单日课程安排
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import logging

logger = logging.getLogger(__name__)


class DayViewWidget(QWidget):
    """日视图组件"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = None
        self.init_ui()
    
    def set_database(self, db):
        """设置数据库连接"""
        self.db = db
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 占位符标签
        placeholder = QLabel("日视图 - 功能开发中")
        placeholder.setStyleSheet("font-size: 16px; text-align: center; padding: 20px;")
        layout.addWidget(placeholder)
        
        self.setLayout(layout)
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        # TODO: 实现日视图更新逻辑
