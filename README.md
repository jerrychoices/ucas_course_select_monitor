# 🍎 UCAS课程选择模拟器

中国科学院大学选课模拟器，支持课程搜索、时间冲突检查和课程表导出功能。

## ✨ 功能特性

- 🔍 **智能课程搜索**: 支持按课程名称、代码、学时等条件搜索
- 📅 **多视图课程表**: 提供月视图、周视图、日视图等多种显示方式
  - **月视图**: 苹果日历风格，显示整月课程安排
  - **周视图**: 传统7×11课程表格式，支持周次导航和冲突检测
  - **日视图**: 单日详细课程安排（开发中）
- ⚠️ **时间冲突检查**: 自动检测课程时间冲突并提醒用户
- 📊 **统计分析**: 显示已选学分、课程数量等统计信息
- 📤 **多格式导出**: 支持导出为CSV、Excel、PDF、JSON格式
- 🎨 **优雅界面**: 采用苹果日历风格的现代化界面设计

## 🏗️ 项目结构

```
ucas_course_select_monitor/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明文档
├── ucas_courses_new.db    # 课程数据库
├── database/              # 数据库模块
│   ├── __init__.py
│   └── course_db.py       # 课程数据库操作类
├── ui/                    # 用户界面模块
│   ├── __init__.py
│   └── main_window.py     # 主窗口类
├── widgets/               # UI组件模块
│   ├── __init__.py
│   ├── month_view.py      # 月视图组件
│   ├── week_view.py       # 周视图组件  
│   ├── day_view.py        # 日视图组件
│   └── statistics_view.py # 统计信息组件
├── utils/                 # 工具类模块
│   ├── __init__.py
│   └── time_conflict.py   # 时间冲突检查工具
└── export/                # 导出功能模块
    ├── __init__.py
    └── schedule_exporter.py # 课程表导出器
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- PyQt5 5.15.0+

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/ucas_course_select_monitor.git
cd ucas_course_select_monitor

# 安装依赖
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

## 📋 使用说明

### 基本操作

1. **搜索课程**: 在左侧搜索栏输入关键词查找课程
2. **添加课程**: 双击课程列表中的课程或点击"添加选中课程"按钮
3. **查看课程表**: 在中央面板切换不同视图查看课程安排
   - **月视图**: 查看整月的课程分布
   - **周视图**: 查看传统课程表格式，支持周次切换
   - **日视图**: 查看单日详细安排
4. **移除课程**: 在右侧已选课程列表中双击课程或点击"移除选中课程"按钮
5. **导出课程表**: 点击"导出课程表"按钮，选择导出格式和位置

### 周视图功能

周视图提供传统的7天×11节课课程表格式：

- **周次导航**: 使用周次选择器查看不同周的课程安排
- **时间冲突检测**: 自动检测并高亮显示时间冲突
- **课程信息**: 显示课程名称和上课地点
- **连续课程**: 多节连续课程用箭头连接
- **颜色编码**: 
  - 🟢 正常课程：绿色背景
  - 🔴 时间冲突：红色背景

### 导出功能

支持以下导出格式：

- **CSV格式**: 逗号分隔值文件，可用Excel打开
- **Excel格式**: 标准Excel文件（需安装pandas）
- **PDF格式**: PDF文档（需安装reportlab）
- **JSON格式**: JSON数据文件

#### 导出内容包括：

- 课程基本信息（代码、名称、学分、学时）
- 详细时间安排（星期、时间段、地点、周次）
- 周课程表格式（可选）

### 时间冲突检查

系统会自动检查课程时间冲突：

- 添加课程时自动检测冲突
- 在统计面板显示冲突数量
- 支持强制添加冲突课程（会有警告提示）

## 🔧 开发说明

### 模块说明

#### database 模块
- `CourseDatabase`: 处理所有数据库操作
- 支持课程搜索、时间安排查询等功能

#### ui 模块  
- `CourseSelectionMainWindow`: 主窗口类
- 集成所有UI组件和业务逻辑

#### widgets 模块
- `MonthViewWidget`: 月视图组件（苹果日历风格）
- `WeekViewWidget`: 周视图组件
- `DayViewWidget`: 日视图组件
- `StatisticsWidget`: 统计信息组件

#### utils 模块
- `TimeConflictChecker`: 时间冲突检查工具
- 支持时间段解析和冲突检测

#### export 模块
- `ScheduleExporter`: 课程表导出器
- 支持多种格式导出

### 扩展开发

1. **添加新的视图组件**: 在`widgets`模块中创建新组件
2. **扩展导出格式**: 在`export`模块中添加新的导出方法
3. **增强数据库功能**: 在`database`模块中添加新的查询方法

## 📦 依赖包说明

### 必需依赖

- **PyQt5**: GUI框架，提供所有界面组件
- **sqlite3**: Python内置，用于数据库操作

### 可选依赖

- **pandas**: 用于Excel格式导出
- **reportlab**: 用于PDF格式导出

### 安装可选依赖

```bash
# 安装Excel导出支持
pip install pandas openpyxl

# 安装PDF导出支持  
pip install reportlab
```

## 🛠️ 故障排除

### 常见问题

1. **导入错误**: 确保所有依赖包已正确安装
   ```bash
   pip install -r requirements.txt
   ```

2. **数据库文件不存在**: 确保`ucas_courses_new.db`文件在项目根目录

3. **导出功能不可用**: 
   - Excel导出需要pandas: `pip install pandas`
   - PDF导出需要reportlab: `pip install reportlab`

4. **界面显示异常**: 检查PyQt5版本是否为5.15.0+

### 日志调试

程序运行时会在控制台输出日志信息，可以根据错误信息进行调试。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 其他
本项目由claude sonnet4全程开发，感谢AI，三小时就能完成该项目。如有什么bug，请优先自己使用AI或自审查代码解决，如提交issue不一定能及时更新。

⭐ 如果这个项目对你有帮助，请给它一个star！
