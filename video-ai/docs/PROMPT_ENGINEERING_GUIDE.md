# Prompt 工程指南：AI Video Summarizer 分析与应用

## 1. ai-video-summarizer 中的 Prompt 策略分析

### 1.1 Prompt 分层结构

该项目使用 **三层 Prompt 设计**，每层专注于特定任务：

```
层级 1: 总结生成 Prompt
  └─ 输入: 完整转录文本
  └─ 输出: 结构化总结内容
  └─ 特点: 根据目标类型定制

层级 2: 主题提取 Prompt
  └─ 输入: 生成的总结
  └─ 输出: JSON 格式的主题列表
  └─ 特点: 强制结构化输出

层级 3: 片段识别 Prompt
  └─ 输入: 转录文本 + 提取的主题
  └─ 输出: 带时间戳的片段列表
  └─ 特点: 涉及复杂推理
```

### 1.2 Prompt 设计原则

#### 原则 1: 清晰的指令结构

```python
# 不好的 Prompt
"从这个转录中提取主题"

# 好的 Prompt
"""
任务：从以下转录中提取主要讨论的主题

输入：[转录内容]

输出格式：JSON 数组，每个主题包含：
- title (字符串): 主题的描述性标题
- description (字符串): 一句话描述
- keywords (数组): 相关关键词列表

约束条件：
- 最多 10 个主题
- 按重要性排序
- 避免重复

示例：
{
  "topics": [
    {
      "title": "项目背景",
      "description": "讨论项目的历史背景和启动原因",
      "keywords": ["背景", "原因", "启动"]
    }
  ]
}

现在，请处理以下转录：
[转录内容]
"""
```

#### 原则 2: 上下文明确化

```python
# 更好的 Prompt 包含：
1. 角色定义
2. 任务说明
3. 约束条件
4. 输出格式
5. 示例
6. 实际输入

PROMPT = """
角色：你是一名专业的视频内容分析师

任务：分析以下会议转录，提取关键决策和行动项

会议背景：{context}

转录：
{transcript}

要求：
1. 列出所有主要决策
2. 为每个决策指定负责人
3. 列出所有行动项及截止日期
4. 按优先级排序

输出格式：
{{
  "decisions": [
    {{
      "id": "D001",
      "description": "...",
      "owner": "...",
      "date": "YYYY-MM-DD"
    }}
  ],
  "action_items": [
    {{
      "id": "A001",
      "description": "...",
      "owner": "...",
      "deadline": "YYYY-MM-DD",
      "priority": "high|medium|low"
    }}
  ]
}}

转录内容：
{transcript}
"""
```

#### 原则 3: 容错设计

```python
# 设计可容错的 Prompt
PROMPT = """
...

重要：如果你无法以 JSON 格式返回，请使用自然语言，
我们有备用解析器处理。

始终返回完整的响应，即使不确定也要提供最佳估计。
"""

# 在代码中实现容错
def parse_response(response: str, schema: Dict) -> Dict:
    # 尝试 JSON 解析
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback: 使用正则或其他方法解析
        return parse_with_regex(response, schema)
```

---

## 2. ai-video-summarizer 使用的具体 Prompts

### 2.1 会议纪要 Prompt

```python
MEETING_MINUTES_PROMPT = """
你是一名专业的会议记录员。请从以下转录中生成专业的会议纪要。

转录：
{transcript}

会议纪要应包括：
1. **参与者**: 提及的所有人名和角色
2. **讨论要点**: 主要讨论的话题和观点
3. **关键决策**: 会议中做出的所有决策
4. **行动项**: 后续需要完成的任务，包括所有者和截止日期
5. **后续步骤**: 会议后需要采取的行动或后续会议

格式要求：
- 使用清晰的标题和项目符号
- 每个决策和行动项应简洁明了
- 包含所有提到的具体数字、日期和名称

请现在生成会议纪要：
"""
```

### 2.2 播客摘要 Prompt

```python
PODCAST_SUMMARY_PROMPT = """
你是一名热情的播客粉丝和内容总结专家。

请从以下播客转录中创建一份引人入胜的摘要。

转录：
{transcript}

摘要应包括：
1. **剧集概述**: 一句话总结这集内容
2. **嘉宾信息**: 提及的所有嘉宾，及其背景/专长
3. **主要话题**: 讨论的 3-5 个核心话题，每个 1-2 句话
4. **核心洞见**: 最有价值的 3 个观点或发现
5. **金句**: 最令人印象深刻的 2-3 个引言
6. **推荐资源**: 嘉宾提到的任何资源、工具或书籍
7. **学习要点**: 听众可以立即应用的 3 个实用建议

格式要求：
- 语言要动态和引人入胜
- 使用编号或项目符号便于阅读
- 包括相关的时间戳（如果可用）

请现在创建播客摘要：
"""
```

### 2.3 讲座笔记 Prompt

```python
LECTURE_NOTES_PROMPT = """
你是一名学术笔记专家，擅长从讲座中提取知识。

请从以下讲座转录中创建全面的讲座笔记。

转录：
{transcript}

讲座笔记应包括：
1. **课程标题和讲师**: 课程名称和讲师信息
2. **学习目标**: 讲座目的和预期学习成果（如果提到）
3. **关键概念**: 
   - 定义所有关键术语
   - 解释核心概念和原理
   - 突出新的或难以理解的概念
4. **示例和案例研究**: 讲座中提供的具体示例
5. **公式和数学**: 使用 LaTeX 格式的所有方程和公式
6. **图表描述**: 讲座中使用的任何图表或视觉辅助工具的描述
7. **复习题**: 3-5 个帮助学生自测理解的问题
8. **进一步阅读**: 推荐的教材或参考资源

格式要求：
- 使用清晰的层级和子标题
- 数学表达式使用标准符号
- 包括任何提到的统计数据或研究发现

请现在创建详细的讲座笔记：
"""
```

### 2.4 采访亮点 Prompt

```python
INTERVIEW_HIGHLIGHTS_PROMPT = """
你是一名采访分析师，专门提取采访中的核心内容。

从以下采访转录中提取亮点内容。

转录：
{transcript}

采访亮点应包括：
1. **受访者背景**: 名字、职位、组织、专业领域
2. **职业历程**: 受访者的关键职业里程碑和成就
3. **核心观点**: 
   - 受访者关于其领域的主要观点（3-5 个）
   - 每个观点的简要解释
4. **个人故事**: 受访者分享的有趣或启发性的故事
5. **成功经验**: 受访者分享的成功案例或教训
6. **建议和建议**: 受访者给予观众或追随者的建议
7. **有趣事实**: 受访者透露的有趣或意外的信息
8. **联系信息**: 如果提供，受访者的社交媒体或网站链接

格式要求：
- 包含直接引用（用引号标注）
- 使用吸引人的语言
- 突出最有见地的评论

请现在提取采访亮点：
"""
```

### 2.5 主题提取 Prompt

```python
TOPIC_EXTRACTION_PROMPT = """
你的任务是从提供的内容中识别和提取主要主题。

内容：
{content}

请识别所有主要主题或讨论的段落。

对于每个主题，提供：
- title: 主题的清晰、描述性的标题
- description: 一句话总结这个主题讨论了什么
- keywords: 与该主题相关的 3-5 个关键词

响应必须是有效的 JSON 格式：
{{
  "topics": [
    {{
      "title": "主题标题",
      "description": "这个主题讨论了...",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
  ]
}}

重要约束：
- 最多提取 15 个主题
- 按在内容中出现的顺序列出
- 每个主题应该是独特的，避免重复
- 确保 JSON 格式有效

现在分析以下内容并提取主题：
"""
```

### 2.6 时间段识别 Prompt（最复杂）

```python
CLIP_SEGMENT_PROMPT = """
你的任务是在转录中找到与特定主题相对应的时间段。

这是关键任务：你需要将识别的主题映射到转录中的具体时间段。

转录（带时间戳）：
{transcript}

要提取的主题：
{topics}

对于每个主题，找到转录中讨论该主题的时间范围。

约束条件：
1. 时间范围：
   - 最少 120 秒（2 分钟）
   - 最多 300 秒（5 分钟）
   - 优先选择完整的讨论

2. 边界规则：
   - 从讨论主题的第一个完整句子开始
   - 延续到最后一个与主题相关的句子
   - 不要在句子中间切割
   - 宁可包含略多的内容也不要剪掉关键信息

3. 质量标准：
   - 每个片段应自成一体、易于理解
   - 避免有歧义的开头或结尾
   - 确保音频/视频连贯

返回 JSON 格式：
{{
  "clips": [
    {{
      "topic": "主题名称",
      "start": <起始秒数作为数字>,
      "end": <结束秒数作为数字>,
      "confidence": <0-1 的置信度>,
      "reason": "为什么选择这个时间范围的简要说明"
    }}
  ]
}}

示例：
{{
  "clips": [
    {{
      "topic": "项目启动背景",
      "start": 45.5,
      "end": 187.3,
      "confidence": 0.95,
      "reason": "从张三介绍项目背景开始，到他总结初衷时结束"
    }}
  ]
}}

重要提示：
- 一些主题可能没有在转录中找到（返回空对象）
- 对于模棱两可的情况，选择较长的时间段
- 在 JSON 块前后不包含任何额外文本
- 确保所有时间戳都有效（start < end）

现在分析转录并识别片段：
"""
```

---

## 3. Prompt 优化技巧

### 3.1 Few-Shot Prompting（少样本提示）

```python
PROMPT_WITH_EXAMPLES = """
从文本中提取关键信息的任务。

示例 1：
输入：
"我们在 2024 年 1 月 15 日召开了产品发布会。参加者包括张三（CEO）、
李四（产品经理）和王五（开发负责人）。我们讨论了新功能的发布时间表，
决定在 3 月份推出第一版本。李四负责市场营销计划。"

输出：
{
  "date": "2024-01-15",
  "attendees": ["张三 (CEO)", "李四 (产品经理)", "王五 (开发负责人)"],
  "decisions": [
    {
      "description": "第一版本在 3 月份推出",
      "owner": "不明确"
    }
  ],
  "action_items": [
    {
      "description": "制定市场营销计划",
      "owner": "李四"
    }
  ]
}

示例 2：
输入：
"在今天的会议上，我们讨论了技术债务问题。开发主管提议
在下个季度分配 30% 的资源来解决技术债。所有人都同意这个计划。
李四将领导这个计划，截止日期是 Q2 末。"

输出：
{
  "date": "今天（需要从上下文推断）",
  "attendees": [],
  "decisions": [
    {
      "description": "在下个季度分配 30% 的资源解决技术债",
      "owner": "团队"
    }
  ],
  "action_items": [
    {
      "description": "领导技术债债务解决计划",
      "owner": "李四",
      "deadline": "Q2 末"
    }
  ]
}

现在，请按照上述格式分析以下转录：
{transcript}
"""
```

### 3.2 Chain-of-Thought Prompting（思维链）

```python
COT_PROMPT = """
请按照以下步骤分析转录：

步骤 1：识别所有参与者和他们的角色
- 列出所有提到的人名
- 识别他们在讨论中的角色或职位

步骤 2：提取主要讨论话题
- 识别转录中讨论的主要主题
- 记录每个主题出现的大概时间段

步骤 3：识别决策
- 找出所有明确或隐含的决策
- 记录谁做出了决策或谁负责实施

步骤 4：识别行动项
- 列出所有需要完成的任务
- 识别每项任务的负责人和截止日期

步骤 5：总结和验证
- 确保没有遗漏重要信息
- 检查时间戳的准确性

转录：
{transcript}

现在，请按照这 5 个步骤分析上述转录，
最后以 JSON 格式输出结果。
"""
```

### 3.3 提示工程最佳实践

```python
# 1. 明确指定输出格式
GOOD = """
返回 JSON 格式，结构如下：
{
  "key1": "类型: 字符串",
  "key2": ["类型: 数组, 元素: 字符串"],
  "key3": {
    "nested_key": "类型: 字符串"
  }
}
"""

# 2. 包括温度参数指导
PROMPT_WITH_TEMP = """
这个任务需要创意和多样性，使用 temperature=0.8

这个任务需要精确和一致，使用 temperature=0.0
"""

# 3. 指定长度约束
WITH_LENGTH = """
摘要应该是：
- 最少：200 字
- 最多：500 字
- 避免超出这个范围
"""

# 4. 添加上下文约束
WITH_CONTEXT = """
重点关注：
1. 与 AI 相关的技术决策
2. 预算分配讨论
3. 团队协作安排

忽略：
1. 闲聊和个人话题
2. 重复的观点
3. 明显的离题讨论
"""

# 5. 指定失败恢复
WITH_FALLBACK = """
如果无法生成完全准确的 JSON：
1. 保留尽可能多的有效数据
2. 使用 null 表示缺失值
3. 在注释中说明遇到的问题

示例失败输出：
{
  "topics": [
    {
      "title": "清晰的主题",
      "description": "有描述",
      "keywords": null  // 无法从转录中提取
    }
  ],
  "parsing_note": "主题 2 被跳过，因为不清晰"
}
"""
```

---

## 4. 针对 video-ai 项目的 Prompt 改进建议

### 4.1 多语言支持 Prompt

```python
MULTILINGUAL_PROMPT = """
你现在是一个多语言内容分析师。

首先，检测以下转录的语言。
然后，用检测到的语言执行任务。

检测到的语言：[通过 API 检测]

转录（{detected_language}）：
{transcript}

任务：提取关键主题并生成总结

重要：
- 响应必须与原始转录使用相同的语言
- 保留原始语言中的专业术语和缩写
- 如果有英文专业术语，保留英文版本

JSON 响应：
...
"""
```

### 4.2 专业领域特定 Prompt

```python
DOMAIN_SPECIFIC_PROMPTS = {
    "medical": """
你现在充当医学转录分析师。
关注医学术语、诊断、治疗方案和患者信息。
遵守 HIPAA 隐私要求。
""",
    
    "legal": """
你现在充当法律文件分析师。
关注法律条款、合同义务、风险和建议。
使用法律术语的标准解释。
""",
    
    "technical": """
你现在充当技术讨论分析师。
关注技术决策、架构讨论和实现细节。
准确记录技术术语和规范。
""",
    
    "business": """
你现在充当商业分析师。
关注战略、财务影响、市场机会和竞争分析。
强调商业价值和 KPI。
"""
}
```

### 4.3 实时反馈和迭代 Prompt

```python
ITERATIVE_PROMPT = """
这是一个两步骤的处理流程。

步骤 1（初始分析）：
- 进行初步分析
- 标记任何不确定的部分
- 返回初始结果和置信度评分

步骤 2（精化）：
根据用户的反馈进行精化：
- 如果有任何不确定性，明确说明
- 提供多个解释选项，如果存在歧义
- 请求澄清以改进准确性

初始输入：
{transcript}

初始分析：
[执行分析]

等待用户反馈...

如果用户提供反馈：
[根据反馈进行精化]
"""
```

---

## 5. Prompt 测试和验证

```python
# 测试框架
class PromptTester:
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def test_prompt(
        self,
        prompt: str,
        test_cases: List[Dict],
        expected_schema: Dict = None
    ) -> Dict:
        """测试 prompt 的有效性"""
        results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "failures": []
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                # 替换测试数据
                filled_prompt = prompt.format(**test_case["input"])
                
                # 获取响应
                response = self.llm.generate_text(filled_prompt)
                
                # 验证响应
                if expected_schema:
                    parsed = json.loads(response)
                    self._validate_schema(parsed, expected_schema)
                
                # 检查预期输出
                if not self._check_expected(response, test_case.get("expected")):
                    results["failed"] += 1
                    results["failures"].append({
                        "test": i,
                        "reason": "输出不符合预期"
                    })
                else:
                    results["passed"] += 1
            
            except Exception as e:
                results["failed"] += 1
                results["failures"].append({
                    "test": i,
                    "reason": str(e)
                })
        
        return results

# 使用示例
tester = PromptTester(llm_provider)
results = tester.test_prompt(
    TOPIC_EXTRACTION_PROMPT,
    test_cases=[
        {
            "input": {"content": "测试内容 1"},
            "expected": ["预期主题 1", "预期主题 2"]
        },
        {
            "input": {"content": "测试内容 2"},
            "expected": ["预期主题 A"]
        }
    ],
    expected_schema={"topics": [{"title": "", "keywords": []}]}
)

print(f"通过: {results['passed']}/{results['total']}")
if results['failures']:
    for failure in results['failures']:
        print(f"  失败 {failure['test']}: {failure['reason']}")
```

---

## 6. 常见 Prompt 问题和解决方案

| 问题 | 表现 | 解决方案 |
|------|------|--------|
| 格式不一致 | 有时返回 JSON，有时不返回 | 添加明确的格式示例和约束 |
| 幻觉 | 编造不存在的信息 | 添加"如果不确定，说'未知'" |
| 过度简化 | 遗漏细节 | 要求更详细的解释和例子 |
| 长度问题 | 输出太长或太短 | 明确指定字数范围和要点数 |
| 语言混杂 | 混合多种语言 | 明确指定输出语言 |
| JSON 错误 | 返回无效的 JSON | 包含有效的 JSON 示例 |

---

## 总结

有效的 Prompt 工程是开发高质量 AI 视频处理系统的关键。关键要点：

1. **结构化设计**: 使用分层、明确的指令
2. **示例驱动**: 包含 few-shot 示例
3. **容错设计**: 考虑失败情况并提供备选方案
4. **迭代改进**: 根据实际结果不断优化
5. **域特定优化**: 针对不同领域调整 prompt
6. **测试验证**: 有系统的测试方法

