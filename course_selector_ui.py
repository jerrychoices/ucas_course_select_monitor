import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                           QLineEdit, QLabel, QComboBox, QTextEdit, QSplitter,
                           QHeaderView, QMessageBox, QTabWidget, QGridLayout,
                           QCheckBox, QScrollArea, QFrame, QSpinBox, QGroupBox,
                           QProgressBar, QListWidget, QListWidgetItem, QDialog,
                           QDialogButtonBox, QFormLayout, QCalendarWidget,
                           QButtonGroup, QRadioButton, QStackedWidget, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate, QRect
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QPen, QPalette
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class MonthViewWidget(QWidget):
    """月视图组件 - 类似苹果日历的月视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = CourseDatabase()
        self.current_month = 9  # 当前月份
        self.current_year = 2025  # 当前年份
        self.semester_start_date = QDate(2025, 9, 1)  # 学期开始日期
        self.init_ui()
    
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
        
        if week_number > 0:
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
        courses_text = ""
        
        for course_id, course_name in self.selected_courses:
            schedules = self.db.get_course_schedules(course_id)
            
            for schedule in schedules:
                sched_day, time_slots, location, weeks, semester = schedule
                
                # 检查星期是否匹配
                if str(sched_day) != str(day_of_week):
                    continue
                
                # 检查周次是否匹配
                weeks_list = TimeConflictChecker.parse_weeks(weeks)
                if week_number not in weeks_list:
                    continue
                
                # 添加课程信息
                if courses_text:
                    courses_text += "\n"
                courses_text += f"{course_name[:6]}..."
        
        return courses_text
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        self.update_calendar()


class CourseDatabase:
    """数据库操作类"""
    
    def __init__(self, db_path="ucas_courses_new.db"):
        self.db_path = db_path
    
    def get_all_courses(self):
        """获取所有课程 - 修改后的结构：去除teacher列"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT DISTINCT c.id, c.course_name, c.credits, c.hours, c.course_code
            FROM courses c
            ORDER BY c.course_name
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_course_schedules(self, course_id):
        """获取特定课程的时间安排"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT day_of_week, time_slots, location, weeks, semester
            FROM course_schedules
            WHERE course_id = ?
        '''
        cursor.execute(query, (course_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_courses(self, keyword="", department=""):
        """搜索课程 - 移除teacher参数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT DISTINCT c.id, c.course_name, c.credits, c.hours, c.course_code
            FROM courses c
            WHERE 1=1
        '''
        params = []
        
        if keyword:
            query += ' AND (c.course_name LIKE ? OR c.course_code LIKE ?)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        if department:
            query += ' AND c.hours LIKE ?'
            params.append(f'%{department}%')
        
        query += ' ORDER BY c.course_name'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_statistics(self):
        """获取数据库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 课程总数
        cursor.execute('SELECT COUNT(*) FROM courses')
        stats['total_courses'] = cursor.fetchone()[0]
        
        # 学时数量
        cursor.execute('SELECT COUNT(DISTINCT hours) FROM courses WHERE hours IS NOT NULL AND hours != ""')
        stats['hours'] = cursor.fetchone()[0]
        
        # 时间安排数量
        cursor.execute('SELECT COUNT(*) FROM course_schedules')
        stats['schedules'] = cursor.fetchone()[0]
        
        conn.close()
        return stats

class TimeConflictChecker:
    """时间冲突检查器"""
    
    @staticmethod
    def parse_time_slots(time_slots_str):
        """解析时间段字符串，返回时间段列表"""
        if not time_slots_str:
            return []
        
        import re
        numbers = re.findall(r'\d+', time_slots_str)
        time_slots = []
        
        if len(numbers) >= 2:
            start = int(numbers[0])
            end = int(numbers[-1])
            time_slots = list(range(start, end + 1))
        elif len(numbers) == 1:
            time_slots = [int(numbers[0])]
        
        return time_slots
    
    @staticmethod
    def parse_weeks(weeks_str):
        """解析周次字符串，返回周次列表"""
        if not weeks_str:
            return []
        
        import re
        numbers = re.findall(r'\d+', weeks_str)
        return [int(n) for n in numbers]
    
    @staticmethod
    def check_conflict(schedule1, schedule2):
        """检查两个课程安排是否冲突"""
        day1, time1, _, weeks1, _ = schedule1
        day2, time2, _, weeks2, _ = schedule2
        
        if day1 != day2:
            return False
        
        slots1 = TimeConflictChecker.parse_time_slots(time1)
        slots2 = TimeConflictChecker.parse_time_slots(time2)
        weeks_list1 = TimeConflictChecker.parse_weeks(weeks1)
        weeks_list2 = TimeConflictChecker.parse_weeks(weeks2)
        
        time_overlap = bool(set(slots1) & set(slots2))
        week_overlap = bool(set(weeks_list1) & set(weeks_list2))
        
        return time_overlap and week_overlap

class DayViewWidget(QWidget):
    """日视图组件 - 类似苹果日历的日视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = CourseDatabase()
        self.current_week = 1
        self.current_day = 1  # 1=周一, 7=周日
        self.total_weeks = 18
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_bar = QHBoxLayout()
        
        # 日期导航
        self.prev_day_btn = QPushButton("◀")
        self.prev_day_btn.setMaximumWidth(40)
        self.prev_day_btn.clicked.connect(self.prev_day)
        control_bar.addWidget(self.prev_day_btn)
        
        # 当前日期显示
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.update_date_label()
        control_bar.addWidget(self.date_label)
        
        self.next_day_btn = QPushButton("▶")
        self.next_day_btn.setMaximumWidth(40)
        self.next_day_btn.clicked.connect(self.next_day)
        control_bar.addWidget(self.next_day_btn)
        
        # 周次选择
        control_bar.addWidget(QLabel("周次:"))
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, self.total_weeks)
        self.week_spinbox.setValue(self.current_week)
        self.week_spinbox.valueChanged.connect(self.change_week)
        control_bar.addWidget(self.week_spinbox)
        
        # 今天按钮
        today_btn = QPushButton("今天")
        today_btn.clicked.connect(self.go_to_today)
        control_bar.addWidget(today_btn)
        
        control_bar.addStretch()
        layout.addLayout(control_bar)
        
        # 时间轴和课程显示区域
        content_area = QHBoxLayout()
        
        # 左侧时间轴
        time_axis = QVBoxLayout()
        time_axis.setSpacing(0)
        
        # 创建时间标签
        self.time_slots = [
            ('08:30', '09:15'), ('09:20', '10:05'), ('10:25', '11:10'),
            ('11:15', '12:00'), ('13:30', '14:15'), ('14:20', '15:05'),
            ('15:25', '16:10'), ('16:15', '17:00'), ('17:20', '18:05'),
            ('18:10', '18:55'), ('19:20', '20:05'), ('20:10', '20:55'),
            ('21:00', '21:45')
        ]
        
        for i, (start_time, end_time) in enumerate(self.time_slots):
            time_label = QLabel(f"{start_time}\n{end_time}")
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setMinimumWidth(80)
            time_label.setMaximumWidth(80)
            time_label.setMinimumHeight(60)
            time_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #e0e0e0;
                    background-color: #f8f9fa;
                    font-size: 10px;
                    color: #666;
                }
            """)
            time_axis.addWidget(time_label)
        
        content_area.addLayout(time_axis)
        
        # 右侧课程显示区域
        self.course_area = QScrollArea()
        self.course_widget = QWidget()
        self.course_layout = QVBoxLayout(self.course_widget)
        self.course_layout.setSpacing(0)
        
        # 创建课程槽位
        self.course_slots = []
        for i in range(13):
            slot = QLabel()
            slot.setMinimumHeight(60)
            slot.setStyleSheet("""
                QLabel {
                    border: 1px solid #e0e0e0;
                    background-color: white;
                    margin: 0px;
                }
            """)
            self.course_slots.append(slot)
            self.course_layout.addWidget(slot)
        
        self.course_area.setWidget(self.course_widget)
        self.course_area.setWidgetResizable(True)
        content_area.addWidget(self.course_area)
        
        layout.addLayout(content_area)
        self.setLayout(layout)
    
    def update_date_label(self):
        """更新日期标签"""
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.date_label.setText(f"{day_names[self.current_day-1]} - 第{self.current_week}周")
    
    def prev_day(self):
        """上一天"""
        if self.current_day > 1:
            self.current_day -= 1
        else:
            self.current_day = 7
            if self.current_week > 1:
                self.current_week -= 1
                self.week_spinbox.setValue(self.current_week)
        self.update_date_label()
        self.update_schedule(self.selected_courses)
    
    def next_day(self):
        """下一天"""
        if self.current_day < 7:
            self.current_day += 1
        else:
            self.current_day = 1
            if self.current_week < self.total_weeks:
                self.current_week += 1
                self.week_spinbox.setValue(self.current_week)
        self.update_date_label()
        self.update_schedule(self.selected_courses)
    
    def change_week(self, week):
        """改变周次"""
        self.current_week = week
        self.update_date_label()
        self.update_schedule(self.selected_courses)
    
    def go_to_today(self):
        """回到今天"""
        self.current_week = 1
        self.current_day = 1
        self.week_spinbox.setValue(self.current_week)
        self.update_date_label()
        self.update_schedule(self.selected_courses)
    
    def update_schedule(self, selected_courses):
        """更新日程显示"""
        self.selected_courses = selected_courses
        
        # 清空所有槽位
        for slot in self.course_slots:
            slot.setText("")
            slot.setStyleSheet("""
                QLabel {
                    border: 1px solid #e0e0e0;
                    background-color: white;
                    margin: 0px;
                }
            """)
        
        # 填入当天的课程
        for course_id, course_name in selected_courses:
            schedules = self.db.get_course_schedules(course_id)
            
            for schedule in schedules:
                day_of_week, time_slots, location, weeks, semester = schedule
                
                # 检查是否是当前显示的天
                if str(day_of_week) != str(self.current_day):
                    continue
                
                # 检查当前周是否在课程周次范围内
                weeks_list = TimeConflictChecker.parse_weeks(weeks)
                if self.current_week not in weeks_list:
                    continue
                
                # 解析时间段
                slots = TimeConflictChecker.parse_time_slots(time_slots)
                
                # 生成课程显示文本
                course_text = f"{course_name}\n{location or ''}\n第{time_slots}节"
                
                # 为每个时间段设置课程信息
                for slot in slots:
                    if 1 <= slot <= 13:
                        slot_index = slot - 1
                        
                        # 检查是否已有课程（冲突）
                        if self.course_slots[slot_index].text():
                            # 冲突情况
                            current_text = self.course_slots[slot_index].text()
                            self.course_slots[slot_index].setText(f"{current_text}\n[冲突]{course_name[:8]}")
                            self.course_slots[slot_index].setStyleSheet("""
                                QLabel {
                                    border: 2px solid #ff4444;
                                    background-color: #ffe6e6;
                                    color: #cc0000;
                                    padding: 5px;
                                    font-weight: bold;
                                    font-size: 10px;
                                }
                            """)
                        else:
                            # 正常情况
                            self.course_slots[slot_index].setText(course_text)
                            self.course_slots[slot_index].setStyleSheet("""
                                QLabel {
                                    border: 2px solid #4CAF50;
                                    background-color: #e8f5e9;
                                    color: #2e7d32;
                                    padding: 5px;
                                    font-weight: bold;
                                    font-size: 10px;
                                    border-radius: 4px;
                                }
                            """)


class WeekViewWidget(QWidget):
    """周视图组件 - 改进的周视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = CourseDatabase()
        self.current_week = 1
        self.total_weeks = 18
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_bar = QHBoxLayout()
        
        # 周次导航
        self.prev_week_btn = QPushButton("◀ 上一周")
        self.prev_week_btn.clicked.connect(self.prev_week)
        control_bar.addWidget(self.prev_week_btn)
        
        # 当前周次显示
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.update_week_label()
        control_bar.addWidget(self.week_label)
        
        self.next_week_btn = QPushButton("下一周 ▶")
        self.next_week_btn.clicked.connect(self.next_week)
        control_bar.addWidget(self.next_week_btn)
        
        # 周次快速选择
        control_bar.addWidget(QLabel("跳转到:"))
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, self.total_weeks)
        self.week_spinbox.setValue(self.current_week)
        self.week_spinbox.valueChanged.connect(self.change_week)
        control_bar.addWidget(self.week_spinbox)
        
        # 今天按钮
        current_week_btn = QPushButton("本周")
        current_week_btn.clicked.connect(self.go_to_current_week)
        control_bar.addWidget(current_week_btn)
        
        control_bar.addStretch()
        layout.addLayout(control_bar)
        
        # 课程表
        self.schedule_table = QTableWidget(13, 8)
        
        # 设置表头
        headers = ['时间段', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        # 设置时间段
        time_slots = [
            '第1节\n08:30-09:15', '第2节\n09:20-10:05', '第3节\n10:25-11:10',
            '第4节\n11:15-12:00', '第5节\n13:30-14:15', '第6节\n14:20-15:05',
            '第7节\n15:25-16:10', '第8节\n16:15-17:00', '第9节\n17:20-18:05',
            '第10节\n18:10-18:55', '第11节\n19:20-20:05', '第12节\n20:10-20:55',
            '第13节\n21:00-21:45'
        ]
        
        for i, time_slot in enumerate(time_slots):
            item = QTableWidgetItem(time_slot)
            item.setBackground(QColor(248, 249, 250))
            item.setFont(QFont("Arial", 8))
            self.schedule_table.setItem(i, 0, item)
        
        # 设置表格属性
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setFont(QFont("Arial", 9))
        # 设置不可编辑
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置行高和列宽
        for i in range(13):
            self.schedule_table.setRowHeight(i, 60)
        for i in range(8):
            if i == 0:
                self.schedule_table.setColumnWidth(i, 100)  # 时间段列较窄
            else:
                self.schedule_table.setColumnWidth(i, 150)  # 其他列较宽
        
        # 美化表格样式
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QTableWidget::item {
                border: 1px solid #f0f0f0;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.schedule_table)
        self.setLayout(layout)
    
    def update_week_label(self):
        """更新周次标签"""
        self.week_label.setText(f"第 {self.current_week} 周")
    
    def prev_week(self):
        """上一周"""
        if self.current_week > 1:
            self.current_week -= 1
            self.week_spinbox.setValue(self.current_week)
    
    def next_week(self):
        """下一周"""
        if self.current_week < self.total_weeks:
            self.current_week += 1
            self.week_spinbox.setValue(self.current_week)
    
    def change_week(self, week):
        """改变周次"""
        self.current_week = week
        self.update_week_label()
        self.update_schedule(self.selected_courses)
    
    def go_to_current_week(self):
        """回到本周"""
        self.current_week = 1
        self.week_spinbox.setValue(self.current_week)
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        
        # 清空表格内容(除了时间段列)
        for row in range(13):
            for col in range(1, 8):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # 填入选中的课程
        for course_id, course_name in selected_courses:
            schedules = self.db.get_course_schedules(course_id)
            
            for schedule in schedules:
                day_of_week, time_slots, location, weeks, semester = schedule
                
                # 检查当前周是否在课程周次范围内
                weeks_list = TimeConflictChecker.parse_weeks(weeks)
                if self.current_week not in weeks_list:
                    continue
                
                # 转换星期
                day_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7}
                col = day_map.get(str(day_of_week), 0)
                
                if col > 0:
                    # 解析时间段
                    slots = TimeConflictChecker.parse_time_slots(time_slots)
                    
                    for slot in slots:
                        if 1 <= slot <= 13:
                            row = slot - 1
                            current_item = self.schedule_table.item(row, col)
                            
                            if current_item and current_item.text():
                                # 如果已有课程，标记冲突
                                text = f"{current_item.text()}\n[冲突]\n{course_name[:8]}"
                                item = QTableWidgetItem(text)
                                item.setBackground(QColor(255, 235, 238))  # 更淡的红色
                                item.setForeground(QColor(198, 40, 40))
                                item.setFont(QFont("Arial", 8, QFont.Bold))
                            else:
                                text = f"{course_name[:12]}\n{location[:12] if location else ''}"
                                item = QTableWidgetItem(text)
                                item.setBackground(QColor(232, 245, 233))  # 更淡的绿色
                                item.setForeground(QColor(46, 125, 50))
                                item.setFont(QFont("Arial", 8, QFont.Bold))
                            
                            item.setTextAlignment(Qt.AlignCenter)
                            self.schedule_table.setItem(row, col, item)

class MultiWeekViewWidget(QWidget):
    """多周视图组件 - 类似苹果日历的周视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = CourseDatabase()
        self.current_week = 1
        self.total_weeks = 18
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_bar = QHBoxLayout()
        
        # 周次导航
        self.prev_week_btn = QPushButton("◀ 上一周")
        self.prev_week_btn.clicked.connect(self.prev_week)
        control_bar.addWidget(self.prev_week_btn)
        
        # 当前周次显示
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.update_week_label()
        control_bar.addWidget(self.week_label)
        
        self.next_week_btn = QPushButton("下一周 ▶")
        self.next_week_btn.clicked.connect(self.next_week)
        control_bar.addWidget(self.next_week_btn)
        
        # 周次快速选择
        control_bar.addWidget(QLabel("跳转到:"))
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, self.total_weeks)
        self.week_spinbox.setValue(self.current_week)
        self.week_spinbox.valueChanged.connect(self.change_week)
        control_bar.addWidget(self.week_spinbox)
        
        # 今天按钮
        current_week_btn = QPushButton("本周")
        current_week_btn.clicked.connect(self.go_to_current_week)
        control_bar.addWidget(current_week_btn)
        
        control_bar.addStretch()
        layout.addLayout(control_bar)
        
        # 课程表
        self.schedule_table = QTableWidget(13, 8)
        
        # 设置表头
        headers = ['时间段', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        # 设置时间段
        time_slots = [
            '第1节\n08:30-09:15', '第2节\n09:20-10:05', '第3节\n10:25-11:10',
            '第4节\n11:15-12:00', '第5节\n13:30-14:15', '第6节\n14:20-15:05',
            '第7节\n15:25-16:10', '第8节\n16:15-17:00', '第9节\n17:20-18:05',
            '第10节\n18:10-18:55', '第11节\n19:20-20:05', '第12节\n20:10-20:55',
            '第13节\n21:00-21:45'
        ]
        
        for i, time_slot in enumerate(time_slots):
            item = QTableWidgetItem(time_slot)
            item.setBackground(QColor(248, 249, 250))
            item.setFont(QFont("Arial", 8))
            self.schedule_table.setItem(i, 0, item)
        
        # 设置表格属性
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setFont(QFont("Arial", 9))
        # 设置不可编辑
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置行高和列宽
        for i in range(13):
            self.schedule_table.setRowHeight(i, 60)
        for i in range(8):
            self.schedule_table.setColumnWidth(i, 120)
        
        # 美化表格样式
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QTableWidget::item {
                border: 1px solid #f0f0f0;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.schedule_table)
        self.setLayout(layout)
    
    def update_week_label(self):
        """更新周次标签"""
        self.week_label.setText(f"第 {self.current_week} 周")
    
    def prev_week(self):
        """上一周"""
        if self.current_week > 1:
            self.current_week -= 1
            self.week_spinbox.setValue(self.current_week)
    
    def next_week(self):
        """下一周"""
        if self.current_week < self.total_weeks:
            self.current_week += 1
            self.week_spinbox.setValue(self.current_week)
    
    def change_week(self, week):
        """改变周次"""
        self.current_week = week
        self.update_week_label()
        self.update_schedule(self.selected_courses)
    
    def go_to_current_week(self):
        """回到本周"""
        self.current_week = 1
        self.week_spinbox.setValue(self.current_week)
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        
        # 清空表格内容(除了时间段列)
        for row in range(13):
            for col in range(1, 8):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # 填入选中的课程
        for course_id, course_name in selected_courses:
            schedules = self.db.get_course_schedules(course_id)
            
            for schedule in schedules:
                day_of_week, time_slots, location, weeks, semester = schedule
                
                # 检查当前周是否在课程周次范围内
                weeks_list = TimeConflictChecker.parse_weeks(weeks)
                if self.current_week not in weeks_list:
                    continue
                
                # 转换星期
                day_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7}
                col = day_map.get(str(day_of_week), 0)
                
                if col > 0:
                    # 解析时间段
                    slots = TimeConflictChecker.parse_time_slots(time_slots)
                    
                    for slot in slots:
                        if 1 <= slot <= 13:
                            row = slot - 1
                            current_item = self.schedule_table.item(row, col)
                            
                            if current_item and current_item.text():
                                # 如果已有课程，标记冲突
                                text = f"{current_item.text()}\n[冲突]\n{course_name[:8]}"
                                item = QTableWidgetItem(text)
                                item.setBackground(QColor(255, 235, 238))  # 更淡的红色
                                item.setForeground(QColor(198, 40, 40))
                                item.setFont(QFont("Arial", 8, QFont.Bold))
                            else:
                                text = f"{course_name[:12]}\n{location[:12] if location else ''}"
                                item = QTableWidgetItem(text)
                                item.setBackground(QColor(232, 245, 233))  # 更淡的绿色
                                item.setForeground(QColor(46, 125, 50))
                                item.setFont(QFont("Arial", 8, QFont.Bold))
                            
                            item.setTextAlignment(Qt.AlignCenter)
                            self.schedule_table.setItem(row, col, item)

class CalendarStyleScheduleWidget(QWidget):
    """苹果日历风格的课程表组件 - 更新为周视图和月视图"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.db = CourseDatabase()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部视图切换栏
        view_control = QHBoxLayout()
        view_control.setSpacing(0)
        
        # 视图切换按钮组
        self.view_group = QButtonGroup()
        
        self.week_view_btn = QPushButton("周")
        self.week_view_btn.setCheckable(True)
        self.week_view_btn.setChecked(True)
        self.week_view_btn.setMinimumWidth(60)
        
        self.month_view_btn = QPushButton("月")
        self.month_view_btn.setCheckable(True)
        self.month_view_btn.setMinimumWidth(60)
        
        self.view_group.addButton(self.week_view_btn, 0)
        self.view_group.addButton(self.month_view_btn, 1)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked:hover {
                background-color: #0056b3;
            }
        """
        
        self.week_view_btn.setStyleSheet(button_style)
        self.month_view_btn.setStyleSheet(button_style)
        
        view_control.addWidget(self.week_view_btn)
        view_control.addWidget(self.month_view_btn)
        view_control.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_schedule)
        view_control.addWidget(refresh_btn)
        
        layout.addLayout(view_control)
        
        # 创建堆叠窗口组件
        self.stacked_widget = QStackedWidget()
        
        # 周视图
        self.week_view = WeekViewWidget()
        self.stacked_widget.addWidget(self.week_view)
        
        # 月视图
        self.month_view = MonthViewWidget()
        self.stacked_widget.addWidget(self.month_view)
        
        layout.addWidget(self.stacked_widget)
        
        # 连接视图切换信号
        self.view_group.buttonClicked[int].connect(self.switch_view)
        
        self.setLayout(layout)
    
    def switch_view(self, view_id):
        """切换视图"""
        self.stacked_widget.setCurrentIndex(view_id)
        
        # 同步当前选中的课程
        if view_id == 0:  # 周视图
            self.week_view.update_schedule(self.selected_courses)
        else:  # 月视图
            self.month_view.update_schedule(self.selected_courses)
    
    def update_schedule(self, selected_courses):
        """更新课程表"""
        self.selected_courses = selected_courses
        
        # 更新当前显示的视图
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            self.week_view.update_schedule(selected_courses)
        else:
            self.month_view.update_schedule(selected_courses)
    
    def refresh_schedule(self):
        """刷新课程表"""
        self.update_schedule(self.selected_courses)


class StatisticsWidget(QWidget):
    """统计信息组件"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_courses = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 数据库统计
        db_stats_group = QGroupBox("📊 数据库统计")
        db_stats_layout = QGridLayout()
        
        stats = self.db.get_statistics()
        
        # 创建统计标签 - 移除teachers统计
        self.total_courses_label = QLabel(f"课程总数: {stats['total_courses']}")
        self.hours_label = QLabel(f"学时数量: {stats['hours']}")
        self.schedules_label = QLabel(f"时间安排: {stats['schedules']}")
        
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
    
    def update_selection_stats(self, selected_courses, conflicts_count=0):
        """更新选课统计"""
        self.selected_courses = selected_courses
        
        # 计算总学分
        total_credits = 0
        for course_id, _ in selected_courses:
            courses = self.db.get_all_courses()
            for course in courses:
                if course[0] == course_id:
                    credits_str = course[2] or "0"  # 修改索引：credits现在是第2列
                    try:
                        import re
                        credits_match = re.search(r'\d+', credits_str)
                        if credits_match:
                            total_credits += int(credits_match.group())
                    except:
                        pass
                    break
        
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

class AppleStyleCourseSelector(QMainWindow):
    """苹果日历风格的选课模拟器"""
    
    def __init__(self):
        super().__init__()
        self.db = CourseDatabase()
        self.selected_courses = []
        self.conflict_checker = TimeConflictChecker()
        
        self.init_ui()
        self.load_courses()
    
    def init_ui(self):
        self.setWindowTitle('🍎 UCAS选课模拟器 - 苹果日历风格')
        self.setGeometry(50, 50, 1800, 1000)
        
        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #fafbfc, stop:1 #f0f2f5);
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #24292e;
            }
            QTableWidget {
                gridline-color: #e1e4e8;
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                selection-background-color: #0366d6;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0366d6, stop:1 #0256c4);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0472e6, stop:1 #0366d6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0256c4, stop:1 #0245a8);
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #0366d6;
                box-shadow: 0 0 0 2px rgba(3, 102, 214, 0.3);
            }
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板：搜索和课程列表
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # 中央面板：苹果日历风格课程表
        center_widget = self.create_center_panel()
        splitter.addWidget(center_widget)
        
        # 右侧面板：统计和已选课程
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([450, 900, 450])
    
    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 搜索区域
        search_group = QGroupBox("🔍 课程搜索")
        search_layout = QVBoxLayout()
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程名称或代码...")
        self.search_input.textChanged.connect(self.search_courses)
        search_layout.addWidget(self.search_input)
        
        # 移除教师搜索，只保留院系搜索
        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("搜索学时数...")
        self.department_input.textChanged.connect(self.search_courses)
        search_layout.addWidget(self.department_input)
        
        # 搜索按钮
        search_btn = QPushButton("🔍 搜索课程")
        search_btn.clicked.connect(self.search_courses)
        search_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("🗑️ 清空搜索")
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 课程列表
        course_list_group = QGroupBox("📚 课程列表")
        course_list_layout = QVBoxLayout()
        
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(4)  # 减少列数：移除教师列
        self.course_table.setHorizontalHeaderLabels(['课程代码', '课程名称', '学分', '学时'])
        self.course_table.horizontalHeader().setStretchLastSection(True)
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.doubleClicked.connect(self.add_course)
        self.course_table.setAlternatingRowColors(True)
        # 设置不可编辑
        self.course_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        course_list_layout.addWidget(self.course_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加课程")
        add_btn.clicked.connect(self.add_course)
        button_layout.addWidget(add_btn)
        
        course_list_layout.addLayout(button_layout)
        course_list_group.setLayout(course_list_layout)
        layout.addWidget(course_list_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_center_panel(self):
        """创建中央面板 - 苹果日历风格课程表"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("📅 课程表")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #24292e; margin: 10px;")
        layout.addWidget(title_label)
        
        # 苹果日历风格的课程表组件
        self.schedule_widget = CalendarStyleScheduleWidget()
        layout.addWidget(self.schedule_widget)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 统计信息
        self.stats_widget = StatisticsWidget(self.db)
        layout.addWidget(self.stats_widget)
        
        # 已选课程
        selected_group = QGroupBox("📋 已选课程")
        selected_layout = QVBoxLayout()
        
        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(3)  # 减少列数：移除教师列
        self.selected_table.setHorizontalHeaderLabels(['课程名称', '学分', '操作'])
        self.selected_table.horizontalHeader().setStretchLastSection(True)
        self.selected_table.setAlternatingRowColors(True)
        # 设置不可编辑
        self.selected_table.setEditTriggers(QTableWidget.NoEditTriggers)
        selected_layout.addWidget(self.selected_table)
        
        # 批量操作
        batch_layout = QHBoxLayout()
        
        check_btn = QPushButton("🔍 检查冲突")
        check_btn.clicked.connect(self.check_conflicts)
        batch_layout.addWidget(check_btn)
        
        clear_btn = QPushButton("🗑️ 清空所有")
        clear_btn.clicked.connect(self.clear_all_courses)
        batch_layout.addWidget(clear_btn)
        
        selected_layout.addLayout(batch_layout)
        selected_group.setLayout(selected_layout)
        layout.addWidget(selected_group)
        
        # 冲突信息
        conflict_group = QGroupBox("⚠️ 冲突信息")
        conflict_layout = QVBoxLayout()
        
        self.conflict_info = QTextEdit()
        self.conflict_info.setMaximumHeight(150)
        self.conflict_info.setPlaceholderText("暂无冲突信息...")
        conflict_layout.addWidget(self.conflict_info)
        
        conflict_group.setLayout(conflict_layout)
        layout.addWidget(conflict_group)
        
        widget.setLayout(layout)
        return widget
    
    def load_courses(self):
        """加载所有课程"""
        try:
            courses = self.db.get_all_courses()
            self.populate_course_table(courses)
            self.stats_widget.update_selection_stats(self.selected_courses)
        except Exception as e:
            logger.error(f"加载课程失败: {e}")
            QMessageBox.critical(self, "错误", f"加载课程失败：{str(e)}")
    
    def add_course(self):
        """添加课程到已选列表"""
        current_row = self.course_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一门课程！")
            return
        
        # 获取课程ID
        course_code_item = self.course_table.item(current_row, 0)
        if not course_code_item:
            return
        
        course_id = course_code_item.data(Qt.UserRole)
        if course_id is None:
            return
        
        # 获取课程名称
        course_name_item = self.course_table.item(current_row, 1)
        if not course_name_item:
            return
        
        course_name = course_name_item.text()
        
        # 检查是否已经添加
        for selected_course_id, _ in self.selected_courses:
            if selected_course_id == course_id:
                QMessageBox.information(self, "提示", "该课程已经添加过了！")
                return
        
        # 检查时间冲突
        schedules = self.db.get_course_schedules(course_id)
        conflicts = []
        
        for selected_course_id, selected_course_name in self.selected_courses:
            selected_schedules = self.db.get_course_schedules(selected_course_id)
            for schedule1 in schedules:
                for schedule2 in selected_schedules:
                    if self.conflict_checker.check_conflict(schedule1, schedule2):
                        conflicts.append(selected_course_name)
                        break
        
        # 如果有冲突，询问用户是否仍要添加
        if conflicts:
            conflict_msg = f"与以下课程时间冲突：\n" + "\n".join(set(conflicts)) + "\n\n是否仍要添加？"
            reply = QMessageBox.question(self, "时间冲突", conflict_msg, 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        
        # 添加课程
        self.selected_courses.append((course_id, course_name))
        self.update_selected_table()
        self.schedule_widget.update_schedule(self.selected_courses)
        self.check_conflicts()
        
        QMessageBox.information(self, "成功", f"已添加课程：{course_name}")
    
    def remove_course(self, course_id):
        """移除课程"""
        # 找到要移除的课程
        for i, (selected_id, course_name) in enumerate(self.selected_courses):
            if selected_id == course_id:
                reply = QMessageBox.question(self, "确认", f"确定要移除课程：{course_name}？")
                if reply == QMessageBox.Yes:
                    del self.selected_courses[i]
                    self.update_selected_table()
                    self.schedule_widget.update_schedule(self.selected_courses)
                    self.check_conflicts()
                break
    
    def update_selected_table(self):
        """更新已选课程表格 - 适配新的数据结构"""
        self.selected_table.setRowCount(len(self.selected_courses))
        
        for row, (course_id, course_name) in enumerate(self.selected_courses):
            courses = self.db.get_all_courses()
            course_info = None
            for course in courses:
                if course[0] == course_id:
                    course_info = course
                    break
            
            if course_info:
                _, name, credits, hours, course_code = course_info  # 修改解包：移除teacher
                
                self.selected_table.setItem(row, 0, QTableWidgetItem(name or ""))
                self.selected_table.setItem(row, 1, QTableWidgetItem(credits or ""))
                
                # 删除按钮
                remove_btn = QPushButton("🗑️")
                remove_btn.setMaximumWidth(40)
                remove_btn.setStyleSheet("background-color: #dc3545; color: white; font-size: 12px; border: none; border-radius: 3px;")
                remove_btn.clicked.connect(lambda checked, cid=course_id: self.remove_course(cid))
                self.selected_table.setCellWidget(row, 2, remove_btn)
    
    def check_conflicts(self):
        """检查课程冲突"""
        conflicts = []
        
        for i, (course_id1, course_name1) in enumerate(self.selected_courses):
            schedules1 = self.db.get_course_schedules(course_id1)
            
            for j, (course_id2, course_name2) in enumerate(self.selected_courses[i+1:], i+1):
                schedules2 = self.db.get_course_schedules(course_id2)
                
                for schedule1 in schedules1:
                    for schedule2 in schedules2:
                        if self.conflict_checker.check_conflict(schedule1, schedule2):
                            conflicts.append({
                                'course1': course_name1,
                                'course2': course_name2,
                                'schedule1': schedule1,
                                'schedule2': schedule2
                            })
        
        self.display_conflicts(conflicts)
        self.stats_widget.update_selection_stats(self.selected_courses, len(conflicts))
    
    def display_conflicts(self, conflicts):
        """显示冲突信息"""
        if not conflicts:
            self.conflict_info.setText("🟢 太好了！没有发现时间冲突。")
            self.conflict_info.setStyleSheet("background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius: 6px; padding: 10px;")
        else:
            conflict_text = f"🔴 发现 {len(conflicts)} 个时间冲突：\n\n"
            
            day_map = {'1': '周一', '2': '周二', '3': '周三', '4': '周四', 
                      '5': '周五', '6': '周六', '7': '周日'}
            
            for i, conflict in enumerate(conflicts, 1):
                schedule1 = conflict['schedule1']
                
                day1 = day_map.get(str(schedule1[0]), f"星期{schedule1[0]}")
                
                conflict_text += f"冲突 {i}: {conflict['course1']} ⚔️ {conflict['course2']}\n"
                conflict_text += f"时间: {day1} 第{schedule1[1]}节\n\n"
            
            self.conflict_info.setText(conflict_text)
            self.conflict_info.setStyleSheet("background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 6px; padding: 10px;")
    
    def clear_all_courses(self):
        """清空所有课程"""
        if not self.selected_courses:
            QMessageBox.information(self, "提示", "当前没有已选课程")
            return
            
        reply = QMessageBox.question(self, "确认", "确定要清空所有已选课程吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.selected_courses.clear()
            self.update_selected_table()
            self.schedule_widget.update_schedule(self.selected_courses)
            self.check_conflicts()
            QMessageBox.information(self, "成功", "已清空所有课程")
    
    def populate_course_table(self, courses):
        """填充课程表格 - 适配新的数据结构"""
        self.course_table.setRowCount(len(courses))
        
        for row, course in enumerate(courses):
            course_id, name, credits, department, course_code = course  # 修改解包：移除teacher
            
            self.course_table.setItem(row, 0, QTableWidgetItem(course_code or ""))
            self.course_table.setItem(row, 1, QTableWidgetItem(name or ""))
            self.course_table.setItem(row, 2, QTableWidgetItem(credits or ""))
            self.course_table.setItem(row, 3, QTableWidgetItem(department or ""))
            
            # 存储课程ID在第一列的UserRole中
            if self.course_table.item(row, 0):
                self.course_table.item(row, 0).setData(Qt.UserRole, course_id)
    
    def search_courses(self):
        """搜索课程 - 移除teacher参数"""
        keyword = self.search_input.text()
        department = self.department_input.text()
        
        try:
            courses = self.db.search_courses(keyword, department)
            self.populate_course_table(courses)
        except Exception as e:
            logger.error(f"搜索课程失败: {e}")
            QMessageBox.warning(self, "错误", f"搜索失败：{str(e)}")
    
    def clear_search(self):
        """清空搜索"""
        self.search_input.clear()
        self.department_input.clear()
        self.load_courses()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UCAS选课模拟器")
    app.setApplicationVersion("3.0 Apple Style")
    
    window = AppleStyleCourseSelector()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()