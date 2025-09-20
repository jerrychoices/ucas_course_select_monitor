"""
主窗口模块
重构后的苹果日历风格课程选择器主窗口
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTableWidget, QTableWidgetItem, QPushButton,
                           QLineEdit, QLabel, QTextEdit, QSplitter,
                           QHeaderView, QMessageBox, QTabWidget, QGroupBox,
                           QListWidget, QListWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import logging

# 导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import CourseDatabase
from utils import TimeConflictChecker
from widgets import MonthViewWidget, WeekViewWidget, DayViewWidget, StatisticsWidget, CustomCourseDialog
from export import ScheduleExporter

logger = logging.getLogger(__name__)


class CourseSelectionMainWindow(QMainWindow):
    """课程选择主窗口"""
    
    def __init__(self):
        super().__init__()
        self.db = CourseDatabase()
        self.selected_courses = []
        self.custom_courses = []  # 存储自定义课程
        self.conflict_checker = TimeConflictChecker()
        self.schedule_exporter = ScheduleExporter()
        
        self.init_ui()
        self.load_courses()
    
    def init_ui(self):
        """初始化UI"""
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
        
        # 中央面板：课程表视图
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
        
        # 学时搜索
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
        
        # 添加自定义课程按钮
        custom_course_btn = QPushButton("➕ 添加自定义课程")
        custom_course_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #34ce57, stop:1 #28a745);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e7e34, stop:1 #155724);
            }
        """)
        custom_course_btn.clicked.connect(self.show_custom_course_dialog)
        search_layout.addWidget(custom_course_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 课程列表
        course_list_group = QGroupBox("📚 课程列表")
        course_list_layout = QVBoxLayout()
        
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(4)
        self.course_table.setHorizontalHeaderLabels(['课程代码', '课程名称', '学分', '学时'])
        
        # 设置表格属性
        header = self.course_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 100)
        header.resizeSection(1, 200)
        header.resizeSection(2, 60)
        
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.setAlternatingRowColors(True)
        self.course_table.itemDoubleClicked.connect(self.add_course)
        
        course_list_layout.addWidget(self.course_table)
        
        # 添加课程按钮
        add_course_btn = QPushButton("➕ 添加选中课程")
        add_course_btn.clicked.connect(self.add_course)
        course_list_layout.addWidget(add_course_btn)
        
        course_list_group.setLayout(course_list_layout)
        layout.addWidget(course_list_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_center_panel(self):
        """创建中央面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        export_btn = QPushButton("📤 导出课程表")
        export_btn.clicked.connect(self.export_schedule)
        toolbar.addWidget(export_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 课程表视图选项卡
        self.schedule_tabs = QTabWidget()
        
        # 月视图
        self.month_view = MonthViewWidget()
        self.month_view.set_database(self.db)
        self.schedule_tabs.addTab(self.month_view, "📅 月视图")
        
        # 周视图
        self.week_view = WeekViewWidget()
        self.week_view.set_database(self.db)
        self.schedule_tabs.addTab(self.week_view, "📊 周视图")
        
        # 日视图
        self.day_view = DayViewWidget()
        self.day_view.set_database(self.db)
        self.schedule_tabs.addTab(self.day_view, "📋 日视图")
        
        layout.addWidget(self.schedule_tabs)
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 统计信息
        self.statistics_widget = StatisticsWidget(self.db)
        layout.addWidget(self.statistics_widget)
        
        # 已选课程列表
        selected_group = QGroupBox("✅ 已选课程")
        selected_layout = QVBoxLayout()
        
        self.selected_list = QListWidget()
        self.selected_list.itemDoubleClicked.connect(self.remove_course)
        selected_layout.addWidget(self.selected_list)
        
        # 移除课程按钮
        remove_btn = QPushButton("➖ 移除选中课程")
        remove_btn.clicked.connect(self.remove_course)
        selected_layout.addWidget(remove_btn)
        
        clear_all_btn = QPushButton("🗑️ 清空所有选课")
        clear_all_btn.clicked.connect(self.clear_all_courses)
        selected_layout.addWidget(clear_all_btn)
        
        selected_group.setLayout(selected_layout)
        layout.addWidget(selected_group)
        
        widget.setLayout(layout)
        return widget
    
    def load_courses(self):
        """加载课程数据"""
        try:
            courses = self.db.get_all_courses()
            self.display_courses(courses)
        except Exception as e:
            logger.error(f"Failed to load courses: {e}")
            QMessageBox.critical(self, "错误", f"加载课程数据失败: {e}")
    
    def display_courses(self, courses):
        """显示课程列表（包括数据库课程和自定义课程）"""
        # 合并数据库课程和自定义课程
        all_courses = list(courses)
        
        # 添加自定义课程到列表
        for custom_course in self.custom_courses:
            # 自定义课程格式：(course_id, course_name, credits, hours, course_code)
            # course_id 使用负数来区分自定义课程
            custom_id = -(len(self.custom_courses) - self.custom_courses.index(custom_course))
            course_data = (
                custom_id,
                custom_course.get('name', ''),
                custom_course.get('credits', ''),
                custom_course.get('hours', ''),
                custom_course.get('code', '')
            )
            all_courses.append(course_data)
        
        self.course_table.setRowCount(len(all_courses))
        
        for row, course in enumerate(all_courses):
            course_id, course_name, credits, hours, course_code = course
            
            # 填充表格
            code_item = QTableWidgetItem(str(course_code or ''))
            name_item = QTableWidgetItem(str(course_name or ''))
            credits_item = QTableWidgetItem(str(credits or ''))
            hours_item = QTableWidgetItem(str(hours or ''))
            
            # 如果是自定义课程，用不同颜色标识
            if course_id < 0:
                for item in [code_item, name_item, credits_item, hours_item]:
                    item.setBackground(QColor(240, 248, 255))  # 淡蓝色背景
                    item.setToolTip("自定义课程")
            
            self.course_table.setItem(row, 0, code_item)
            self.course_table.setItem(row, 1, name_item)
            self.course_table.setItem(row, 2, credits_item)
            self.course_table.setItem(row, 3, hours_item)
            
            # 存储课程ID
            self.course_table.item(row, 0).setData(Qt.UserRole, course_id)
    
    def search_courses(self):
        """搜索课程（包括自定义课程）"""
        keyword = self.search_input.text().strip().lower()
        department = self.department_input.text().strip()
        
        try:
            # 搜索数据库课程
            courses = self.db.search_courses(self.search_input.text().strip(), department)
            
            # 如果有关键词搜索，还要搜索自定义课程
            if keyword:
                filtered_courses = []
                # 过滤数据库课程
                for course in courses:
                    course_id, course_name, credits, hours, course_code = course
                    if (keyword in str(course_name).lower() or 
                        keyword in str(course_code).lower()):
                        filtered_courses.append(course)
                
                # 搜索自定义课程
                custom_filtered = []
                for custom_course in self.custom_courses:
                    name = str(custom_course.get('name', '')).lower()
                    code = str(custom_course.get('code', '')).lower()
                    if keyword in name or keyword in code:
                        custom_filtered.append(custom_course)
                
                # 临时替换自定义课程列表用于显示
                original_custom = self.custom_courses[:]
                self.custom_courses = custom_filtered
                self.display_courses(filtered_courses)
                self.custom_courses = original_custom
            else:
                self.display_courses(courses)
                
        except Exception as e:
            logger.error(f"Failed to search courses: {e}")
            QMessageBox.warning(self, "警告", f"搜索失败: {e}")
    
    def clear_search(self):
        """清空搜索"""
        self.search_input.clear()
        self.department_input.clear()
        self.load_courses()
    
    def add_course(self):
        """添加课程到选课列表"""
        current_row = self.course_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选择一门课程")
            return
        
        # 获取课程信息
        course_id_item = self.course_table.item(current_row, 0)
        course_name_item = self.course_table.item(current_row, 1)
        
        if not course_id_item or not course_name_item:
            return
        
        course_id = course_id_item.data(Qt.UserRole)
        course_name = course_name_item.text()
        
        # 检查是否已选择
        for selected_id, _ in self.selected_courses:
            if selected_id == course_id:
                QMessageBox.information(self, "提示", "该课程已在选课列表中")
                return
        
        # 检查时间冲突
        conflicts = self.check_time_conflicts(course_id)
        if conflicts:
            conflict_msg = "检测到时间冲突：\n" + "\n".join(conflicts)
            reply = QMessageBox.question(self, "时间冲突", 
                                       f"{conflict_msg}\n\n是否仍要添加该课程？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # 添加到选课列表
        self.selected_courses.append((course_id, course_name))
        self.update_selected_list()
        self.update_all_views()
        
        QMessageBox.information(self, "成功", f"已添加课程: {course_name}")
    
    def remove_course(self):
        """从选课列表中移除课程"""
        current_item = self.selected_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择要移除的课程")
            return
        
        # 获取课程ID
        course_id = current_item.data(Qt.UserRole)
        
        # 从列表中移除
        self.selected_courses = [(cid, cname) for cid, cname in self.selected_courses if cid != course_id]
        
        self.update_selected_list()
        self.update_all_views()
        
        QMessageBox.information(self, "成功", "课程已移除")
    
    def clear_all_courses(self):
        """清空所有选课"""
        reply = QMessageBox.question(self, "确认", "确定要清空所有选课吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.selected_courses.clear()
            self.update_selected_list()
            self.update_all_views()
    
    def update_selected_list(self):
        """更新已选课程列表"""
        self.selected_list.clear()
        
        for course_id, course_name in self.selected_courses:
            item = QListWidgetItem(course_name)
            item.setData(Qt.UserRole, course_id)
            self.selected_list.addItem(item)
    
    def update_all_views(self):
        """更新所有视图"""
        # 传递自定义课程数据给视图组件
        self.month_view.set_custom_courses(self.custom_courses)
        self.week_view.set_custom_courses(self.custom_courses)
        self.day_view.set_custom_courses(self.custom_courses)
        
        # 更新课程表视图
        self.month_view.update_schedule(self.selected_courses)
        self.week_view.update_schedule(self.selected_courses)
        self.day_view.update_schedule(self.selected_courses)
        
        # 更新统计信息
        conflicts_count = len(self.get_all_conflicts())
        self.statistics_widget.update_selection_stats(self.selected_courses, conflicts_count)
    
    def check_time_conflicts(self, new_course_id):
        """检查时间冲突"""
        conflicts = []
        
        # 获取新课程的时间安排
        if new_course_id < 0:
            # 自定义课程
            new_schedules = self.get_custom_course_schedules(new_course_id)
        else:
            # 数据库课程
            new_schedules = self.db.get_course_schedules(new_course_id)
        
        # 获取已选课程的时间安排
        for course_id, course_name in self.selected_courses:
            if course_id < 0:
                # 自定义课程
                existing_schedules = self.get_custom_course_schedules(course_id)
            else:
                # 数据库课程
                existing_schedules = self.db.get_course_schedules(course_id)
            
            for new_schedule in new_schedules:
                for existing_schedule in existing_schedules:
                    if self.conflict_checker.check_conflict(new_schedule, existing_schedule):
                        conflicts.append(f"与 {course_name} 的时间冲突")
        
        return conflicts
    
    def get_all_conflicts(self):
        """获取所有时间冲突"""
        conflicts = []
        
        for i, (course_id1, course_name1) in enumerate(self.selected_courses):
            if course_id1 < 0:
                schedules1 = self.get_custom_course_schedules(course_id1)
            else:
                schedules1 = self.db.get_course_schedules(course_id1)
            
            for j, (course_id2, course_name2) in enumerate(self.selected_courses[i+1:], i+1):
                if course_id2 < 0:
                    schedules2 = self.get_custom_course_schedules(course_id2)
                else:
                    schedules2 = self.db.get_course_schedules(course_id2)
                
                for schedule1 in schedules1:
                    for schedule2 in schedules2:
                        if self.conflict_checker.check_conflict(schedule1, schedule2):
                            conflicts.append((course_name1, course_name2))
        
        return conflicts
    
    def export_schedule(self):
        """导出课程表"""
        if not self.selected_courses:
            QMessageBox.information(self, "提示", "请先选择课程")
            return
        
        # 文件对话框
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "导出课程表",
            f"我的课程表_{self.get_current_timestamp()}.csv",
            "CSV文件 (*.csv);;Excel文件 (*.xlsx);;PDF文件 (*.pdf);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 获取课程数据
            course_ids = [course_id for course_id, _ in self.selected_courses]
            courses_data = self.db.get_selected_courses_with_schedules(course_ids)
            
            # 根据文件类型导出
            success = False
            if file_path.endswith('.csv'):
                success = self.schedule_exporter.export_to_csv(courses_data, file_path)
            elif file_path.endswith('.xlsx'):
                success = self.schedule_exporter.export_to_excel(courses_data, file_path)
            elif file_path.endswith('.pdf'):
                success = self.schedule_exporter.export_to_pdf(courses_data, file_path)
            elif file_path.endswith('.json'):
                success = self.schedule_exporter.export_to_json(courses_data, file_path)
            else:
                # 默认导出为CSV
                success = self.schedule_exporter.export_to_csv(courses_data, file_path)
            
            if success:
                QMessageBox.information(self, "成功", f"课程表已导出到: {file_path}")
            else:
                QMessageBox.warning(self, "失败", "导出失败，请检查文件格式和权限")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def show_custom_course_dialog(self):
        """显示自定义课程对话框"""
        dialog = CustomCourseDialog(self)
        
        if dialog.exec_() == CustomCourseDialog.Accepted:
            course_data = dialog.get_course_data()
            
            # 检查课程代码是否重复
            if self.is_course_code_duplicate(course_data.get('code', '')):
                QMessageBox.warning(self, "警告", "课程代码已存在，请使用不同的代码")
                return
            
            # 添加到自定义课程列表
            self.custom_courses.append(course_data)
            
            # 刷新课程列表显示
            self.refresh_course_display()
            
            QMessageBox.information(self, "成功", f"已添加自定义课程: {course_data.get('name', '')}")
    
    def is_course_code_duplicate(self, code):
        """检查课程代码是否重复"""
        if not code:
            return False
        
        # 检查数据库中的课程
        try:
            courses = self.db.get_all_courses()
            for course in courses:
                if course[4] == code:  # course_code
                    return True
        except:
            pass
        
        # 检查自定义课程
        for custom_course in self.custom_courses:
            if custom_course.get('code', '') == code:
                return True
        
        return False
    
    def refresh_course_display(self):
        """刷新课程显示"""
        # 如果当前有搜索条件，重新执行搜索
        if self.search_input.text().strip() or self.department_input.text().strip():
            self.search_courses()
        else:
            self.load_courses()
    
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
            schedule_data = {
                'weekday': schedule.get('weekday'),
                'start_time': schedule.get('start_time'),
                'end_time': schedule.get('end_time'),
                'location': schedule.get('location', ''),
                'weeks': schedule.get('weeks', '1-16')
            }
            schedules.append(schedule_data)
        
        return schedules
