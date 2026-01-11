# 🔍 实时网站搜索功能说明

## ✅ 功能概述

系统现在支持**实时搜索 UF MAE 网站**，特别是当涉及课程相关问题时，可以自动获取最新的课程信息。

## 🎯 使用场景

### 场景 1: 老师问学生选了什么课
```
Advisor: "What courses are you taking this semester?"
→ 系统自动搜索 UF MAE 网站获取最新课程表
→ 学生回复时可以使用真实的课程信息
```

### 场景 2: 询问课程安排
```
Advisor: "What's the schedule for EML2023?"
→ 系统自动搜索课程表页面
→ 返回具体的课程时间、地点等信息
```

### 场景 3: 询问学期信息
```
Advisor: "What courses are available in spring?"
→ 系统自动搜索春季学期课程表
→ 返回可用的课程列表
```

## 🔧 技术实现

### 1. 网页爬虫模块
- **文件**: `uf_mae_web_scraper.py`
- **功能**: 实时搜索 UF MAE 网站
- **支持**: 课程表搜索、一般信息搜索

### 2. 自动触发机制
系统会在以下情况自动搜索网站：
- 检测到课程相关关键词：`course`, `class`, `schedule`, `semester`, `spring`, `summer`, `fall`, `EML`
- 检测到询问类问题：`what classes`, `what courses`, `taking`, `enrolled`

### 3. 集成到回复生成流程
```
用户问题
  ↓
检测课程相关关键词
  ↓
实时搜索 UF MAE 网站
  ↓
将搜索结果添加到知识上下文
  ↓
生成学生回复（包含真实课程信息）
```

## 📋 支持的搜索类型

### 1. 课程表搜索
- **学期**: Spring 2025, Summer 2025, Fall 2025
- **课程代码**: 如 EML2023, EML3100
- **返回**: 课程时间、地点、教师等信息

### 2. 一般信息搜索
- **研究领域**: Robotics, Space Research 等
- **部门信息**: 联系方式、资源等
- **返回**: 相关文本片段

## ⚙️ 配置

### 依赖安装
```bash
pip install beautifulsoup4 lxml
```

### 课程表 URL
系统会自动访问以下 URL：
- Spring: `https://mae.ufl.edu/undergraduate/course-schedules/spring-2025/`
- Summer: `https://mae.ufl.edu/undergraduate/course-schedules/summer-2025/`
- Fall: `https://mae.ufl.edu/undergraduate/course-schedules/fall-2025/`

## 🎯 使用示例

### 示例 1: 搜索特定课程
```python
from uf_mae_web_scraper import UFMAEWebScraper

scraper = UFMAEWebScraper()
courses = scraper.search_course_schedule("spring", "EML2023")
# 返回: 包含 EML2023 课程信息的列表
```

### 示例 2: 搜索课程相关问题
```python
results = scraper.search_website("EML2023 spring course", max_results=3)
# 返回: 相关的课程信息文本片段
```

## ⚠️ 注意事项

1. **网络连接**: 需要稳定的网络连接才能访问网站
2. **网站结构变化**: 如果 UF MAE 网站结构改变，可能需要更新爬虫代码
3. **性能**: 实时搜索会增加响应时间，系统会优雅降级（如果搜索失败，使用静态知识库）
4. **错误处理**: 如果网站搜索失败，系统会自动回退到静态知识库

## 🔄 工作流程

```
1. 用户输入问题
   ↓
2. 检测是否涉及课程
   ↓
3. 如果是 → 实时搜索网站
   ↓
4. 将搜索结果添加到知识上下文
   ↓
5. 生成回复（包含最新信息）
```

## 📊 优势

✅ **实时性**: 获取最新的课程信息
✅ **准确性**: 直接从官方网站获取信息
✅ **自动化**: 无需手动更新知识库
✅ **智能**: 只在需要时搜索，不影响性能

## 🚀 未来改进

- [ ] 缓存搜索结果（减少重复请求）
- [ ] 支持更多页面类型（研究领域、教师信息等）
- [ ] 添加搜索结果的置信度评分
- [ ] 支持多学期课程对比
