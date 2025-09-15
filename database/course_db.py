"""
课程数据库操作类
处理与课程数据相关的所有数据库操作
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


class CourseDatabase:
    """课程数据库操作类"""
    
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
    
    def get_selected_courses_with_schedules(self, selected_course_ids):
        """获取已选课程及其时间安排，用于导出功能"""
        if not selected_course_ids:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询语句
        placeholders = ','.join(['?' for _ in selected_course_ids])
        query = f'''
            SELECT c.id, c.course_name, c.credits, c.hours, c.course_code,
                   cs.day_of_week, cs.time_slots, cs.location, cs.weeks, cs.semester
            FROM courses c
            LEFT JOIN course_schedules cs ON c.id = cs.course_id
            WHERE c.id IN ({placeholders})
            ORDER BY c.course_name, cs.day_of_week, cs.time_slots
        '''
        
        cursor.execute(query, selected_course_ids)
        results = cursor.fetchall()
        conn.close()
        
        # 组织数据结构
        courses_data = {}
        for row in results:
            course_id, course_name, credits, hours, course_code, day_of_week, time_slots, location, weeks, semester = row
            
            if course_id not in courses_data:
                courses_data[course_id] = {
                    'id': course_id,
                    'name': course_name,
                    'credits': credits,
                    'hours': hours,
                    'code': course_code,
                    'schedules': []
                }
            
            if day_of_week is not None:  # 有时间安排
                courses_data[course_id]['schedules'].append({
                    'day_of_week': day_of_week,
                    'time_slots': time_slots,
                    'location': location,
                    'weeks': weeks,
                    'semester': semester
                })
        
        return list(courses_data.values())
