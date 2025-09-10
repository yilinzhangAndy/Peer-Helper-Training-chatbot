import json
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any

class SimpleKnowledgeBase:
    def __init__(self):
        # 初始化嵌入模型
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 初始化知识库数据
        self.knowledge_data = [
            # 课程信息
            {
                "text": "MAE program requires 30 credit hours including core courses in engineering fundamentals, mathematics, and specialized electives.",
                "type": "academic_requirements",
                "category": "curriculum"
            },
            {
                "text": "Core courses include Engineering Mathematics, Engineering Design, and Engineering Ethics. Students must maintain a 3.0 GPA.",
                "type": "academic_requirements", 
                "category": "curriculum"
            },
            {
                "text": "Students can choose from specializations in Aerospace, Automotive, Manufacturing, Robotics, and Materials Science.",
                "type": "specialization_info",
                "category": "curriculum"
            },
            
            # 职业发展
            {
                "text": "MAE graduates can pursue careers in aerospace, automotive, manufacturing, robotics, and research. Internships are highly recommended.",
                "type": "career_guidance",
                "category": "professional_development"
            },
            {
                "text": "Research opportunities are available with faculty in areas like fluid dynamics, materials science, and control systems.",
                "type": "research_opportunities",
                "category": "academic_advancement"
            },
            {
                "text": "Industry partnerships provide internship and co-op opportunities with major engineering companies.",
                "type": "industry_connections",
                "category": "professional_development"
            },
            
            # 常见问题
            {
                "text": "Students can change their specialization track after the first semester. Consult with academic advisor for course planning.",
                "type": "academic_advice",
                "category": "course_planning"
            },
            {
                "text": "Thesis option requires 6 credit hours of research and a written thesis. Non-thesis option requires additional coursework.",
                "type": "academic_requirements",
                "category": "graduation_options"
            },
            {
                "text": "Prerequisites for advanced courses include completion of core engineering courses and maintaining good academic standing.",
                "type": "academic_requirements",
                "category": "course_planning"
            },
            
            # 学习技巧
            {
                "text": "Time management is crucial for MAE students. Use study groups, office hours, and academic resources effectively.",
                "type": "study_advice",
                "category": "academic_support"
            },
            {
                "text": "Engineering design projects require collaboration, critical thinking, and practical application of theoretical knowledge.",
                "type": "project_guidance",
                "category": "academic_support"
            },
            {
                "text": "Graduate school preparation includes research experience, strong GPA, and relevant coursework in chosen specialization.",
                "type": "graduate_preparation",
                "category": "academic_advancement"
            }
        ]
        
        # 预计算所有文档的嵌入向量
        self._compute_embeddings()
    
    def _compute_embeddings(self):
        """预计算所有文档的嵌入向量"""
        try:
            self.embeddings = []
            for item in self.knowledge_data:
                embedding = self.embedder.encode(item['text'])
                self.embeddings.append(embedding)
            self.embeddings = np.array(self.embeddings)
        except Exception as e:
            print(f"Error computing embeddings: {str(e)}")
            # 如果嵌入失败，使用空列表
            self.embeddings = []
    
    def search(self, query: str, n_results: int = 3) -> List[str]:
        """搜索相关知识"""
        try:
            if len(self.embeddings) == 0:
                return []
            
            # 计算查询的嵌入向量
            query_embedding = self.embedder.encode(query)
            
            # 计算余弦相似度
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # 获取最相似的文档
            top_indices = np.argsort(similarities)[-n_results:][::-1]
            
            # 返回相关文档
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # 相似度阈值
                    results.append(self.knowledge_data[idx]['text'])
            
            return results
            
        except Exception as e:
            print(f"Knowledge base search error: {str(e)}")
            return []
    
    def get_knowledge_by_category(self, category: str) -> List[str]:
        """根据类别获取知识"""
        try:
            results = []
            for item in self.knowledge_data:
                if item['category'] == category:
                    results.append(item['text'])
            return results
        except Exception as e:
            print(f"Error getting knowledge by category: {str(e)}")
            return []
    
    def get_knowledge_by_type(self, type_name: str) -> List[str]:
        """根据类型获取知识"""
        try:
            results = []
            for item in self.knowledge_data:
                if item['type'] == type_name:
                    results.append(item['text'])
            return results
        except Exception as e:
            print(f"Error getting knowledge by type: {str(e)}")
            return []
