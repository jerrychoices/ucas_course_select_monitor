"""
自定义课程添加对话框
允许用户手动添加数据库中不存在的课程
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLineEdit, QTextEdit, QSpinBox, QComboBox, 
                           QPushButton, QLabel, QDialogButtonBox, QGroupBox,
                           QCheckBox, QTimeEdit, QMessageBox, QScrollArea,
                           QWidget, QGridLayout)
from PyQt5.QtCore import Qt, QTime, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)


class CustomCourseDialog(QDialog):
    """自定义课程添加对话框"""
    
    # 定义信号，用于传递新添加的课程信息
    course_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.course_data = {}
        self.schedule_widgets = []  # 存储时间安排控件
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("🆕 添加自定义课程")
        self.setModal(True)
        self.resize(600, 700)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #495057;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox, QTimeEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
            QComboBox:focus, QTimeEdit:focus {
                border-color: #0366d6;
                background-color: #f8f9ff;
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
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0472e6, stop:1 #0366d6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0256c4, stop:1 #0245a8);
            }
            QPushButton#deleteButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #dc3545, stop:1 #c82333);
            }
            QPushButton#deleteButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e4606d, stop:1 #dc3545);
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建滚动内容
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # 基本信息组
        basic_group = self.create_basic_info_group()
        scroll_layout.addWidget(basic_group)
        
        # 时间安排组
        schedule_group = self.create_schedule_group()
        scroll_layout.addWidget(schedule_group)
        
        # 其他信息组
        other_group = self.create_other_info_group()
        scroll_layout.addWidget(other_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # 按钮组
        button_layout = self.create_button_group()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 添加第一个时间安排
        self.add_schedule_slot()
    
    def create_basic_info_group(self):
        """创建基本信息组"""
        group = QGroupBox("📝 基本信息")
        layout = QFormLayout()
        
        # 课程名称（必填）
        self.course_name_edit = QLineEdit()
        self.course_name_edit.setPlaceholderText("请输入课程名称（必填）")
        layout.addRow("课程名称 *:", self.course_name_edit)
        
        # 课程代码
        self.course_code_edit = QLineEdit()
        self.course_code_edit.setPlaceholderText("如：CS101")
        layout.addRow("课程代码:", self.course_code_edit)
        
        # 学分
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(0, 10)
        self.credits_spin.setValue(2)
        self.credits_spin.setSuffix(" 学分")
        layout.addRow("学分:", self.credits_spin)
        
        # 学时
        self.hours_edit = QLineEdit()
        self.hours_edit.setPlaceholderText("如：32学时")
        layout.addRow("学时:", self.hours_edit)
        
        # 课程类型
        self.course_type_combo = QComboBox()
        self.course_type_combo.addItems([
            "必修课", "选修课", "专业课", "公共课", 
            "实验课", "实习课", "毕业设计", "其他"
        ])
        layout.addRow("课程类型:", self.course_type_combo)
        
        # 授课教师
        self.teacher_edit = QLineEdit()
        self.teacher_edit.setPlaceholderText("教师姓名")
        layout.addRow("授课教师:", self.teacher_edit)
        
        group.setLayout(layout)
        return group
    
    def create_schedule_group(self):
        """创建时间安排组"""
        self.schedule_group = QGroupBox("⏰ 时间安排")
        self.schedule_layout = QVBoxLayout()
        
        # 添加说明
        info_label = QLabel("💡 提示：可以添加多个时间安排（如理论课+实验课）")
        info_label.setStyleSheet("color: #6c757d; font-style: italic; margin: 8px;")
        self.schedule_layout.addWidget(info_label)
        
        # 时间安排容器
        self.schedule_container = QVBoxLayout()
        self.schedule_layout.addLayout(self.schedule_container)
        
        # 添加时间安排按钮
        add_schedule_btn = QPushButton("➕ 添加时间安排")
        add_schedule_btn.clicked.connect(self.add_schedule_slot)
        self.schedule_layout.addWidget(add_schedule_btn)
        
        self.schedule_group.setLayout(self.schedule_layout)
        return self.schedule_group
    
    def create_other_info_group(self):
        """创建其他信息组"""
        group = QGroupBox("📋 其他信息")
        layout = QFormLayout()
        
        # 课程描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("课程简介、教学目标等...")
        self.description_edit.setMaximumHeight(100)
        layout.addRow("课程描述:", self.description_edit)
        
        # 先修课程
        self.prerequisite_edit = QLineEdit()
        self.prerequisite_edit.setPlaceholderText("如：高等数学、线性代数")
        layout.addRow("先修课程:", self.prerequisite_edit)
        
        # 考核方式
        self.assessment_combo = QComboBox()
        self.assessment_combo.addItems([
            "考试", "考查", "考试+平时", "论文", "实践", "其他"
        ])
        layout.addRow("考核方式:", self.assessment_combo)
        
        # 开课学期
        self.semester_combo = QComboBox()
        self.semester_combo.addItems([
            "春季学期", "秋季学期", "夏季学期", "全年"
        ])
        layout.addRow("开课学期:", self.semester_combo)
        
        # 是否推荐
        self.recommended_check = QCheckBox("推荐选修")
        layout.addRow("", self.recommended_check)
        
        group.setLayout(layout)
        return group
    
    def add_schedule_slot(self):
        """添加一个时间安排槽"""
        # 创建时间安排框架
        schedule_frame = QGroupBox(f"时间安排 {len(self.schedule_widgets) + 1}")
        schedule_frame.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QGridLayout()
        
        # 星期选择
        weekday_combo = QComboBox()
        weekday_combo.addItems([
            "周一", "周二", "周三", "周四", "周五", "周六", "周日"
        ])
        layout.addWidget(QLabel("星期:"), 0, 0)
        layout.addWidget(weekday_combo, 0, 1)
        
        # 开始时间
        start_time = QTimeEdit()
        start_time.setTime(QTime(8, 0))
        start_time.setDisplayFormat("HH:mm")
        layout.addWidget(QLabel("开始时间:"), 0, 2)
        layout.addWidget(start_time, 0, 3)
        
        # 结束时间
        end_time = QTimeEdit()
        end_time.setTime(QTime(9, 50))
        end_time.setDisplayFormat("HH:mm")
        layout.addWidget(QLabel("结束时间:"), 0, 4)
        layout.addWidget(end_time, 0, 5)
        
        # 上课地点
        location_edit = QLineEdit()
        location_edit.setPlaceholderText("如：教一楼101")
        layout.addWidget(QLabel("上课地点:"), 1, 0)
        layout.addWidget(location_edit, 1, 1, 1, 3)
        
        # 上课周次
        weeks_edit = QLineEdit()
        weeks_edit.setPlaceholderText("如：1-16周 或 1,3,5,7周")
        layout.addWidget(QLabel("上课周次:"), 1, 4)
        layout.addWidget(weeks_edit, 1, 5)
        
        # 删除按钮
        if len(self.schedule_widgets) > 0:  # 第一个不能删除
            delete_btn = QPushButton("🗑️ 删除")
            delete_btn.setObjectName("deleteButton")
            delete_btn.clicked.connect(lambda: self.remove_schedule_slot(schedule_frame))
            layout.addWidget(delete_btn, 2, 5)
        
        schedule_frame.setLayout(layout)
        
        # 保存控件引用
        schedule_data = {
            'frame': schedule_frame,
            'weekday': weekday_combo,
            'start_time': start_time,
            'end_time': end_time,
            'location': location_edit,
            'weeks': weeks_edit
        }
        self.schedule_widgets.append(schedule_data)
        
        # 添加到布局
        self.schedule_container.addWidget(schedule_frame)
    
    def remove_schedule_slot(self, frame):
        """移除时间安排槽"""
        # 找到对应的控件数据
        for i, schedule_data in enumerate(self.schedule_widgets):
            if schedule_data['frame'] == frame:
                # 从布局中移除
                self.schedule_container.removeWidget(frame)
                frame.deleteLater()
                # 从列表中移除
                self.schedule_widgets.pop(i)
                break
        
        # 更新编号
        for i, schedule_data in enumerate(self.schedule_widgets):
            schedule_data['frame'].setTitle(f"时间安排 {i + 1}")
    
    def create_button_group(self):
        """创建按钮组"""
        layout = QHBoxLayout()
        
        # 预览按钮
        preview_btn = QPushButton("👁️ 预览")
        preview_btn.clicked.connect(self.preview_course)
        layout.addWidget(preview_btn)
        
        layout.addStretch()
        
        # 标准对话框按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.button(QDialogButtonBox.Ok).setText("✅ 添加课程")
        button_box.button(QDialogButtonBox.Cancel).setText("❌ 取消")
        
        button_box.accepted.connect(self.accept_course)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        return layout
    
    def preview_course(self):
        """预览课程信息"""
        course_data = self.collect_course_data()
        if not course_data:
            return
        
        # 创建预览文本
        preview_text = f"""
📚 课程名称: {course_data['name']}
🏷️ 课程代码: {course_data.get('code', '无')}
📊 学分: {course_data.get('credits', 0)} 学分
⏱️ 学时: {course_data.get('hours', '无')}
👨‍🏫 授课教师: {course_data.get('teacher', '无')}
📂 课程类型: {course_data.get('type', '无')}

⏰ 时间安排:
"""
        
        for i, schedule in enumerate(course_data.get('schedules', []), 1):
            preview_text += f"""
  {i}. {schedule['weekday']} {schedule['start_time']}-{schedule['end_time']}
     📍 地点: {schedule.get('location', '待定')}
     📅 周次: {schedule.get('weeks', '全学期')}
"""
        
        if course_data.get('description'):
            preview_text += f"\n📝 课程描述:\n{course_data['description']}"
        
        # 显示预览对话框
        QMessageBox.information(self, "课程预览", preview_text)
    
    def collect_course_data(self):
        """收集表单数据"""
        # 验证必填字段
        if not self.course_name_edit.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入课程名称！")
            self.course_name_edit.setFocus()
            return None
        
        # 验证时间安排
        if not self.schedule_widgets:
            QMessageBox.warning(self, "输入错误", "请至少添加一个时间安排！")
            return None
        
        # 收集基本信息
        course_data = {
            'name': self.course_name_edit.text().strip(),
            'code': self.course_code_edit.text().strip(),
            'credits': self.credits_spin.value(),
            'hours': self.hours_edit.text().strip(),
            'type': self.course_type_combo.currentText(),
            'teacher': self.teacher_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'prerequisite': self.prerequisite_edit.text().strip(),
            'assessment': self.assessment_combo.currentText(),
            'semester': self.semester_combo.currentText(),
            'recommended': self.recommended_check.isChecked(),
            'schedules': []
        }
        
        # 收集时间安排
        for schedule_data in self.schedule_widgets:
            schedule = {
                'weekday': schedule_data['weekday'].currentText(),
                'weekday_num': schedule_data['weekday'].currentIndex() + 1,
                'start_time': schedule_data['start_time'].time().toString("HH:mm"),
                'end_time': schedule_data['end_time'].time().toString("HH:mm"),
                'location': schedule_data['location'].text().strip(),
                'weeks': schedule_data['weeks'].text().strip()
            }
            
            # 验证时间逻辑
            if schedule_data['start_time'].time() >= schedule_data['end_time'].time():
                QMessageBox.warning(self, "时间错误", 
                                  f"时间安排{len(course_data['schedules']) + 1}: 开始时间必须早于结束时间！")
                return None
            
            course_data['schedules'].append(schedule)
        
        return course_data
    
    def accept_course(self):
        """确认添加课程"""
        course_data = self.collect_course_data()
        if course_data:
            # 发送信号
            self.course_added.emit(course_data)
            self.accept()
    
    def reset_form(self):
        """重置表单"""
        # 清空基本信息
        self.course_name_edit.clear()
        self.course_code_edit.clear()
        self.credits_spin.setValue(2)
        self.hours_edit.clear()
        self.course_type_combo.setCurrentIndex(0)
        self.teacher_edit.clear()
        self.description_edit.clear()
        self.prerequisite_edit.clear()
        self.assessment_combo.setCurrentIndex(0)
        self.semester_combo.setCurrentIndex(0)
        self.recommended_check.setChecked(False)
        
        # 清空时间安排
        for schedule_data in self.schedule_widgets[:]:
            self.remove_schedule_slot(schedule_data['frame'])
        
        # 添加一个默认时间安排
        self.add_schedule_slot()
