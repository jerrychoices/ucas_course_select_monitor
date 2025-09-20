"""
周视图组件
显示传统的7天×11节课的周课程表
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QPushButton, QSpinBox,
                           QHeaderView, QAbstractItemView, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class WeekViewWidget(QWidget):
    """周视图组件 - 传统课程表格式"""
    
    def __init__(self):
        super().__init__()
        self.selected_courses = []
        self.custom_courses = []  # 存储自定义课程数据
        self.db = None
        self.current_week = 1  # 当前显示的周次
        
        # 时间节次映射
        self.time_slots = {
            1: "08:00-08:50", 2: "09:00-09:50", 3: "10:10-11:00", 4: "11:10-12:00",
            5: "14:00-14:50", 6: "15:00-15:50", 7: "16:10-17:00", 8: "17:10-18:00",
            9: "19:00-19:50", 10: "20:00-20:50", 11: "21:00-21:50"
        }
        
        # 星期映射
        self.weekdays = {
            1: "周一", 2: "周二", 3: "周三", 4: "周四",
            5: "周五", 6: "周六", 7: "周日"
        }
        
        self.init_ui()
    
    def get_custom_course_by_id(self, course_id):
        """根据ID获取自定义课程"""
        if course_id >= 0:
            return None
        
        index = -(course_id + 1)
        if 0 <= index < len(self.custom_courses):
            return self.custom_courses[index]
        return None
    
    def get_custom_course_schedules(self, course_id):
        """获取自定义课程的时间安排"""
        custom_course = self.get_custom_course_by_id(course_id)
        if not custom_course:
            return []
        
        schedules = []
        for schedule in custom_course.get('schedules', []):
            # 转换为数据库格式的时间安排
            # (weekday, time_slots, location, weeks, semester)
            schedule_data = (
                schedule.get('weekday'),
                f"{schedule.get('start_time')}-{schedule.get('end_time')}",
                schedule.get('location', ''),
                schedule.get('weeks', '1-16'),
                '1'  # 默认学期
            )
            schedules.append(schedule_data)
        
        return schedules
    
    def set_database(self, db):
        """设置数据库连接"""
        self.db = db
    
    def set_custom_courses(self, custom_courses):
        """设置自定义课程数据"""
        self.custom_courses = custom_courses
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)
        
        # 课程表
        self.schedule_table = self.create_schedule_table()
        layout.addWidget(self.schedule_table)
        
        # 底部统计信息
        stats_bar = self.create_stats_bar()
        layout.addWidget(stats_bar)
        
        self.setLayout(layout)
        
        # 初始化课程表
        self.update_schedule_display()
    
    def create_control_bar(self):
        """创建顶部控制栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # 周次选择
        week_label = QLabel("学期周次:")
        week_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(week_label)
        
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, 20)  # 假设学期有20周
        self.week_spinbox.setValue(self.current_week)
        self.week_spinbox.valueChanged.connect(self.on_week_changed)
        self.week_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.week_spinbox)
        
        layout.addWidget(QLabel("周"))
        
        # 导航按钮
        prev_btn = QPushButton("← 上一周")
        prev_btn.clicked.connect(self.prev_week)
        prev_btn.setMaximumWidth(100)
        layout.addWidget(prev_btn)
        
        next_btn = QPushButton("下一周 →")
        next_btn.clicked.connect(self.next_week)
        next_btn.setMaximumWidth(100)
        layout.addWidget(next_btn)
        
        layout.addStretch()
        
        # 当前周显示
        self.current_week_label = QLabel(f"第 {self.current_week} 周")
        self.current_week_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.current_week_label.setStyleSheet("color: #0366d6;")
        layout.addWidget(self.current_week_label)
        
        frame.setLayout(layout)
        return frame
    
    def create_schedule_table(self):
        """创建课程表格"""
        table = QTableWidget(11, 8)  # 11节课 × 8列（时间+7天）
        
        # 设置表头
        headers = ['时间'] + [self.weekdays[i] for i in range(1, 8)]
        table.setHorizontalHeaderLabels(headers)
        
        # 设置第一列（时间列）
        for i in range(11):
            time_slot = i + 1
            time_text = f"第{time_slot}节\n{self.time_slots.get(time_slot, '')}"
            item = QTableWidgetItem(time_text)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont("Arial", 9))
            item.setBackground(QColor("#f8f9fa"))
            table.setItem(i, 0, item)
        
        # 设置表格属性
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 设置列宽
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 100)  # 时间列稍窄
        for i in range(1, 8):
            header.resizeSection(i, 150)  # 星期列
        
        # 设置行高
        for i in range(11):
            table.setRowHeight(i, 60)
        
        # 美化样式
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                font-size: 11px;
            }
            QTableWidget::item {
                border: 1px solid #e9ecef;
                padding: 4px;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #6c757d;
                color: white;
                padding: 8px;
                border: 1px solid #495057;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        return table
    
    def create_stats_bar(self):
        """创建底部统计栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        
        layout = QHBoxLayout()
        
        self.stats_label = QLabel("当前周次课程统计: 0门课程")
        self.stats_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        # 图例
        legend_layout = QHBoxLayout()
        
        # 普通课程图例
        normal_legend = QLabel("■ 普通课程")
        normal_legend.setStyleSheet("color: #28a745; font-weight: bold;")
        legend_layout.addWidget(normal_legend)
        
        # 冲突课程图例
        conflict_legend = QLabel("■ 时间冲突")
        conflict_legend.setStyleSheet("color: #dc3545; font-weight: bold;")
        legend_layout.addWidget(conflict_legend)
        
        layout.addLayout(legend_layout)
        
        frame.setLayout(layout)
        return frame
    
    def on_week_changed(self, week):
        """周次改变回调"""
        self.current_week = week
        self.current_week_label.setText(f"第 {self.current_week} 周")
        self.update_schedule_display()
    
    def prev_week(self):
        """上一周"""
        if self.current_week > 1:
            self.week_spinbox.setValue(self.current_week - 1)
    
    def next_week(self):
        """下一周"""
        if self.current_week < 20:
            self.week_spinbox.setValue(self.current_week + 1)
    
    def update_schedule(self, selected_courses):
        """更新课程表显示"""
        self.selected_courses = selected_courses
        self.update_schedule_display()
    
    def update_schedule_display(self):
        """更新课程表格显示"""
        if not self.db:
            return
        
        # 清空课程表格（保留时间列）
        for row in range(11):
            for col in range(1, 8):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # 统计变量
        total_courses_this_week = 0
        conflict_count = 0
        
        # 创建课程网格用于冲突检测
        course_grid = {}
        
        try:
            # 填充课程信息
            for course_id, course_name in self.selected_courses:
                # 获取课程时间安排
                if course_id < 0:
                    # 自定义课程
                    schedules = self.get_custom_course_schedules(course_id)
                else:
                    # 数据库课程
                    schedules = self.db.get_course_schedules(course_id)
                
                for schedule in schedules:
                    day_of_week, time_slots_str, location, weeks, semester = schedule
                    
                    # 检查是否在当前周次
                    if not self.is_course_in_week(weeks, self.current_week):
                        continue
                    
                    # 解析时间段
                    time_slots = self.parse_time_slots(time_slots_str)
                    
                    if not time_slots or not (1 <= int(day_of_week) <= 7):
                        continue
                    
                    total_courses_this_week += 1
                    
                    # 检查冲突
                    is_conflict = False
                    day_of_week = int(day_of_week)  # 确保是整数
                    for time_slot in time_slots:
                        if 1 <= time_slot <= 11:
                            grid_key = (day_of_week, time_slot)
                            if grid_key in course_grid:
                                is_conflict = True
                                conflict_count += 1
                            course_grid[grid_key] = course_name
                    
                    # 创建课程显示内容
                    course_text = f"{course_name}\n"
                    if location:
                        course_text += f"@{location}"
                    
                    # 显示课程（跨时间段）
                    start_slot = min(time_slots)
                    end_slot = max(time_slots)
                    
                    if start_slot == end_slot:
                        # 单节课
                        self.set_course_cell(start_slot - 1, day_of_week, 
                                           course_text, is_conflict)
                    else:
                        # 多节连续课程
                        for slot in range(start_slot, end_slot + 1):
                            if slot == start_slot:
                                # 第一节显示完整信息
                                self.set_course_cell(slot - 1, day_of_week, 
                                                   course_text, is_conflict)
                            else:
                                # 后续节次显示连接符
                                self.set_course_cell(slot - 1, day_of_week, 
                                                   "↑", is_conflict)
            
            # 更新统计信息
            stats_text = f"第{self.current_week}周课程统计: {total_courses_this_week}门课程"
            if conflict_count > 0:
                stats_text += f", {conflict_count}处时间冲突"
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            logger.error(f"Error updating schedule display: {e}")
            self.stats_label.setText("显示课程表时出错")
    
    def set_course_cell(self, row, day_col, text, is_conflict=False):
        """设置课程单元格"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("Arial", 9, QFont.Bold))
        
        # 设置颜色
        if is_conflict:
            item.setBackground(QColor("#f8d7da"))  # 浅红色背景
            item.setForeground(QColor("#721c24"))  # 深红色文字
        else:
            item.setBackground(QColor("#d4edda"))  # 浅绿色背景
            item.setForeground(QColor("#155724"))  # 深绿色文字
        
        self.schedule_table.setItem(row, day_col, item)
    
    def parse_time_slots(self, time_slots_str):
        """解析时间段字符串"""
        if not time_slots_str:
            return []
        
        try:
            import re
            numbers = re.findall(r'\d+', str(time_slots_str))
            if len(numbers) >= 2:
                start = int(numbers[0])
                end = int(numbers[-1])
                return list(range(start, end + 1))
            elif len(numbers) == 1:
                return [int(numbers[0])]
        except:
            pass
        
        return []
    
    def is_course_in_week(self, weeks_str, target_week):
        """检查课程是否在指定周次"""
        if not weeks_str:
            return True  # 如果没有周次信息，默认显示
        
        try:
            # 简化的周次检查，实际项目中可能需要更复杂的解析
            weeks_str = str(weeks_str)
            if str(target_week) in weeks_str:
                return True
            
            # 尝试解析范围，如"1-16周"
            import re
            range_match = re.search(r'(\d+)-(\d+)', weeks_str)
            if range_match:
                start_week = int(range_match.group(1))
                end_week = int(range_match.group(2))
                return start_week <= target_week <= end_week
            
        except:
            pass
        
        return False
