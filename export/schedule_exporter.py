"""
课程表导出功能
支持导出为CSV、Excel、PDF等格式
"""

import csv
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available, Excel export will be disabled")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not available, PDF export will be disabled")


class ScheduleExporter:
    """课程表导出器"""
    
    def __init__(self):
        self.time_slots = {
            1: "08:00-08:50", 2: "09:00-09:50", 3: "10:10-11:00", 4: "11:10-12:00",
            5: "14:00-14:50", 6: "15:00-15:50", 7: "16:10-17:00", 8: "17:10-18:00",
            9: "19:00-19:50", 10: "20:00-20:50", 11: "21:00-21:50"
        }
        
        self.weekdays = {
            1: "周一", 2: "周二", 3: "周三", 4: "周四",
            5: "周五", 6: "周六", 7: "周日"
        }
    
    def export_to_csv(self, courses_data, file_path):
        """导出为CSV格式"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入标题
                writer.writerow(['课程代码', '课程名称', '学分', '学时', '星期', '时间', '地点', '周次', '学期'])
                
                # 写入数据
                for course in courses_data:
                    if course['schedules']:
                        for schedule in course['schedules']:
                            writer.writerow([
                                course['code'],
                                course['name'],
                                course['credits'],
                                course['hours'],
                                self.weekdays.get(schedule['day_of_week'], f"第{schedule['day_of_week']}天"),
                                schedule['time_slots'],
                                schedule['location'] or '',
                                schedule['weeks'] or '',
                                schedule['semester'] or ''
                            ])
                    else:
                        # 没有时间安排的课程
                        writer.writerow([
                            course['code'],
                            course['name'],
                            course['credits'],
                            course['hours'],
                            '', '', '', '', ''
                        ])
            
            logger.info(f"Successfully exported to CSV: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def export_to_excel(self, courses_data, file_path):
        """导出为Excel格式"""
        if not PANDAS_AVAILABLE:
            logger.error("pandas is required for Excel export")
            return False
        
        try:
            # 准备数据
            rows = []
            for course in courses_data:
                if course['schedules']:
                    for schedule in course['schedules']:
                        rows.append({
                            '课程代码': course['code'],
                            '课程名称': course['name'],
                            '学分': course['credits'],
                            '学时': course['hours'],
                            '星期': self.weekdays.get(schedule['day_of_week'], f"第{schedule['day_of_week']}天"),
                            '时间': schedule['time_slots'],
                            '地点': schedule['location'] or '',
                            '周次': schedule['weeks'] or '',
                            '学期': schedule['semester'] or ''
                        })
                else:
                    rows.append({
                        '课程代码': course['code'],
                        '课程名称': course['name'],
                        '学分': course['credits'],
                        '学时': course['hours'],
                        '星期': '',
                        '时间': '',
                        '地点': '',
                        '周次': '',
                        '学期': ''
                    })
            
            # 创建DataFrame并导出
            df = pd.DataFrame(rows)
            df.to_excel(file_path, index=False, sheet_name='课程表')
            
            logger.info(f"Successfully exported to Excel: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
            return False
    
    def export_to_pdf(self, courses_data, file_path):
        """导出为PDF格式"""
        if not REPORTLAB_AVAILABLE:
            logger.error("reportlab is required for PDF export")
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # 样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 居中
            )
            
            # 标题
            title = Paragraph("课程表", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # 准备表格数据
            table_data = [['课程代码', '课程名称', '学分', '学时', '星期', '时间', '地点', '周次']]
            
            for course in courses_data:
                if course['schedules']:
                    for schedule in course['schedules']:
                        table_data.append([
                            course['code'] or '',
                            course['name'],
                            str(course['credits']) if course['credits'] else '',
                            course['hours'] or '',
                            self.weekdays.get(schedule['day_of_week'], f"第{schedule['day_of_week']}天"),
                            schedule['time_slots'] or '',
                            schedule['location'] or '',
                            schedule['weeks'] or ''
                        ])
                else:
                    table_data.append([
                        course['code'] or '',
                        course['name'],
                        str(course['credits']) if course['credits'] else '',
                        course['hours'] or '',
                        '', '', '', ''
                    ])
            
            # 创建表格
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            logger.info(f"Successfully exported to PDF: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to PDF: {e}")
            return False
    
    def export_weekly_schedule(self, courses_data, file_path, format='csv'):
        """导出周课程表格式"""
        try:
            # 创建7x11的课程表格式（周一到周日，1-11节课）
            schedule_grid = {}
            for day in range(1, 8):
                schedule_grid[day] = {}
                for time_slot in range(1, 12):
                    schedule_grid[day][time_slot] = []
            
            # 填充课程数据
            for course in courses_data:
                for schedule in course['schedules']:
                    day = schedule['day_of_week']
                    time_slots_str = schedule['time_slots']
                    
                    # 解析时间段
                    if time_slots_str:
                        import re
                        numbers = re.findall(r'\d+', time_slots_str)
                        if len(numbers) >= 2:
                            start = int(numbers[0])
                            end = int(numbers[-1])
                            for slot in range(start, end + 1):
                                if 1 <= slot <= 11:
                                    schedule_grid[day][slot].append({
                                        'name': course['name'],
                                        'location': schedule['location'] or '',
                                        'weeks': schedule['weeks'] or ''
                                    })
                        elif len(numbers) == 1:
                            slot = int(numbers[0])
                            if 1 <= slot <= 11:
                                schedule_grid[day][slot].append({
                                    'name': course['name'],
                                    'location': schedule['location'] or '',
                                    'weeks': schedule['weeks'] or ''
                                })
            
            if format.lower() == 'csv':
                return self._export_weekly_csv(schedule_grid, file_path)
            elif format.lower() == 'excel' and PANDAS_AVAILABLE:
                return self._export_weekly_excel(schedule_grid, file_path)
            else:
                logger.error(f"Unsupported format or missing dependencies: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export weekly schedule: {e}")
            return False
    
    def _export_weekly_csv(self, schedule_grid, file_path):
        """导出周课程表为CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入标题行
            header = ['时间'] + [self.weekdays[day] for day in range(1, 8)]
            writer.writerow(header)
            
            # 写入每个时间段
            for time_slot in range(1, 12):
                row = [self.time_slots.get(time_slot, f"第{time_slot}节")]
                
                for day in range(1, 8):
                    courses = schedule_grid[day][time_slot]
                    if courses:
                        course_info = []
                        for course in courses:
                            info = course['name']
                            if course['location']:
                                info += f"@{course['location']}"
                            course_info.append(info)
                        row.append(' | '.join(course_info))
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        return True
    
    def _export_weekly_excel(self, schedule_grid, file_path):
        """导出周课程表为Excel"""
        # 准备数据
        data = []
        for time_slot in range(1, 12):
            row = {'时间': self.time_slots.get(time_slot, f"第{time_slot}节")}
            
            for day in range(1, 8):
                courses = schedule_grid[day][time_slot]
                if courses:
                    course_info = []
                    for course in courses:
                        info = course['name']
                        if course['location']:
                            info += f"@{course['location']}"
                        course_info.append(info)
                    row[self.weekdays[day]] = ' | '.join(course_info)
                else:
                    row[self.weekdays[day]] = ''
            
            data.append(row)
        
        # 创建DataFrame并导出
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, sheet_name='周课程表')
        
        return True
    
    def export_to_json(self, courses_data, file_path):
        """导出为JSON格式"""
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'courses': courses_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Successfully exported to JSON: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            return False
