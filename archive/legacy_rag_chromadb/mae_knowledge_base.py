import json
import chromadb
from sentence_transformers import SentenceTransformer

class MAEKnowledgeBase:
    def __init__(self):
        # 初始化向量数据库
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("mae_knowledge")
        
        # 初始化嵌入模型
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 初始化知识库
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化MAE专业知识库"""
        knowledge_data = [
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
        
        # 向量化并存储
        for i, item in enumerate(knowledge_data):
            embedding = self.embedder.encode(item['text'])
            self.collection.add(
                ids=[f"doc_{i}"],
                embeddings=[embedding.tolist()],
                documents=[item['text']],
                metadatas=[{"type": item['type'], "category": item['category']}]
            )
    
    def search(self, query, n_results=3):
        """搜索相关知识"""
        try:
            query_embedding = self.embedder.encode(query)
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Knowledge base search error: {str(e)}")
            return []
