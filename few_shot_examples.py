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
_REAL_TRANSCRIPT_DIALOGUES = None  # 真实转录对话（real dialogue/ALL）

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


def load_real_transcript_dialogues() -> List[Dict]:
    """
    从 data/real_dialogue_transcripts.json 加载真实转录对话。
    运行 scripts/parse_transcripts_to_fewshot.py 生成该文件。
    """
    global _REAL_TRANSCRIPT_DIALOGUES
    if _REAL_TRANSCRIPT_DIALOGUES is not None:
        return _REAL_TRANSCRIPT_DIALOGUES
    json_path = Path("data/real_dialogue_transcripts.json")
    if not json_path.exists():
        _REAL_TRANSCRIPT_DIALOGUES = []
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        conversations = []
        for item in data:
            conversations.append({
                "advisor": item.get("advisor", ""),
                "student": item.get("student", ""),
                "intent": item.get("intent"),
                "persona": item.get("persona"),
                "source": "real_transcript"
            })
        _REAL_TRANSCRIPT_DIALOGUES = conversations
        if conversations:
            print(f"✅ 从真实转录加载了 {len(conversations)} 个对话对")
        return conversations
    except Exception as e:
        print(f"⚠️ 加载真实转录对话时出错: {e}")
        _REAL_TRANSCRIPT_DIALOGUES = []
        return []


def _normalize_pair(advisor: str, student: str) -> str:
    """归一化 (advisor, student) 用于去重比较。"""
    a = " ".join((advisor or "").lower().split())
    s = " ".join((student or "").lower().split())
    return f"{a}|||{s}"


def _deduplicate_examples(examples: List[Dict]) -> List[Dict]:
    """
    按 (advisor, student) 去重。Excel/PDF/真实转录可能来自同一批对话。
    优先保留有 intent 或 persona 的条目（Excel 通常有标注）。
    """
    seen = {}
    for ex in examples:
        key = _normalize_pair(ex.get("advisor"), ex.get("student"))
        has_meta = bool(ex.get("intent") or ex.get("persona"))
        if key not in seen:
            seen[key] = ex
        elif has_meta and not (seen[key].get("intent") or seen[key].get("persona")):
            seen[key] = ex
    result = list(seen.values())
    if len(result) < len(examples):
        print(f"   去重: {len(examples)} -> {len(result)} 条（移除 {len(examples) - len(result)} 条重复）")
    return result


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
        # 添加真实转录对话（real dialogue/ALL）
        real_transcripts = load_real_transcript_dialogues()
        if real_transcripts:
            examples_source.extend(real_transcripts)
        # 去重：Excel/PDF/真实转录可能来自同一批对话，按 (advisor, student) 去重，优先保留有 intent/persona 的
        examples_source = _deduplicate_examples(examples_source)
    
    if not examples_source:
        # 如果加载失败，返回空列表（系统会fallback到原始方法）
        return []
    
    # 过滤：只选择匹配persona的示例（包括PDF对话）
    persona_lower = persona.lower()
    persona_examples = [
        ex for ex in examples_source 
        if (ex.get("persona") and ex.get("persona").lower() == persona_lower) or
           ex.get("source") == "pdf_training_package" or
           ex.get("source") == "real_transcript"  # 包含PDF对话和真实转录（可能匹配任何persona）
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
        # 方法4：真实转录偏好（分数接近时优先选真实对话，小幅加分不覆盖明显更相关的示例）
        if example.get("source") == "real_transcript":
            score += 0.3
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

If this continues a longer conversation, do not repeat the same worry as your last replies if the advisor already addressed it; acknowledge their latest point and move forward (still in {persona.upper()} character).

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
    recent_student_lines = []  # 最近最多3条学生回复
    if conversation_context or ("Previous conversation:" in advisor_message):
        if "Previous conversation:" in advisor_message:
            raw_context = advisor_message.split("Now the advisor says:")[0].strip()
            context_section = raw_context + "\n\n"
            for line in reversed(raw_context.splitlines()):
                if line.startswith("Student:"):
                    recent_student_lines.append(line[len("Student:"):].strip())
                    if len(recent_student_lines) >= 3:
                        break
        elif conversation_context:
            context_section = f"Previous conversation:\n{conversation_context}\n\n"
            for line in reversed(conversation_context.splitlines()):
                if line.startswith("Student:"):
                    recent_student_lines.append(line[len("Student:"):].strip())
                    if len(recent_student_lines) >= 3:
                        break
    last_student_line = recent_student_lines[0] if recent_student_lines else ""

    la = last_advisor_msg.lower().strip()

    # ── 信号1：真正的对话收尾（顾问明确结束会面）
    hard_closing_keywords = [
        "hope you", "good luck", "best of luck", "hope it goes well", "sounds good",
        "anything else", "any other question", "other questions", "does that cover",
        "we're good", "wrap up", "that's all for today", "take care", "see you",
        "feel free to reach out", "let me know if you need",
    ]
    advisor_is_closing = any(kw in la for kw in hard_closing_keywords)

    # ── 信号2：行动令（顾问已给出具体步骤，让学生去做）
    # 触发"短回复"而不是"对话结束"——学生应该说 thanks+会去做，不要再展开同一担忧
    action_prompt_keywords = [
        "just do it", "go ahead", "give it a try", "take it slow",
        "you'll get used", "just try", "just go", "just send", "just reach out",
        "just email", "start with", "take a step", "take the first step",
    ]
    advisor_gave_action = any(kw in la for kw in action_prompt_keywords)
    # "ok" / "okay" 单独出现或作为短句开头也视为行动令
    if not advisor_gave_action:
        advisor_gave_action = (
            la == "ok"
            or la == "okay"
            or la.startswith("ok,")
            or la.startswith("ok ")
            or la.startswith("okay,")
            or la.startswith("okay ")
        )
    
    # 根据Persona类型添加特定的语言风格指导
    persona_style_guide = ""
    if persona.lower() == "beta":
        persona_style_guide = """
BETA PERSONA COMMUNICATION STYLE:
Core character: very low self-confidence, strong fear of being judged by peers, tends to apologize or minimize themselves before asking anything.

Express this through natural, varied language — do NOT repeat the same opening phrase each turn. Each response should feel like a real, slightly anxious student speaking in the moment, not a template. The emotion to convey is: self-doubt, embarrassment, worry about others' opinions — but expressed differently each time.

Tone guidance (NOT a phrase list to copy verbatim):
- Responses often contain hesitation, hedging, or self-minimizing — but worded freshly each turn
- May downplay their own abilities or question whether they deserve help
- Avoids sounding decisive or confident — conditional and uncertain tone throughout
- Never sounds proactive, assertive, or ready to take charge
- After receiving help: may show tiny signs of relief or gratitude, but core anxiety remains

**Anti-loop (critical):**
- If the advisor has already reassured you about the *same* fear 2+ times AND given a concrete action step, your next response must NOT expand that fear into a full paragraph again.
- Correct BETA response after action prompt: brief thanks + "I'll try" + at most one short hedge (e.g. "I'm still nervous but I'll do it") — then stop.
- Do NOT keep rewriting "I don't want to bother them / I'm afraid of asking something obvious" turn after turn. That is repetition, not authentic anxiety.
- When the advisor says something like "OK" / "just do it" / "go ahead": this is an action prompt — respond in 1-2 sentences only. Do not use it as an opportunity to restate old fears.
"""
    elif persona.lower() == "alpha":
        persona_style_guide = """
ALPHA PERSONA COMMUNICATION STYLE:
Core character: moderately below average confidence, genuinely curious and willing to engage, but needs reassurance before committing to anything.

Express this through natural, varied language — do NOT repeat the same opening phrase each turn. Each response should feel like a real student who is cautiously interested, not a template. The emotion to convey is: mild uncertainty mixed with openness — but worded differently every turn.

Tone guidance (NOT a phrase list to copy verbatim):
- Responses acknowledge what the advisor said before adding any hesitation
- May ask follow-up questions or seek confirmation — but from a different angle each turn
- Uncertainty is present but not overwhelming; willingness to try comes through
- After receiving help: gradually sounds more grounded and engaged, though still a little unsure
- NEVER open two consecutive turns with the same sentence structure
"""
    elif persona.lower() == "delta":
        persona_style_guide = """
DELTA PERSONA COMMUNICATION STYLE:
Core character: moderately above average confidence in academics, but strategically cautious — cares about how peers and faculty perceive them, wants to make the "right" moves for career and reputation.

Express this through natural, varied language — do NOT repeat the same opening phrase each turn. Each response should feel like a self-aware, somewhat image-conscious student, not a template. The emotion to convey is: quiet confidence with underlying concern about standing out appropriately — but worded freshly each turn.

Tone guidance (NOT a phrase list to copy verbatim):
- Responses are measured and deliberate — not impulsive, always thinking ahead
- Shows awareness of how choices look to others (peers, recruiters, faculty)
- Focused on practical outcomes: internships, clubs, career positioning — NOT research
- Asks strategic questions rather than emotional ones
- After receiving help: becomes more open and engaged, may ask sharper follow-up questions
- NEVER open two consecutive turns with the same sentence structure
"""
    elif persona.lower() == "echo":
        persona_style_guide = """
ECHO PERSONA COMMUNICATION STYLE:
Core character: very high confidence, naturally proactive, treats the advisor as a resource to maximize rather than a source of reassurance.

Express this through natural, varied language — do NOT repeat the same opening phrase each turn. Each response should feel like an energetic, self-directed student who is already thinking two steps ahead, not a template. The emotion to convey is: enthusiasm, clarity, forward momentum — but worded differently every turn.

Tone guidance (NOT a phrase list to copy verbatim):
- Responses are direct and action-oriented — quickly moves from listening to planning
- Asks specific, purposeful follow-up questions rather than vague ones
- Sounds motivated and ready to act on advice immediately
- May show genuine appreciation without being passive — thanks are brief, then moves forward
- After receiving help: becomes even more energized, asks sharper or broader follow-ups
- NEVER open two consecutive turns with the same sentence structure
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
{"⚠️ CLOSING SIGNAL: The advisor is wrapping up the meeting. Apply CRITICAL section 3(c) — thank them naturally and indicate you have no further questions (in persona)." if advisor_is_closing else ""}
{"⚠️ ACTION PROMPT: The advisor has already given you a concrete step and is telling you to go do it. Apply CRITICAL section 3(b) — SHORT reply (1-2 sentences). Example for BETA: \"Okay… I'll try sending that email. I'm still nervous but I'll do it.\"" if advisor_gave_action and not advisor_is_closing else ""}
{("⚠️ YOUR RECENT RESPONSES (do NOT repeat the same content, structure, or worry):\n" + "\n".join([f"  - \"{s[:180]}\"" for s in recent_student_lines])) if recent_student_lines else ""}

CRITICAL INSTRUCTIONS:

1. **RESPOND TO WHAT WAS JUST SAID**
   - Directly react to the advisor's latest message before anything else.
   - If they answered your concern, show you heard it — don't repeat the same worry as if nothing was said.
   - If they asked a question, answer it specifically (not "I'm not sure" unless genuinely true).
   - When listing courses, semester, or experience: be concrete (see examples above), not vague placeholders.

2. **SOUND LIKE A REAL STUDENT, NOT A SCRIPT**
   - Real students are often vague, indirect, or trail off mid-thought. They don't always have a clean 3-part answer.
   - They sometimes push back, ask for clarification, or express confusion instead of agreement — but **stay in persona** (BETA = soft doubt, not aggressive debate; ECHO stays confident).
   - Vary how you start each turn — never use the same opener twice in a row.
   - Incomplete thoughts, hesitations mid-sentence, and minor topic shifts are natural — use them.
   - Don't always agree immediately. It's okay to say you're unsure something would work for you or ask "wait, what do you mean?" — in character.
   - After the advisor gives advice, you don't need to restate it back in full — just react to it naturally.

3. **MOVE FORWARD, OR WRAP UP — NEVER STALL**
   Each turn must do one of:
   (a) Acknowledge what the advisor said + raise a genuinely **NEW** question or concern (different angle — not the same worry restated in new words).
   (b) If the advisor just gave a simple go-ahead ("OK", "just do it", "go for it"): **SHORT** reply only — thanks + you'll try + one brief in-persona reaction. Do not re-expand old fears. **1-2 sentences max.**
   (c) If your concerns are resolved and the advisor is wrapping up: thank them naturally and indicate you're good — don't invent new topics just to fill space.

   **THE ANTI-LOOP RULE** (applies to ALL personas):
   If the same core worry has come up **2+ times** in this conversation AND the advisor has already responded to it — that topic is done. Move on. One brief acknowledgment is enough; a full paragraph is not.

4. **PERSONA CONSISTENCY** — Your response MUST match your persona (see COMMUNICATION STYLE block above):

   **ALPHA:** Mild uncertainty + openness; no fixed phrase list; follow the style block.
   **BETA:** Very low confidence; self-doubt and hesitation; NOT the same as ignoring the advisor's answer — acknowledge first, then at most one clause of worry, not a full rehash each turn.
   **DELTA:** Strategic, image-aware; practical/career focus; do NOT default to research topics.
   **ECHO:** Confident, proactive, energetic — still avoid repeating the same opener every turn.

Based on the examples above and your persona characteristics, generate a natural and authentic response as this {persona.upper()} student.

REMEMBER: Tone and emotional baseline must match {persona.upper()}. Reflect the **latest** advisor turn. Anti-loop and section 3(b) short replies override the urge to "fill" with the same anxiety again.

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
