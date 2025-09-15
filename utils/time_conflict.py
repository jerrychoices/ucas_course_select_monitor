"""
时间冲突检查工具
用于检查课程时间安排是否存在冲突
"""

import re
import logging

logger = logging.getLogger(__name__)


class TimeConflictChecker:
    """时间冲突检查器"""
    
    @staticmethod
    def parse_time_slots(time_slots_str):
        """解析时间段字符串，返回时间段列表"""
        if not time_slots_str:
            return []
        
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
    
    @staticmethod
    def get_conflicts_for_course(new_course_schedules, existing_schedules):
        """
        检查新课程与已有课程的冲突
        
        Args:
            new_course_schedules: 新课程的时间安排列表
            existing_schedules: 已有课程的时间安排列表
            
        Returns:
            list: 冲突的时间安排列表
        """
        conflicts = []
        
        for new_schedule in new_course_schedules:
            for existing_schedule in existing_schedules:
                if TimeConflictChecker.check_conflict(new_schedule, existing_schedule):
                    conflicts.append((new_schedule, existing_schedule))
        
        return conflicts
    
    @staticmethod
    def format_time_slot(time_slot):
        """格式化时间段显示"""
        time_map = {
            1: "08:00-08:50", 2: "09:00-09:50", 3: "10:10-11:00", 4: "11:10-12:00",
            5: "14:00-14:50", 6: "15:00-15:50", 7: "16:10-17:00", 8: "17:10-18:00",
            9: "19:00-19:50", 10: "20:00-20:50", 11: "21:00-21:50"
        }
        return time_map.get(time_slot, f"第{time_slot}节")
    
    @staticmethod
    def format_day_of_week(day):
        """格式化星期显示"""
        day_map = {
            1: "周一", 2: "周二", 3: "周三", 4: "周四", 
            5: "周五", 6: "周六", 7: "周日"
        }
        return day_map.get(day, f"第{day}天")
