"""
统计信息组件
显示数据库统计和选课统计信息
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox,
                           QLabel, QProgressBar)
import re
import logging

logger = logging.getLogger(__name__)


class StatisticsWidget(QWidget):
    """统计信息组件"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.selected_courses = []
        self.init_ui()
    
    def set_database(self, db):
        """设置数据库连接"""
        self.db = db
        if self.db:
            self.update_db_stats()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 数据库统计
        db_stats_group = QGroupBox("📊 数据库统计")
        db_stats_layout = QGridLayout()
        
        # 创建统计标签
        self.total_courses_label = QLabel("课程总数: -")
        self.hours_label = QLabel("学时数量: -")
        self.schedules_label = QLabel("时间安排: -")
        
        # 设置样式
        label_style = """
            QLabel {
                font-size: 12px; 
                padding: 8px; 
                background-color: #f0f8ff; 
                border-radius: 6px;
                border: 1px solid #e0e6ed;
            }
        """
        
        for label in [self.total_courses_label, self.hours_label, self.schedules_label]:
            label.setStyleSheet(label_style)
        
        db_stats_layout.addWidget(self.total_courses_label, 0, 0)
        db_stats_layout.addWidget(self.hours_label, 0, 1)
        db_stats_layout.addWidget(self.schedules_label, 1, 0)
        
        db_stats_group.setLayout(db_stats_layout)
        layout.addWidget(db_stats_group)
        
        # 选课统计
        selection_stats_group = QGroupBox("📈 选课统计")
        selection_stats_layout = QVBoxLayout()
        
        self.selected_count_label = QLabel("已选课程: 0")
        self.total_credits_label = QLabel("总学分: 0")
        self.conflict_count_label = QLabel("时间冲突: 0")
        
        # 进度条
        self.credits_progress = QProgressBar()
        self.credits_progress.setRange(0, 30)
        self.credits_progress.setValue(0)
        self.credits_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        for label in [self.selected_count_label, self.total_credits_label, self.conflict_count_label]:
            label.setStyleSheet("font-size: 12px; padding: 5px;")
        
        selection_stats_layout.addWidget(self.selected_count_label)
        selection_stats_layout.addWidget(self.total_credits_label)
        selection_stats_layout.addWidget(QLabel("学分进度:"))
        selection_stats_layout.addWidget(self.credits_progress)
        selection_stats_layout.addWidget(self.conflict_count_label)
        
        selection_stats_group.setLayout(selection_stats_layout)
        layout.addWidget(selection_stats_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_db_stats(self):
        """更新数据库统计信息"""
        if not self.db:
            return
        
        try:
            stats = self.db.get_statistics()
            self.total_courses_label.setText(f"课程总数: {stats['total_courses']}")
            self.hours_label.setText(f"学时数量: {stats['hours']}")
            self.schedules_label.setText(f"时间安排: {stats['schedules']}")
        except Exception as e:
            logger.error(f"Failed to update database statistics: {e}")
    
    def update_selection_stats(self, selected_courses, conflicts_count=0):
        """更新选课统计"""
        self.selected_courses = selected_courses
        
        if not self.db:
            return
        
        # 计算总学分
        total_credits = 0
        try:
            for course_id, _ in selected_courses:
                courses = self.db.get_all_courses()
                for course in courses:
                    if course[0] == course_id:
                        credits_str = course[2] or "0"  # credits是第2列
                        credits_match = re.search(r'\d+', str(credits_str))
                        if credits_match:
                            total_credits += int(credits_match.group())
                        break
        except Exception as e:
            logger.error(f"Failed to calculate credits: {e}")
        
        # 更新标签
        self.selected_count_label.setText(f"已选课程: {len(selected_courses)}")
        self.total_credits_label.setText(f"总学分: {total_credits}")
        self.conflict_count_label.setText(f"时间冲突: {conflicts_count}")
        
        # 更新进度条
        self.credits_progress.setValue(min(total_credits, 30))
        
        # 根据冲突数量设置颜色
        if conflicts_count > 0:
            self.conflict_count_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 12px; padding: 5px;")
        else:
            self.conflict_count_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 12px; padding: 5px;")
