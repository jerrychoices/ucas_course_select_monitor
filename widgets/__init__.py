"""
UI组件模块
包含各种课程表视图组件
"""

from .month_view import MonthViewWidget
from .week_view import WeekViewWidget
from .day_view import DayViewWidget
from .statistics_view import StatisticsWidget

__all__ = [
    'MonthViewWidget', 
    'WeekViewWidget', 
    'DayViewWidget', 
    'StatisticsWidget'
]
