"""
Few-Shot Learning Examples for Student Reply Generation
从6000条真实对话数据中加载和使用Few-Shot示例
"""

from typing import List, Dict, Optional
import json
import pandas as pd
from pathlib import Path
import os

# 导入策略矩阵
try:
    from strategy_matrix import get_strategy_for_intent, map_intent_to_strategy_key
    STRATEGY_MATRIX_AVAILABLE = True
except ImportError:
    STRATEGY_MATRIX_AVAILABLE = False
    print("⚠️ 策略矩阵模块不可用，将不使用策略指导")

# ============================================================================
# 📋 配置部分：根据你的6000条数据修改这里
# ============================================================================

# 数据文件路径（修改为你的实际路径）
DATA_FILE_PATH = "data/peer_dataset_26.xlsm"  # 或 .csv

# 列名映射（根据你的实际列名修改）
# peer_dataset_26.xlsm 格式：Mentor, Mentee, Mentor Label, Mentee Label
COLUMN_MAPPING = {
    "advisor": "Mentor",        # 顾问/导师的列名
    "student": "Mentee",         # 学生的列名
    "intent": "Mentee Label",    # 意图标签的列名（使用学生的意图标签）
    "persona": "Persona",        # Persona类型的列名（alpha/beta/delta/echo，如果存在）
    "dialogue": "dialogue",     # 对话文本列（用于兼容其他格式）
}

# 如果列名不同，修改上面的映射
# 例如：如果列名是 "Advisor", "Mentee", "Category", "Type"
# 则改为：
# COLUMN_MAPPING = {
#     "advisor": "Advisor",
#     "student": "Mentee", 
#     "intent": "Category",
#     "persona": "Type",
# }

# ============================================================================
# 🔧 核心功能（通常不需要修改）
# ============================================================================

# 缓存加载的数据
_LOADED_CONVERSATIONS = None
_LOADED_EXAMPLES = None
_PDF_DIALOGUES = None  # PDF中提取的对话

def load_conversations_from_file(file_path: Optional[str] = None) -> List[Dict]:
    """
    从数据文件加载所有对话
    
    Args:
        file_path: 数据文件路径（可选，默认使用配置中的路径）
    
    Returns:
        对话列表，每个对话包含 advisor, student, intent, persona
    """
    global _LOADED_CONVERSATIONS
    
    # 如果已经加载过，直接返回缓存
    if _LOADED_CONVERSATIONS is not None:
        return _LOADED_CONVERSATIONS
    
    file_path = file_path or DATA_FILE_PATH
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"⚠️ 数据文件不存在: {file_path}")
        print(f"   请修改 few_shot_examples.py 中的 DATA_FILE_PATH")
        return []
    
    try:
        # 根据文件扩展名选择读取方式
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm']:
            # .xlsm 是带宏的 Excel 文件，也可以用 read_excel 读取
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            print(f"⚠️ 不支持的文件格式: {file_path.suffix}")
            return []
        
        print(f"✅ 成功加载数据文件: {file_path}")
        print(f"   数据行数: {len(df)}")
        print(f"   列名: {list(df.columns)}")
        
        # 检查数据格式：是否有明确的 Advisor/Student 列，还是只有 dialogue 列
        advisor_col = COLUMN_MAPPING.get("advisor")
        student_col = COLUMN_MAPPING.get("student")
        dialogue_col = COLUMN_MAPPING.get("dialogue")
        intent_col = COLUMN_MAPPING.get("intent")
        
        # 转换为对话列表
        conversations = []
        
        # 情况1：有明确的 Advisor 和 Student 列（标准格式）
        if advisor_col in df.columns and student_col in df.columns:
            print("   使用标准格式（Advisor/Student 列）")
            for _, row in df.iterrows():
                advisor_text = str(row.get(advisor_col, "")).strip()
                student_text = str(row.get(student_col, "")).strip()
                
                if not advisor_text or not student_text:
                    continue
                
                conv = {
                    "advisor": advisor_text,
                    "student": student_text,
                    "intent": str(row.get(intent_col, "")).strip() if intent_col in df.columns else None,
                    "persona": str(row.get(COLUMN_MAPPING.get("persona", ""), "")).strip().lower() if COLUMN_MAPPING.get("persona") in df.columns else None,
                }
                conversations.append(conv)
        
        # 情况2：只有 dialogue 列（new_balanced.xlsx 格式），需要从对话文本中提取
        elif dialogue_col in df.columns:
            print("   检测到 dialogue 格式，尝试从对话文本中提取 Advisor/Student 对")
            import re
            
            for _, row in df.iterrows():
                dialogue_text = str(row.get(dialogue_col, "")).strip()
                if not dialogue_text:
                    continue
                
                # 尝试从 dialogue 中提取对话对
                # 方法1：按句子分割，假设交替的句子是 Advisor 和 Student
                sentences = re.split(r'[.!?]+\s+', dialogue_text)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # 如果句子数 >= 2，尝试配对
                if len(sentences) >= 2:
                    # 假设前一半是 Advisor，后一半是 Student（或交替）
                    # 这里使用简单的策略：前半部分作为 Advisor，后半部分作为 Student
                    mid_point = len(sentences) // 2
                    advisor_text = ". ".join(sentences[:mid_point])
                    student_text = ". ".join(sentences[mid_point:])
                    
                    # 如果提取的文本太短，跳过
                    if len(advisor_text) < 10 or len(student_text) < 10:
                        continue
                    
                    conv = {
                        "advisor": advisor_text,
                        "student": student_text,
                        "intent": str(row.get(intent_col, "")).strip() if intent_col in df.columns else None,
                        "persona": None,  # new_balanced.xlsx 没有 persona 列
                    }
                    conversations.append(conv)
                else:
                    # 如果只有一句话，尝试作为 Student 回复（假设 Advisor 消息在前一轮）
                    if len(sentences) == 1 and len(sentences[0]) > 10:
                        # 这种情况下，我们只能使用 dialogue 作为 student，advisor 留空
                        # 但 Few-Shot 需要完整的对话对，所以跳过单句
                        continue
        
        else:
            print(f"⚠️ 数据格式不支持！")
            print(f"   需要的列: Advisor/Student 或 dialogue")
            print(f"   实际列: {list(df.columns)}")
            print(f"   请检查数据文件格式或修改 COLUMN_MAPPING")
            return []
        
        print(f"✅ 成功解析 {len(conversations)} 条对话")
        
        # 缓存结果
        _LOADED_CONVERSATIONS = conversations
        return conversations
        
    except Exception as e:
        print(f"❌ 加载数据文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_pdf_dialogues() -> List[Dict]:
    """
    从PDF提取的对话中加载对话对
    
    Returns:
        对话列表，格式与load_conversations_from_file()相同
    """
    global _PDF_DIALOGUES
    
    # 如果已经加载过，直接返回缓存
    if _PDF_DIALOGUES is not None:
        return _PDF_DIALOGUES
    
    pdf_json_path = Path("data/extracted_pdf_content.json")
    
    if not pdf_json_path.exists():
        # 如果JSON文件不存在，尝试直接提取
        try:
            from extract_pdf_content import extract_pdf_content, extract_dialogue_pairs
            extracted = extract_pdf_content()
            if extracted:
                dialogue_pairs = extract_dialogue_pairs(extracted.get('dialogue_examples', []))
                
                # 转换为标准格式
                conversations = []
                for pair in dialogue_pairs:
                    conversations.append({
                        "advisor": pair.get('advisor', ''),
                        "student": pair.get('student', ''),
                        "intent": None,  # PDF对话可能没有明确的intent标签
                        "persona": None,  # 需要根据场景推断
                        "source": "pdf_training_package"
                    })
                
                _PDF_DIALOGUES = conversations
                if conversations:
                    print(f"✅ 从PDF加载了 {len(conversations)} 个对话对")
                return conversations
        except Exception as e:
            print(f"⚠️ 加载PDF对话时出错: {e}")
            _PDF_DIALOGUES = []
            return []
    
    # 从JSON文件加载
    try:
        import json
        with open(pdf_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dialogue_pairs = data.get('dialogue_pairs', [])
        
        # 转换为标准格式
        conversations = []
        for pair in dialogue_pairs:
            conversations.append({
                "advisor": pair.get('advisor', ''),
                "student": pair.get('student', ''),
                "intent": None,  # PDF对话可能没有明确的intent标签
                "persona": None,  # 需要根据场景推断
                "source": "pdf_training_package"
            })
        
        _PDF_DIALOGUES = conversations
        if conversations:
            print(f"✅ 从PDF JSON加载了 {len(conversations)} 个对话对")
        return conversations
        
    except Exception as e:
        print(f"⚠️ 加载PDF对话JSON时出错: {e}")
        _PDF_DIALOGUES = []
        return []

def get_few_shot_examples(persona: str, 
                         advisor_message: str,
                         intent: Optional[str] = None,
                         num_examples: int = 2,
                         examples_source: Optional[List[Dict]] = None) -> List[Dict]:
    """
    根据persona和advisor消息选择最相关的Few-Shot示例
    
    Args:
        persona: 学生persona类型 (alpha, beta, delta, echo)
        advisor_message: 顾问的消息
        intent: 意图类别（可选，用于筛选相关示例）
        num_examples: 返回的示例数量
        examples_source: 自定义示例源（可选，默认从文件加载）
    
    Returns:
        选中的Few-Shot示例列表
    """
    # 如果没有提供示例源，从文件加载
    if examples_source is None:
        examples_source = load_conversations_from_file()
        
        # 添加PDF中提取的对话（如果可用）
        pdf_dialogues = load_pdf_dialogues()
        if pdf_dialogues:
            examples_source.extend(pdf_dialogues)
    
    if not examples_source:
        # 如果加载失败，返回空列表（系统会fallback到原始方法）
        return []
    
    # 过滤：只选择匹配persona的示例（包括PDF对话）
    persona_lower = persona.lower()
    persona_examples = [
        ex for ex in examples_source 
        if (ex.get("persona") and ex.get("persona").lower() == persona_lower) or
           ex.get("source") == "pdf_training_package"  # 包含PDF对话（它们可能匹配任何persona）
    ]
    
    # 如果没有匹配的persona，使用所有示例
    if not persona_examples:
        persona_examples = examples_source
        print(f"⚠️ 未找到 {persona} persona的示例，使用所有示例")
    
    # 如果指定了intent，进一步过滤
    if intent:
        matching_examples = [
            ex for ex in persona_examples 
            if ex.get("intent") and intent.lower() in ex.get("intent", "").lower()
        ]
        if matching_examples:
            persona_examples = matching_examples
    
    # 改进的相似度匹配：使用序列相似度 + 关键词 + Intent匹配
    from difflib import SequenceMatcher
    
    advisor_lower = advisor_message.lower()
    scored_examples = []
    
    for example in persona_examples:
        score = 0
        advisor_example = example.get("advisor", "").lower()
        
        # 方法1：序列相似度（比关键词匹配更准确）
        similarity = SequenceMatcher(None, advisor_lower, advisor_example).ratio()
        score += similarity * 10  # 权重10（最重要）
        
        # 方法2：关键词匹配（作为补充）
        advisor_words = set(advisor_lower.split())
        example_words = set(advisor_example.split())
        
        # 移除停用词
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'to', 'of', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 
                     'with', 'by', 'from', 'as', 'this', 'that', 'these', 'those',
                     'so', 'do', 'does', 'did', 'can', 'could', 'will', 'would',
                     'have', 'has', 'had', 'what', 'which', 'when', 'where', 'why', 'how'}
        advisor_words = advisor_words - stop_words
        example_words = example_words - stop_words
        
        common_words = advisor_words & example_words
        score += len(common_words) * 0.5  # 权重0.5（补充）
        
        # 方法3：Intent匹配（重要加分）
        if intent and example.get("intent"):
            if intent.lower() in example.get("intent", "").lower():
                score += 5  # 重要加分
        
        scored_examples.append((score, example))
    
    # 按分数排序
    scored_examples.sort(key=lambda x: x[0], reverse=True)
    
    # 改进：多样性选择（避免选择太相似的示例）
    selected = []
    for score, ex in scored_examples:
        if len(selected) >= num_examples:
            break
        
        # 检查与已选示例的相似度
        is_diverse = True
        for selected_ex in selected:
            selected_text = selected_ex.get("advisor", "").lower()
            current_text = ex.get("advisor", "").lower()
            similarity = SequenceMatcher(None, selected_text, current_text).ratio()
            if similarity > 0.75:  # 如果太相似（>75%），跳过以保持多样性
                is_diverse = False
                break
        
        if is_diverse:
            selected.append(ex)
    
    # 如果还不够，补充其他示例（优先选择高分但不同的）
    if len(selected) < num_examples:
        remaining = [(score, ex) for score, ex in scored_examples if ex not in selected]
        # 按分数排序，选择不同的
        remaining.sort(key=lambda x: x[0], reverse=True)
        for score, ex in remaining:
            if len(selected) >= num_examples:
                break
            # 再次检查多样性
            is_diverse = True
            for selected_ex in selected:
                selected_text = selected_ex.get("advisor", "").lower()
                current_text = ex.get("advisor", "").lower()
                similarity = SequenceMatcher(None, selected_text, current_text).ratio()
                if similarity > 0.75:
                    is_diverse = False
                    break
            if is_diverse:
                selected.append(ex)
    
    # 如果还是不够，随机补充（最后手段）
    if len(selected) < num_examples:
        remaining = [ex for score, ex in scored_examples if ex not in selected]
        import random
        if remaining:
            selected.extend(random.sample(remaining, min(num_examples - len(selected), len(remaining))))
    
    return selected

def format_few_shot_prompt(examples: List[Dict], 
                          advisor_message: str,
                          persona: str,
                          persona_info: Dict,
                          conversation_context: str = None,
                          advisor_intent: Optional[str] = None) -> str:
    """
    格式化Few-Shot Prompt
    
    Args:
        examples: Few-Shot示例列表
        advisor_message: 当前顾问消息
        persona: 学生persona类型
        persona_info: Persona详细信息
    
    Returns:
        格式化后的prompt
    """
    # 如果没有示例，返回基本prompt
    if not examples:
        return f"""You are a {persona.upper()} type MAE student having a conversation with a peer advisor.

Persona Characteristics:
- Description: {persona_info.get('description', '')}
- Traits: {', '.join(persona_info.get('traits', []))}
- Help Seeking: {persona_info.get('help_seeking_behavior', '')}

Peer Advisor said: "{advisor_message}"

Generate a natural and authentic response as this {persona.upper()} student (1-3 sentences).
Student response:"""
    
    # 构建示例部分
    examples_text = "Here are some examples of similar conversations:\n\n"
    
    for i, example in enumerate(examples, 1):
        examples_text += f"Example {i}:\n"
        examples_text += f"Advisor: {example.get('advisor', '')}\n"
        examples_text += f"Student ({persona.upper()}): {example.get('student', '')}\n"
        if example.get('intent'):
            examples_text += f"Intent: {example.get('intent')}\n"
        examples_text += "\n"
    
    # 提取最后一条advisor消息（如果包含对话历史）
    if "Now the advisor says:" in advisor_message:
        last_advisor_msg = advisor_message.split("Now the advisor says:")[-1].strip()
    else:
        last_advisor_msg = advisor_message
    
    # 构建完整prompt
    context_section = ""
    if conversation_context or ("Previous conversation:" in advisor_message):
        if "Previous conversation:" in advisor_message:
            context_section = advisor_message.split("Now the advisor says:")[0].strip() + "\n\n"
        elif conversation_context:
            context_section = f"Previous conversation:\n{conversation_context}\n\n"
    
    # 根据Persona类型添加特定的语言风格指导
    persona_style_guide = ""
    if persona.lower() == "beta":
        persona_style_guide = """
BETA PERSONA LANGUAGE STYLE (STRICT):
- Use hesitant, uncertain language: "I'm not sure...", "I'm worried that...", "Maybe I should...", "I don't know if..."
- Express self-doubt: "I'm afraid I'm not qualified...", "I don't think I'm good enough...", "Maybe I made a mistake..."
- Show embarrassment: "I'm too embarrassed to...", "I don't want people to think...", "I'm worried about what others will think..."
- Avoid confident statements - NEVER say "I'm confident", "I'm ready", "I've decided"
- Use conditional language: "I might...", "I could...", "I'm thinking maybe..."
- Show hesitation: "I'm not really sure...", "I'm kind of...", "I guess..."
"""
    elif persona.lower() == "alpha":
        persona_style_guide = """
ALPHA PERSONA LANGUAGE STYLE:
- Cautious but open: "I'm thinking about...", "I'm interested in...", "I'm willing to..."
- Shows uncertainty but willingness: "I'm not sure if I'm ready, but...", "I'm worried about X, but I want to try..."
"""
    elif persona.lower() == "delta":
        persona_style_guide = """
DELTA PERSONA LANGUAGE STYLE:
- Confident but strategic: "I'm doing well, but...", "I want to make sure...", "I'm considering..."
- Worries about others' opinions: "I'm not sure if this is the right approach...", "I want to make sure I'm competitive..."
"""
    elif persona.lower() == "echo":
        persona_style_guide = """
ECHO PERSONA LANGUAGE STYLE:
- Very confident and proactive: "I'm excited about...", "I want to...", "I'm ready to...", "I'm confident that..."
- Enthusiastic and decisive
"""
    
    # 获取策略指导（如果可用）
    strategy_guide = ""
    if STRATEGY_MATRIX_AVAILABLE and advisor_intent:
        strategy = get_strategy_for_intent(persona, advisor_intent)
        if strategy:
            # 构建策略指导部分
            do_items = strategy.get('do_list', [])[:4]  # 最多4条
            avoid_items = strategy.get('avoid_list', [])[:4]  # 最多4条
            core_strategy = strategy.get('core_strategy', '')
            
            if core_strategy or do_items or avoid_items:
                strategy_guide = f"""
ADVISOR STRATEGY CONTEXT (understand how the advisor is approaching this conversation):
The advisor is using a strategy for "{advisor_intent}" with a {persona.upper()} student.

Core Strategy: {core_strategy[:250]}...

Key things the advisor is trying to DO:
{chr(10).join(['• ' + item[:120] for item in do_items]) if do_items else '• Focus on student needs'}

Key things the advisor is trying to AVOID:
{chr(10).join(['• ' + item[:120] for item in avoid_items]) if avoid_items else '• Generic responses'}

As a {persona.upper()} student, respond authentically to this advisor approach. Your response should feel natural given this strategy context.
"""
    
    prompt = f"""You are a {persona.upper()} type MAE student having a conversation with a peer advisor.

Persona Characteristics:
- Description: {persona_info.get('description', '')}
- Traits: {', '.join(persona_info.get('traits', []))}
- Help Seeking: {persona_info.get('help_seeking_behavior', '')}

{persona_style_guide}

{strategy_guide}

{examples_text}

{context_section}Now, the peer advisor just said:
"{last_advisor_msg}"

CRITICAL INSTRUCTIONS - Follow these rules strictly:

1. **ANSWER DIRECTLY** - If the advisor asks a specific question, give a specific answer:
   - "Which semester?" → Answer with a semester (e.g., "This is my second semester" or "I'm in my third year")
   - "What courses?" → List specific courses or describe your course plan
   - "Have you taken X?" → Answer yes/no and provide details
   - DO NOT say "I need to check" or "I'm still figuring it out" unless that's genuinely true

2. **USE CONVERSATION CONTEXT** - Reference what was said earlier if relevant:
   - If advisor asked about courses earlier, you can reference that
   - If you mentioned something before, be consistent
   - Show you're following the conversation

3. **BE NATURAL** - Match the style in the examples above:
   - Use conversational language (not overly formal)
   - Show personality based on your persona
   - Be authentic, like a real student

4. **BE SPECIFIC** - Give concrete information:
   - Instead of "some courses" → "Physics 1 and Calculus 2"
   - Instead of "a while" → "about two semesters"
   - Instead of vague → specific details

5. **LENGTH** - Keep it 1-3 sentences, but be complete:
   - Answer the question fully
   - Don't cut off mid-thought
   - Be concise but informative

6. **PERSONA CONSISTENCY** - CRITICAL: Your response MUST match your persona's characteristics exactly:

   **ALPHA Persona:**
   - Moderately below average confidence
   - Willing to ask questions but unsure
   - Interested but needs reassurance
   - Language: "I'm thinking about...", "I'm not sure if...", "I'm willing to learn but..."
   - Tone: Cautious but open, slightly uncertain
   - After receiving helpful advice: Can show more confidence and appreciation, become more engaged

   **BETA Persona (VERY IMPORTANT):**
   - VERY LOW confidence and self-efficacy
   - Hesitant, embarrassed to ask for help
   - Avoids questions, sensitive to peer perception
   - Language: "I'm worried that...", "I don't know if I'm qualified...", "I'm afraid that...", "Maybe I should...", "I'm not sure if I can..."
   - Tone: Self-doubting, hesitant, apologetic, uncertain
   - DO NOT: Sound confident, proactive, or decisive
   - DO: Express doubt, hesitation, worry about being judged
   - After receiving helpful advice: May show slight improvement in confidence, more willingness to engage, but still cautious and self-doubting

   **DELTA Persona:**
   - Moderately above average confidence
   - Hesitant to seek help (worries about others' opinions)
   - NOT interested in research (DO NOT mention research topics)
   - Language: "I'm doing well but...", "I want to make sure...", "I'm not sure if this is the right approach..."
   - Tone: Confident but cautious, strategic, indirect
   - Focus on: internships, clubs, career preparation, practical applications
   - After receiving helpful advice: Can become more open and engaged, show appreciation, become more proactive while maintaining strategic thinking

   **ECHO Persona:**
   - Very high confidence
   - Proactive, asks for help freely
   - Language: "I'm excited about...", "I want to...", "I'm ready to...", "I'm confident that..."
   - Tone: Enthusiastic, confident, proactive
   - After receiving helpful advice: Shows strong appreciation, becomes even more motivated, asks follow-up questions enthusiastically

7. **PROGRESSIVE ENGAGEMENT** - IMPORTANT: As the conversation progresses and the advisor provides helpful guidance:
   - If the advisor's advice is helpful and addresses your concerns, you can show positive changes:
     * ALPHA: Become more confident, more engaged, show appreciation
     * BETA: Show slight improvement, become slightly more open, but still cautious
     * DELTA: Become more open and engaged, show appreciation, become more proactive
     * ECHO: Show strong appreciation, become even more enthusiastic and motivated
   - Give the advisor confidence by showing that their help is making a difference
   - However, maintain your core persona characteristics (don't completely change personality)
   - The improvement should be gradual and realistic based on your persona's baseline

Based on the examples above and your persona characteristics, generate a natural and authentic response as this {persona.upper()} student.

REMEMBER: Your response MUST sound like a {persona.upper()} student. If you're BETA, you MUST sound hesitant, uncertain, and self-doubting. If you're ECHO, you MUST sound confident and proactive. Match the persona's language style exactly. If the advisor has been helpful, show appropriate positive changes while maintaining your core persona.

Student response:"""
    
    return prompt

# 默认示例（如果数据文件不存在时使用）
FEW_SHOT_EXAMPLES = {
    "alpha": [
        {
            "advisor": "That's a great question! Research experience is really valuable. Have you thought about which professors' work interests you?",
            "student": "I'm interested in robotics, but I'm not sure if I have the right background. I'm willing to learn, but I don't want to waste a professor's time if I'm not qualified.",
            "intent": "Goal Setting and Planning",
            "persona": "alpha"
        }
    ],
    "beta": [],
    "delta": [],
    "echo": []
}

# ============================================================================
# 🧪 测试和调试函数
# ============================================================================

def test_data_loading():
    """测试数据加载功能"""
    print("=" * 60)
    print("🧪 测试数据加载")
    print("=" * 60)
    
    conversations = load_conversations_from_file()
    
    if conversations:
        print(f"\n✅ 成功加载 {len(conversations)} 条对话")
        print(f"\n前3条示例:")
        for i, conv in enumerate(conversations[:3], 1):
            print(f"\n示例 {i}:")
            print(f"  Advisor: {conv.get('advisor', '')[:80]}...")
            print(f"  Student: {conv.get('student', '')[:80]}...")
            print(f"  Intent: {conv.get('intent', 'N/A')}")
            print(f"  Persona: {conv.get('persona', 'N/A')}")
        
        # 统计persona分布
        persona_counts = {}
        for conv in conversations:
            persona = conv.get('persona', 'unknown')
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        print(f"\n📊 Persona分布:")
        for persona, count in persona_counts.items():
            print(f"  {persona}: {count} 条")
    else:
        print("\n❌ 数据加载失败")
        print("\n请检查:")
        print("  1. DATA_FILE_PATH 是否正确")
        print("  2. COLUMN_MAPPING 中的列名是否匹配")
        print("  3. 数据文件是否存在")

def test_example_selection():
    """测试示例选择功能"""
    print("=" * 60)
    print("🧪 测试示例选择")
    print("=" * 60)
    
    advisor_message = "What courses are you taking next semester?"
    persona = "alpha"
    intent = "Goal Setting and Planning"
    
    examples = get_few_shot_examples(
        persona=persona,
        advisor_message=advisor_message,
        intent=intent,
        num_examples=2
    )
    
    print(f"\n为以下输入选择的示例:")
    print(f"  Advisor: {advisor_message}")
    print(f"  Persona: {persona}")
    print(f"  Intent: {intent}")
    
    if examples:
        print(f"\n✅ 找到 {len(examples)} 个相关示例:")
        for i, ex in enumerate(examples, 1):
            print(f"\n示例 {i}:")
            print(f"  Advisor: {ex.get('advisor', '')[:80]}...")
            print(f"  Student: {ex.get('student', '')[:80]}...")
            print(f"  Intent: {ex.get('intent', 'N/A')}")
    else:
        print("\n⚠️ 未找到相关示例")

if __name__ == "__main__":
    # 运行测试
    test_data_loading()
    print("\n")
    test_example_selection()
