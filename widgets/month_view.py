"""
月视图组件 - 类似苹果日历的月视图
显示课程在月历中的安排
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QPushButton, QLabel)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class MonthViewWidget(QWidget):
    """月视图组件 - 类似苹果日历的月视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = None
        self.current_month = 9  # 当前月份
        self.current_year = 2025  # 当前年份
        self.semester_start_date = QDate(2025, 9, 1)  # 学期开始日期
        self.init_ui()
    
    def set_database(self, db):
        """设置数据库连接"""
        self.db = db
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_bar = QHBoxLayout()
        
        # 月份导航
        self.prev_month_btn = QPushButton("◀")
        self.prev_month_btn.setMaximumWidth(40)
        self.prev_month_btn.clicked.connect(self.prev_month)
        control_bar.addWidget(self.prev_month_btn)
        
        # 当前月份显示
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.update_month_label()
        control_bar.addWidget(self.month_label)
        
        self.next_month_btn = QPushButton("▶")
        self.next_month_btn.setMaximumWidth(40)
        self.next_month_btn.clicked.connect(self.next_month)
        control_bar.addWidget(self.next_month_btn)
        
        # 今天按钮
        today_btn = QPushButton("本月")
        today_btn.clicked.connect(self.go_to_current_month)
        control_bar.addWidget(today_btn)
        
        control_bar.addStretch()
        layout.addLayout(control_bar)
        
        # 月历表格
        self.calendar_table = QTableWidget(6, 7)  # 6周 x 7天
        
        # 设置表头（星期）
        headers = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.calendar_table.setHorizontalHeaderLabels(headers)
        self.calendar_table.verticalHeader().setVisible(False)
        
        # 设置表格属性
        self.calendar_table.setSelectionMode(QTableWidget.NoSelection)
        self.calendar_table.horizontalHeader().setStretchLastSection(True)
        # 设置不可编辑
        self.calendar_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置行高和列宽
        for i in range(6):
            self.calendar_table.setRowHeight(i, 120)
        for i in range(7):
            self.calendar_table.setColumnWidth(i, 120)
        
        # 美化表格样式
        self.calendar_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QTableWidget::item {
                border: 1px solid #f0f0f0;
                padding: 2px;
                vertical-align: top;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.calendar_table)
        self.setLayout(layout)
        
        # 初始化日历
        self.update_calendar()
    
    def update_month_label(self):
        """更新月份标签"""
        month_names = ['', '一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月']
        self.month_label.setText(f"{self.current_year}年 {month_names[self.current_month]}")
    
    def prev_month(self):
        """上一月"""
        if self.current_month > 1:
            self.current_month -= 1
        else:
            self.current_month = 12
            self.current_year -= 1
        self.update_month_label()
        self.update_calendar()
    
    def next_month(self):
        """下一月"""
        if self.current_month < 12:
            self.current_month += 1
        else:
            self.current_month = 1
            self.current_year += 1
        self.update_month_label()
        self.update_calendar()
    
    def go_to_current_month(self):
        """回到当前月"""
        current_date = QDate.currentDate()
        self.current_year = current_date.year()
        self.current_month = current_date.month()
        self.update_month_label()
        self.update_calendar()
    
    def update_calendar(self):
        """更新日历显示"""
        # 清空表格
        for row in range(6):
            for col in range(7):
                self.calendar_table.setItem(row, col, QTableWidgetItem(""))
        
        # 获取当月第一天
        first_day = QDate(self.current_year, self.current_month, 1)
        
        # 计算第一天是星期几 (1=周一, 7=周日)
        first_weekday = first_day.dayOfWeek()
        
        # 获取当月天数
        days_in_month = first_day.daysInMonth()
        
        # 填充日期
        current_date = 1
        for week in range(6):
            for day in range(7):
                if week == 0 and day < first_weekday - 1:
                    # 月份开始前的空白
                    continue
                elif current_date > days_in_month:
                    # 月份结束后的空白
                    break
                else:
                    # 创建日期单元格
                    date_widget = self.create_date_cell(current_date)
                    self.calendar_table.setCellWidget(week, day, date_widget)
                    current_date += 1
    
    def create_date_cell(self, day):
        """创建日期单元格"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)
        
        # 日期标签
        date_label = QLabel(str(day))
        date_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        date_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        # 检查是否是今天
        today = QDate.currentDate()
        if (self.current_year == today.year() and 
            self.current_month == today.month() and 
            day == today.day()):
            date_label.setStyleSheet("color: #007bff; background-color: #e3f2fd; border-radius: 10px; padding: 2px;")
        else:
            date_label.setStyleSheet("color: #333;")
        
        layout.addWidget(date_label)
        
        # 计算这一天对应的学期周次
        current_date = QDate(self.current_year, self.current_month, day)
        week_number = self.get_week_number(current_date)
        
        if week_number > 0 and self.db:
            # 显示这一天的课程
            courses_text = self.get_courses_for_day(current_date.dayOfWeek(), week_number)
            if courses_text:
                course_label = QLabel(courses_text)
                course_label.setWordWrap(True)
                course_label.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e9;
                        color: #2e7d32;
                        font-size: 8px;
                        padding: 1px;
                        border-radius: 2px;
                        margin: 1px;
                    }
                """)
                layout.addWidget(course_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def get_week_number(self, date):
        """计算日期对应的学期周次"""
        days_diff = self.semester_start_date.daysTo(date)
        if days_diff < 0:
            return 0
        return (days_diff // 7) + 1
    
    def get_courses_for_day(self, day_of_week, week_number):
        """获取指定日期的课程"""
        if not self.db:
            return ""
        
        courses_text = ""
        
        try:
            for course_id, course_name in self.selected_courses:
                schedules = self.db.get_course_schedules(course_id)
                
                for schedule in schedules:
                    sched_day, time_slots, location, weeks, semester = schedule
                    
                    # 检查星期是否匹配
                    if str(sched_day) != str(day_of_week):
                        continue
                    
                    # 检查周次是否匹配 (简化版本)
                    if weeks and str(week_number) in str(weeks):
                        # 添加课程信息
                        if courses_text:
                            courses_text += "\n"
                        courses_text += f"{course_name[:6]}..."
                        break
        except Exception as e:
            logger.error(f"Error getting courses for day: {e}")
        
        return courses_text
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        self.update_calendar()
