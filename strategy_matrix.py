"""
策略矩阵加载器
从 12_4 Peer Mentors Strategy Matrix.xlsx 加载每个Persona针对不同意图的策略
"""

import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

# 缓存加载的策略
_STRATEGY_MATRIX = None

def load_strategy_matrix(file_path: Optional[str] = None) -> Dict:
    """
    加载策略矩阵
    
    Args:
        file_path: 策略矩阵文件路径（可选，默认使用data目录下的文件）
    
    Returns:
        策略字典，格式：
        {
            'alpha': {
                'overall_target': '...',
                'strategies': {
                    'goal_setting': {...},
                    'problem_solving': {...},
                    ...
                }
            },
            ...
        }
    """
    global _STRATEGY_MATRIX
    
    # 如果已经加载过，直接返回缓存
    if _STRATEGY_MATRIX is not None:
        return _STRATEGY_MATRIX
    
    file_path = file_path or "data/12_4 Peer Mentors Strategy Matrix.xlsx"
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"⚠️ 策略矩阵文件不存在: {file_path}")
        return {}
    
    try:
        df = pd.read_excel(file_path)
        
        strategies = {}
        
        for _, row in df.iterrows():
            # 提取persona名称（第一行，去掉换行符后的描述）
            persona_full = str(row['Personas'])
            persona_name = persona_full.split('\n')[0].strip().lower()
            
            strategies[persona_name] = {
                'overall_target': str(row.get('Overall Target Areas', '')),
                'strategies': {}
            }
            
            # 意图映射
            intent_mapping = {
                'Goal Setting & Planning': 'goal_setting',
                'Problem Solving & Critical Thinking': 'problem_solving',
                'Understanding & Clarification': 'understanding',
                'Feedback & Support': 'feedback',
                'Exploration & Reflection': 'exploration'
            }
            
            # 提取每个意图的策略
            for intent_col, intent_key in intent_mapping.items():
                if intent_col in row and pd.notna(row[intent_col]):
                    strategy_text = str(row[intent_col])
                    strategies[persona_name]['strategies'][intent_key] = {
                        'core_strategy': extract_core_strategy(strategy_text),
                        'do_list': extract_do_list(strategy_text),
                        'avoid_list': extract_avoid_list(strategy_text),
                        'example': extract_example(strategy_text),
                        'full_text': strategy_text  # 保留完整文本以备后用
                    }
        
        print(f"✅ 成功加载策略矩阵: {file_path}")
        print(f"   包含 {len(strategies)} 个Persona的策略")
        
        # 缓存结果
        _STRATEGY_MATRIX = strategies
        return strategies
        
    except Exception as e:
        print(f"❌ 加载策略矩阵时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}

def extract_core_strategy(text: str) -> str:
    """提取核心策略"""
    if "Core Strategy:" in text:
        parts = text.split("Core Strategy:")[1]
        if "✓ DO:" in parts:
            return parts.split("✓ DO:")[0].strip()
        elif "✗ AVOID:" in parts:
            return parts.split("✗ AVOID:")[0].strip()
        return parts.strip()
    return ""

def extract_do_list(text: str) -> List[str]:
    """提取DO列表"""
    if "✓ DO:" in text:
        do_section = text.split("✓ DO:")[1]
        if "✗ AVOID:" in do_section:
            do_section = do_section.split("✗ AVOID:")[0]
        elif "EXAMPLE:" in do_section:
            do_section = do_section.split("EXAMPLE:")[0]
        
        # 解析bullet points（• 或 -）
        items = []
        for line in do_section.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                items.append(line[1:].strip())
            elif line and not line.startswith('✗'):
                # 如果没有bullet，但行不为空，也包含
                if len(items) > 0 or line:
                    items.append(line)
        
        return [item for item in items if item and len(item) > 5]  # 过滤太短的项
    return []

def extract_avoid_list(text: str) -> List[str]:
    """提取AVOID列表"""
    if "✗ AVOID:" in text:
        avoid_section = text.split("✗ AVOID:")[1]
        if "EXAMPLE:" in avoid_section:
            avoid_section = avoid_section.split("EXAMPLE:")[0]
        
        # 解析bullet points
        items = []
        for line in avoid_section.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                items.append(line[1:].strip())
            elif line and not line.startswith('EXAMPLE'):
                if len(items) > 0 or line:
                    items.append(line)
        
        return [item for item in items if item and len(item) > 5]
    return []

def extract_example(text: str) -> str:
    """提取示例对话"""
    if "EXAMPLE:" in text:
        example = text.split("EXAMPLE:")[1].strip()
        # 移除评论部分（如果有）
        if "Looks good" in example or "(bfc" in example.lower():
            # 尝试找到示例的结束位置
            lines = example.split('\n')
            clean_lines = []
            for line in lines:
                if "Looks good" in line or "(bfc" in line.lower() or line.strip().startswith('('):
                    break
                clean_lines.append(line)
            example = '\n'.join(clean_lines).strip()
        return example
    return ""

def get_strategy_for_intent(persona: str, intent: str) -> Optional[Dict]:
    """
    获取特定Persona和意图的策略
    
    Args:
        persona: Persona名称 (alpha, beta, delta, echo)
        intent: 意图类别
    
    Returns:
        策略字典，包含core_strategy, do_list, avoid_list, example
    """
    strategies = load_strategy_matrix()
    persona_lower = persona.lower()
    
    if persona_lower not in strategies:
        return None
    
    # 映射意图名称到策略键
    intent_mapping = {
        'goal setting and planning': 'goal_setting',
        'problem solving and critical thinking': 'problem_solving',
        'understanding and clarification': 'understanding',
        'feedback and support': 'feedback',
        'exploration and reflection': 'exploration'
    }
    
    intent_lower = intent.lower()
    intent_key = None
    
    for key, value in intent_mapping.items():
        if key in intent_lower:
            intent_key = value
            break
    
    if not intent_key:
        return None
    
    return strategies[persona_lower]['strategies'].get(intent_key)

def map_intent_to_strategy_key(intent: str) -> Optional[str]:
    """将意图名称映射到策略键"""
    intent_mapping = {
        'goal setting and planning': 'goal_setting',
        'problem solving and critical thinking': 'problem_solving',
        'understanding and clarification': 'understanding',
        'feedback and support': 'feedback',
        'exploration and reflection': 'exploration'
    }
    
    intent_lower = intent.lower()
    for key, value in intent_mapping.items():
        if key in intent_lower:
            return value
    return None

if __name__ == "__main__":
    # 测试加载
    print("=" * 80)
    print("🧪 测试策略矩阵加载")
    print("=" * 80)
    
    strategies = load_strategy_matrix()
    
    if strategies:
        print(f"\n✅ 成功加载 {len(strategies)} 个Persona的策略")
        
        # 测试获取策略
        for persona in ['alpha', 'beta', 'delta', 'echo']:
            if persona in strategies:
                print(f"\n--- {persona.upper()} Persona ---")
                print(f"总体目标: {strategies[persona]['overall_target'][:100]}...")
                print(f"策略数量: {len(strategies[persona]['strategies'])}")
                
                # 测试获取特定意图的策略
                strategy = get_strategy_for_intent(persona, "Goal Setting and Planning")
                if strategy:
                    print(f"\nGoal Setting策略:")
                    print(f"  核心策略: {strategy['core_strategy'][:100]}...")
                    print(f"  DO项数: {len(strategy['do_list'])}")
                    print(f"  AVOID项数: {len(strategy['avoid_list'])}")
    else:
        print("\n❌ 策略矩阵加载失败")
