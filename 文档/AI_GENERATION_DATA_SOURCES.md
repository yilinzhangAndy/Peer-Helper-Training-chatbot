# 🤖 AI 生成使用的数据来源说明

## 📊 数据使用概览

### ✅ 是的，API 生成确实使用了你提供的很多数据！

系统在生成学生回复时使用了多个数据源，确保回复符合 persona 特征并基于真实对话数据。

## 🎯 开场问题生成（Opening Message）

### 使用的数据源：

#### 1. ✅ Persona 特征（来自 `STUDENT_PERSONAS`）
```python
- Description: "Moderately below average self-efficacy..."
- Traits: ["Works hard", "Average confidence", "Willing to ask questions", ...]
- Help-seeking behavior: "Well above average; not worried about asking for help."
```

#### 2. ✅ 知识库检索（RAG）
- 从 `knowledge_base` 搜索 "MAE advising student opening prompt"
- 返回相关的 MAE 专业知识和建议

#### 3. ❌ Few-Shot 真实对话数据
- **不使用**（因为 `use_few_shot=False`）
- 开场问题只基于 persona 特征和知识库生成

### 生成流程：
```
1. 获取 persona 特征（description, traits, help_seeking）
   ↓
2. 从知识库检索相关知识
   ↓
3. 构建 prompt（包含 persona 特征 + 知识库内容）
   ↓
4. 调用 UF LiteLLM API 生成开场问题
```

## 💬 后续对话生成（Student Replies）

### 使用的数据源：

#### 1. ✅ Persona 特征（完整信息）
```python
- Description: 完整的 persona 描述
- Traits: 所有特征列表
- Help-seeking behavior: 帮助寻求行为
- Language style guide: 特定 persona 的语言风格指导
```

#### 2. ✅ 真实对话数据（Few-Shot Learning）
- **1387 条真实对话**（来自 `data/peer_dataset_26.xlsm`）
- **PDF 提取的对话**（来自 `data/extracted_pdf_content.json`）
- 系统会从这些数据中选择 2 个最相关的示例

#### 3. ✅ 知识库检索（RAG）
- 根据 advisor 消息检索相关的 MAE 专业知识
- 提供上下文信息

#### 4. ✅ 策略矩阵（Strategy Matrix）
- 根据 persona 和 intent 选择对应的策略
- 包含 Core Strategy、DO 列表、AVOID 列表

#### 5. ✅ 对话历史
- 智能选择最相关的历史消息（最多 6 条）
- 保持对话连贯性

### 生成流程：
```
1. 获取 persona 特征
   ↓
2. 从 1387 条真实对话中选择 Few-Shot 示例（2个）
   ↓
3. 从知识库检索相关知识
   ↓
4. 从策略矩阵获取策略指导
   ↓
5. 选择相关的对话历史
   ↓
6. 构建完整的 prompt（包含所有上述信息）
   ↓
7. 调用 UF LiteLLM API 生成学生回复
```

## 📋 详细数据使用说明

### 1. Persona 特征数据

**来源**: `STUDENT_PERSONAS` 字典（在 `web_app_cloud_simple.py` 中定义）

**每个 Persona 包含**:
- Description: 详细描述
- Traits: 特征列表（5-6 个）
- Help-seeking behavior: 帮助寻求行为描述
- Opening questions: 开场问题列表（8-9 个）

**在 Prompt 中的使用**:
```
Persona Characteristics:
- Description: {description}
- Traits: {traits}
- Help Seeking: {help_seeking_behavior}
```

### 2. 真实对话数据（Few-Shot）

**来源**: 
- `data/peer_dataset_26.xlsm` - **1387 条真实对话** ✅
- `data/extracted_pdf_content.json` - PDF 提取的对话 ✅

**选择机制**:
1. 根据 persona 过滤（只选择匹配的 persona）
2. 根据 intent 过滤（如果指定了 intent）
3. 根据相似度排序（使用序列相似度 + 关键词匹配）
4. 选择最相关的 2 个示例

**在 Prompt 中的使用**:
```
Here are some examples of similar conversations:

Example 1:
Advisor: {advisor_message}
Student (ALPHA): {student_reply}
Intent: {intent}

Example 2:
...
```

### 3. 知识库（RAG）

**来源**: `knowledge_base/` 目录
- `training_knowledge.json` - 训练知识
- `faq_knowledge.json` - FAQ 知识
- `scenario_knowledge.json` - 场景知识

**检索机制**:
- 根据 advisor 消息进行关键词搜索
- 返回最相关的文档（最多 5 条）

**在 Prompt 中的使用**:
```
Based on the following MAE professional knowledge:
{knowledge_context}
```

### 4. 策略矩阵（Strategy Matrix）

**来源**: `data/12_4 Peer Mentors Strategy Matrix.xlsx`

**内容**:
- 每个 Persona × Intent 组合对应一个策略
- 包含 Core Strategy、DO 列表、AVOID 列表、示例

**在 Prompt 中的使用**:
```
ADVISOR STRATEGY CONTEXT:
Core Strategy: {core_strategy}
Key things the advisor is trying to DO:
• {do_item_1}
• {do_item_2}
...
```

### 5. 对话历史

**来源**: `st.session_state.messages`

**选择机制**:
- 智能选择最相关的历史消息（最多 6 条）
- 考虑消息的相关性和重要性

**在 Prompt 中的使用**:
```
Previous conversation:
{conversation_context}

Now, the peer advisor just said:
"{current_message}"
```

## 🎯 数据使用对比

| 数据类型 | 开场问题 | 后续对话 |
|---------|---------|---------|
| **Persona 特征** | ✅ 使用 | ✅ 使用 |
| **知识库（RAG）** | ✅ 使用 | ✅ 使用 |
| **真实对话（Few-Shot）** | ❌ 不使用 | ✅ 使用（1387条） |
| **策略矩阵** | ❌ 不使用 | ✅ 使用 |
| **对话历史** | ❌ 不使用 | ✅ 使用 |

## 📊 完整 Prompt 结构（后续对话）

```
1. Persona Characteristics
   - Description
   - Traits
   - Help Seeking Behavior

2. Persona Language Style Guide
   - 特定 persona 的语言风格指导

3. Advisor Strategy Context（如果可用）
   - Core Strategy
   - DO 列表
   - AVOID 列表

4. Few-Shot Examples（2个真实对话示例）
   - Example 1: Advisor → Student
   - Example 2: Advisor → Student

5. Previous Conversation（如果存在）
   - 最相关的历史消息

6. Current Advisor Message
   - 当前 advisor 的消息

7. Critical Instructions
   - 回答规则
   - Persona 一致性要求
   - 长度要求
```

## ✅ 总结

### 开场问题生成：
- ✅ 使用 **Persona 特征**
- ✅ 使用 **知识库检索**
- ❌ **不使用** Few-Shot 真实对话数据

### 后续对话生成：
- ✅ 使用 **Persona 特征**
- ✅ 使用 **知识库检索**
- ✅ 使用 **1387 条真实对话**（Few-Shot Learning）
- ✅ 使用 **策略矩阵**
- ✅ 使用 **对话历史**

**所以，是的！API 生成确实使用了你提供的很多数据，特别是：**
1. **1387 条真实对话数据** - 用于 Few-Shot Learning
2. **Persona 特征数据** - 确保回复符合 persona 特征
3. **知识库数据** - 提供专业背景
4. **策略矩阵数据** - 指导对话策略

这些数据共同确保生成的学生回复既符合 persona 特征，又基于真实对话模式！
