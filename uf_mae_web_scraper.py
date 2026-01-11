"""
UF MAE Website Real-time Scraper
实时搜索 UF MAE 网站获取最新信息（特别是课程信息）
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, quote


class UFMAEWebScraper:
    """实时搜索 UF MAE 网站的工具类"""
    
    BASE_URL = "https://mae.ufl.edu"
    COURSE_SCHEDULE_URLS = {
        "spring": "https://mae.ufl.edu/undergraduate/course-schedules/spring-2025/",
        "summer": "https://mae.ufl.edu/undergraduate/course-schedules/summer-2025/",
        "fall": "https://mae.ufl.edu/undergraduate/course-schedules/fall-2025/"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_course_schedule(self, semester: str = "spring", course_code: Optional[str] = None) -> List[Dict]:
        """
        搜索课程表信息
        
        Args:
            semester: 学期 (spring, summer, fall)
            course_code: 课程代码 (如 "EML2023", "EML3100")，可选
        
        Returns:
            课程信息列表
        """
        try:
            url = self.COURSE_SCHEDULE_URLS.get(semester.lower(), self.COURSE_SCHEDULE_URLS["spring"])
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            courses = []
            
            # 尝试不同的表格结构
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                headers = []
                
                # 获取表头
                if rows:
                    header_row = rows[0]
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # 解析数据行
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    course_data = {}
                    for i, cell in enumerate(cells):
                        header = headers[i] if i < len(headers) else f"col_{i}"
                        course_data[header] = cell.get_text(strip=True)
                    
                    # 如果指定了课程代码，进行过滤
                    if course_code:
                        course_text = ' '.join(course_data.values()).upper()
                        if course_code.upper() not in course_text:
                            continue
                    
                    if course_data:
                        courses.append(course_data)
            
            # 如果没有找到表格，尝试搜索文本内容
            if not courses:
                page_text = soup.get_text()
                if course_code:
                    # 搜索包含课程代码的段落
                    pattern = rf'\b{re.escape(course_code.upper())}\b[^\n]*'
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    for match in matches[:5]:  # 最多返回5个匹配
                        courses.append({"course_info": match.strip()})
            
            return courses[:10]  # 最多返回10个结果
            
        except Exception as e:
            print(f"⚠️ Error searching course schedule: {e}")
            return []
    
    def search_website(self, query: str, max_results: int = 5) -> List[str]:
        """
        在 UF MAE 网站上搜索相关信息
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
        
        Returns:
            相关文本片段列表
        """
        results = []
        
        try:
            # 搜索课程表页面
            if any(keyword in query.lower() for keyword in ['course', 'class', 'schedule', 'semester', 'spring', 'summer', 'fall']):
                semester = "spring"  # 默认春季学期
                if "summer" in query.lower():
                    semester = "summer"
                elif "fall" in query.lower():
                    semester = "fall"
                
                # 提取可能的课程代码
                course_code = None
                course_pattern = r'\b([A-Z]{3}\d{4})\b'
                matches = re.findall(course_pattern, query.upper())
                if matches:
                    course_code = matches[0]
                
                courses = self.search_course_schedule(semester, course_code)
                for course in courses[:max_results]:
                    course_text = " | ".join([f"{k}: {v}" for k, v in course.items() if v])
                    if course_text:
                        results.append(f"Course Schedule: {course_text}")
            
            # 搜索主页面
            try:
                response = self.session.get(self.BASE_URL, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 搜索包含关键词的文本
                page_text = soup.get_text()
                query_words = query.lower().split()
                
                # 查找包含关键词的段落
                paragraphs = page_text.split('\n')
                for para in paragraphs:
                    para_lower = para.lower()
                    if any(word in para_lower for word in query_words if len(word) > 2):
                        if len(para.strip()) > 20 and len(para.strip()) < 500:
                            results.append(para.strip())
                            if len(results) >= max_results:
                                break
            except Exception as e:
                print(f"⚠️ Error searching main page: {e}")
            
            return results[:max_results]
            
        except Exception as e:
            print(f"⚠️ Error in website search: {e}")
            return []
    
    def get_course_info(self, course_code: str, semester: str = "spring") -> Optional[Dict]:
        """
        获取特定课程的详细信息
        
        Args:
            course_code: 课程代码 (如 "EML2023")
            semester: 学期
        
        Returns:
            课程信息字典
        """
        courses = self.search_course_schedule(semester, course_code)
        if courses:
            return courses[0]
        return None


# 测试代码
if __name__ == "__main__":
    scraper = UFMAEWebScraper()
    
    print("🔍 测试 UF MAE 网站实时搜索:")
    print("=" * 60)
    
    # 测试1: 搜索课程
    print("\n1. 搜索课程信息:")
    results = scraper.search_website("EML2023 spring course", max_results=3)
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result[:100]}...")
    
    # 测试2: 搜索课程表
    print("\n2. 搜索课程表:")
    courses = scraper.search_course_schedule("spring", "EML")
    print(f"   找到 {len(courses)} 门课程")
    for i, course in enumerate(courses[:3], 1):
        print(f"   {i}. {course}")
    
    # 测试3: 搜索一般信息
    print("\n3. 搜索研究领域:")
    results = scraper.search_website("robotics research", max_results=3)
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result[:100]}...")
