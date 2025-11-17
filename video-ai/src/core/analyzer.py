"""
内容分析模块

分析视频转录内容,提取关键信息、主题、情感等。
集成LLM进行深度分析和智能片段识别。
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
import json
import asyncio
import logging

# 导入LLM工厂
from .llm_factory import LLMFactory, LLMProvider

# 导入NLP处理器
try:
    from ..utils.nlp_processor import KeywordExtractor, TopicExtractor, SentimentAnalyzer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)


# ====== Prompt 模板 ======

TOPIC_EXTRACTION_PROMPT = """请从以下视频内容中提取主要主题。

内容摘要:
{content}

要求:
1. 提取5-10个主要主题
2. 每个主题提供简短描述
3. 列出每个主题的相关关键词

请以JSON格式返回:
{{
  "topics": [
    {{
      "title": "主题标题",
      "description": "简短描述(1-2句话)",
      "keywords": ["关键词1", "关键词2", "关键词3"],
      "relevance": 0.95
    }}
  ]
}}
"""

SEGMENT_IDENTIFICATION_PROMPT = """基于以下转录内容和用户兴趣,识别最相关的视频片段。

用户兴趣: {interests}
要跳过的主题: {skip_topics}

转录内容:
{transcript}

已识别的主题:
{topics}

要求:
1. 识别5-10个最相关的片段
2. 每个片段时长建议2-5分钟(120-300秒)
3. 片段之间应有逻辑连贯性
4. 评估每个片段的相关性分数(0-1)
5. 评估每个片段的重要性分数(0-1)
6. 确保片段不在句子中间切断

返回JSON格式:
{{
  "segments": [
    {{
      "start_time": 123.5,
      "end_time": 234.8,
      "topic": "主题名称",
      "relevance_score": 0.95,
      "importance_score": 0.88,
      "reason": "选择这个片段的理由",
      "keywords": ["关键词1", "关键词2"]
    }}
  ]
}}

注意:
- start_time 和 end_time 必须是数字(秒)
- 确保 start_time < end_time
- 如果某些主题不相关,可以省略
"""

SUMMARY_GENERATION_PROMPT = """请为以下视频转录生成简洁的摘要。

转录内容:
{transcript}

要求:
1. 摘要长度: 200-300字
2. 突出核心观点
3. 保持客观中立
4. 使用清晰易懂的语言

请直接返回摘要文本,不需要额外说明。
"""


@dataclass
class KeySegment:
    """关键片段"""
    start: float
    end: float
    text: str
    topic: str
    relevance_score: float  # 相关性评分 (0-1)
    importance_score: float  # 重要性评分 (0-1)
    keywords: List[str]
    reason: Optional[str] = None  # 选择理由


@dataclass
class AnalysisResult:
    """分析结果"""
    key_segments: List[KeySegment]
    main_topics: List[str]
    summary: str
    keywords: List[str]
    sentiment: str  # positive, negative, neutral


class ContentAnalyzer:
    """内容分析器"""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        api_provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_llm: bool = True
    ):
        """
        初始化内容分析器

        Args:
            llm_provider: LLM提供商实例(可选)
            api_provider: API提供商名称 ('openai', 'gemini', 'claude')
            api_key: API密钥
            model: 模型名称
            use_llm: 是否使用LLM进行深度分析
        """
        self.use_llm = use_llm
        self.llm_provider = llm_provider

        # 如果没有提供LLM实例但启用了LLM,则创建一个
        if self.use_llm and not self.llm_provider:
            if api_key:
                self.llm_provider = LLMFactory.create(
                    provider=api_provider,
                    api_key=api_key,
                    model=model
                )
                logger.info(f"使用 {api_provider} 进行LLM分析")
            else:
                logger.warning("未提供API密钥,将使用基础分析模式")
                self.use_llm = False

    def analyze(
        self,
        transcript,
        user_interests: Optional[List[str]] = None,
        skip_topics: Optional[List[str]] = None,
        max_segments: int = 10
    ) -> AnalysisResult:
        """
        分析转录内容

        Args:
            transcript: 转录对象
            user_interests: 用户兴趣列表
            skip_topics: 要跳过的主题列表
            max_segments: 最大返回片段数

        Returns:
            AnalysisResult对象
        """
        logger.info("开始分析视频内容...")

        if self.use_llm and self.llm_provider:
            # 使用LLM进行深度分析
            return asyncio.run(
                self._analyze_with_llm_async(
                    transcript,
                    user_interests,
                    skip_topics,
                    max_segments
                )
            )
        else:
            # 使用基础NLP分析
            return self._analyze_basic(
                transcript,
                user_interests,
                skip_topics,
                max_segments
            )

    def _analyze_basic(
        self,
        transcript,
        user_interests: Optional[List[str]],
        skip_topics: Optional[List[str]],
        max_segments: int
    ) -> AnalysisResult:
        """基础分析(不使用LLM)"""
        logger.info("使用基础NLP分析...")

        # 提取关键词
        if NLP_AVAILABLE:
            keywords_dict = KeywordExtractor.tfidf([transcript.full_text], top_n=20)
            keywords = list(keywords_dict.keys())

            # 识别主题
            topics_with_weight = TopicExtractor.identify_topics(
                transcript.full_text,
                num_topics=5
            )
            main_topics = [topic for topic, _ in topics_with_weight]

            # 分析情感
            sentiment, _ = SentimentAnalyzer.analyze(transcript.full_text)
        else:
            # 使用简单的关键词提取
            keywords = self._extract_keywords(transcript.full_text)
            main_topics = keywords[:5]
            sentiment = self._analyze_sentiment(transcript.full_text)

        # 生成摘要
        summary = self._generate_summary(transcript.full_text)

        # 识别关键片段
        key_segments = self._identify_key_segments(
            transcript.segments,
            user_interests,
            skip_topics,
            keywords,
            main_topics,
            max_segments
        )

        logger.info(f"分析完成！识别到 {len(key_segments)} 个关键片段")

        return AnalysisResult(
            key_segments=key_segments,
            main_topics=main_topics,
            summary=summary,
            keywords=keywords,
            sentiment=sentiment
        )

    async def _analyze_with_llm_async(
        self,
        transcript,
        user_interests: Optional[List[str]],
        skip_topics: Optional[List[str]],
        max_segments: int
    ) -> AnalysisResult:
        """使用LLM进行深度分析(异步)"""
        logger.info("使用LLM进行深度分析...")

        # 阶段1: 生成摘要和提取主题
        logger.info("阶段1: 生成摘要和提取主题...")

        # 并行执行摘要生成和主题提取
        summary_task = self._generate_summary_llm(transcript.full_text)
        topics_task = self._extract_topics_llm(transcript.full_text)

        summary, topics_data = await asyncio.gather(summary_task, topics_task)

        # 提取主题列表
        topics = topics_data.get('topics', [])
        main_topics = [topic['title'] for topic in topics]

        logger.info(f"识别到 {len(main_topics)} 个主题")

        # 阶段2: 识别关键片段
        logger.info("阶段2: 识别关键片段...")

        segments_data = await self._identify_segments_llm(
            transcript,
            topics,
            user_interests,
            skip_topics
        )

        # 解析片段数据
        key_segments = self._parse_segments(
            segments_data.get('segments', []),
            transcript.segments
        )

        # 限制片段数量
        key_segments = key_segments[:max_segments]

        # 提取关键词(从主题中)
        keywords = []
        for topic in topics:
            keywords.extend(topic.get('keywords', []))

        # 去重并限制数量
        keywords = list(dict.fromkeys(keywords))[:20]

        # 分析情感(使用NLP或基础方法)
        if NLP_AVAILABLE:
            sentiment, _ = SentimentAnalyzer.analyze(transcript.full_text)
        else:
            sentiment = self._analyze_sentiment(transcript.full_text)

        logger.info(f"分析完成！识别到 {len(key_segments)} 个关键片段")

        return AnalysisResult(
            key_segments=key_segments,
            main_topics=main_topics,
            summary=summary,
            keywords=keywords,
            sentiment=sentiment
        )

    async def _generate_summary_llm(self, text: str) -> str:
        """使用LLM生成摘要"""
        # 限制输入长度(避免超出token限制)
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length] + "..."

        prompt = SUMMARY_GENERATION_PROMPT.format(transcript=text)

        try:
            summary = await self.llm_provider.generate(prompt, max_tokens=512)
            return summary.strip()
        except Exception as e:
            logger.error(f"LLM摘要生成失败: {e}")
            return self._generate_summary(text)

    async def _extract_topics_llm(self, text: str) -> dict:
        """使用LLM提取主题"""
        # 限制输入长度
        max_length = 8000
        if len(text) > max_length:
            text = text[:max_length] + "..."

        prompt = TOPIC_EXTRACTION_PROMPT.format(content=text)

        schema = {
            "topics": [
                {
                    "title": "",
                    "description": "",
                    "keywords": [],
                    "relevance": 0.0
                }
            ]
        }

        try:
            result = await self.llm_provider.generate_json(prompt, schema)
            return result
        except Exception as e:
            logger.error(f"LLM主题提取失败: {e}")
            # 返回空结果
            return {"topics": []}

    async def _identify_segments_llm(
        self,
        transcript,
        topics: List[Dict],
        user_interests: Optional[List[str]],
        skip_topics: Optional[List[str]]
    ) -> dict:
        """使用LLM识别片段"""
        # 构建转录文本(包含时间戳)
        transcript_with_time = self._format_transcript_with_time(transcript.segments)

        # 限制长度
        max_length = 12000
        if len(transcript_with_time) > max_length:
            # 智能截断:保留开头、中间、结尾
            part_len = max_length // 3
            transcript_with_time = (
                transcript_with_time[:part_len] + "\n...\n" +
                transcript_with_time[len(transcript_with_time)//2 - part_len//2:
                                      len(transcript_with_time)//2 + part_len//2] + "\n...\n" +
                transcript_with_time[-part_len:]
            )

        # 格式化兴趣和跳过主题
        interests_str = ", ".join(user_interests) if user_interests else "无特定兴趣"
        skip_str = ", ".join(skip_topics) if skip_topics else "无"

        # 格式化主题
        topics_str = json.dumps(topics, indent=2, ensure_ascii=False)

        prompt = SEGMENT_IDENTIFICATION_PROMPT.format(
            interests=interests_str,
            skip_topics=skip_str,
            transcript=transcript_with_time,
            topics=topics_str
        )

        schema = {
            "segments": [
                {
                    "start_time": 0.0,
                    "end_time": 0.0,
                    "topic": "",
                    "relevance_score": 0.0,
                    "importance_score": 0.0,
                    "reason": "",
                    "keywords": []
                }
            ]
        }

        try:
            result = await self.llm_provider.generate_json(prompt, schema, max_tokens=2048)
            return result
        except Exception as e:
            logger.error(f"LLM片段识别失败: {e}")
            return {"segments": []}

    def _format_transcript_with_time(self, segments, max_segments: int = 100) -> str:
        """格式化转录文本(包含时间戳)"""
        lines = []

        # 如果片段太多,采样
        if len(segments) > max_segments:
            step = len(segments) // max_segments
            segments = segments[::step]

        for seg in segments:
            time_str = f"[{seg.start:.1f}s - {seg.end:.1f}s]"
            lines.append(f"{time_str} {seg.text}")

        return "\n".join(lines)

    def _parse_segments(
        self,
        segments_data: List[Dict],
        transcript_segments
    ) -> List[KeySegment]:
        """解析LLM返回的片段数据"""
        key_segments = []

        for seg_data in segments_data:
            try:
                start = float(seg_data.get('start_time', 0))
                end = float(seg_data.get('end_time', 0))

                # 验证时间有效性
                if start >= end or start < 0:
                    logger.warning(f"无效的时间范围: {start} - {end}")
                    continue

                # 找到对应的转录文本
                text = self._get_text_for_timerange(transcript_segments, start, end)

                segment = KeySegment(
                    start=start,
                    end=end,
                    text=text,
                    topic=seg_data.get('topic', ''),
                    relevance_score=float(seg_data.get('relevance_score', 0.5)),
                    importance_score=float(seg_data.get('importance_score', 0.5)),
                    keywords=seg_data.get('keywords', []),
                    reason=seg_data.get('reason')
                )

                key_segments.append(segment)

            except (ValueError, TypeError) as e:
                logger.warning(f"解析片段数据失败: {e}, 数据: {seg_data}")
                continue

        # 按综合评分排序
        key_segments.sort(
            key=lambda x: (x.relevance_score + x.importance_score) / 2,
            reverse=True
        )

        return key_segments

    def _get_text_for_timerange(self, segments, start: float, end: float) -> str:
        """获取时间范围内的转录文本"""
        texts = []

        for seg in segments:
            # 检查片段是否在时间范围内
            if seg.start >= end:
                break

            if seg.end <= start:
                continue

            texts.append(seg.text)

        return " ".join(texts)

    # ====== 基础分析方法 ======

    def _extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """提取关键词(简化版)"""
        words = re.findall(r'\b\w+\b', text.lower())

        # 停用词
        stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or'
        }

        filtered_words = [w for w in words if w not in stopwords and len(w) > 1]

        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 返回前N个高频词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]

    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成摘要(简化版)"""
        if len(text) <= max_length:
            return text

        return text[:max_length] + "..."

    def _analyze_sentiment(self, text: str) -> str:
        """分析情感(简化版)"""
        positive_words = {'好', '优秀', '棒', '喜欢', '成功', 'good', 'great', 'excellent'}
        negative_words = {'差', '糟糕', '失败', '问题', 'bad', 'poor', 'terrible'}

        text_lower = text.lower()

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def _identify_key_segments(
        self,
        segments,
        user_interests: Optional[List[str]],
        skip_topics: Optional[List[str]],
        keywords: List[str],
        topics: List[str],
        max_segments: int
    ) -> List[KeySegment]:
        """识别关键片段(基础版)"""
        key_segments = []

        for segment in segments:
            # 检查是否包含要跳过的主题
            if skip_topics:
                should_skip = any(
                    skip_topic.lower() in segment.text.lower()
                    for skip_topic in skip_topics
                )
                if should_skip:
                    continue

            # 计算相关性评分
            relevance_score = self._calculate_relevance(
                segment.text,
                user_interests,
                keywords
            )

            # 计算重要性评分
            importance_score = self._calculate_importance(
                segment.text,
                keywords,
                topics
            )

            # 提取片段关键词
            segment_keywords = [
                kw for kw in keywords
                if kw in segment.text.lower()
            ]

            # 确定片段主题
            segment_topic = self._determine_segment_topic(
                segment.text,
                topics
            )

            # 综合评分
            overall_score = (relevance_score + importance_score) / 2

            if overall_score > 0.3:  # 阈值
                key_segments.append(KeySegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    topic=segment_topic,
                    relevance_score=relevance_score,
                    importance_score=importance_score,
                    keywords=segment_keywords
                ))

        # 按综合评分排序
        key_segments.sort(
            key=lambda x: (x.relevance_score + x.importance_score) / 2,
            reverse=True
        )

        return key_segments[:max_segments]

    def _calculate_relevance(
        self,
        text: str,
        user_interests: Optional[List[str]],
        keywords: List[str]
    ) -> float:
        """计算相关性评分"""
        if not user_interests:
            return 0.5  # 默认评分

        text_lower = text.lower()
        matches = sum(
            1 for interest in user_interests
            if interest.lower() in text_lower
        )

        # 标准化到 0-1
        return min(matches / len(user_interests), 1.0)

    def _calculate_importance(
        self,
        text: str,
        keywords: List[str],
        topics: List[str]
    ) -> float:
        """计算重要性评分"""
        text_lower = text.lower()

        # 关键词密度
        keyword_count = sum(1 for kw in keywords if kw in text_lower)
        keyword_density = keyword_count / max(len(keywords), 1)

        # 主题相关性
        topic_count = sum(1 for topic in topics if topic in text_lower)
        topic_relevance = topic_count / max(len(topics), 1)

        # 文本长度(更长的片段可能更重要)
        length_score = min(len(text) / 500, 1.0)

        # 综合评分
        importance = (keyword_density * 0.4 +
                     topic_relevance * 0.4 +
                     length_score * 0.2)

        return min(importance, 1.0)

    def _determine_segment_topic(self, text: str, topics: List[str]) -> str:
        """确定片段主题"""
        text_lower = text.lower()

        for topic in topics:
            if topic in text_lower:
                return topic

        return "其他"


if __name__ == "__main__":
    # 测试代码
    print("ContentAnalyzer 模块已加载")
    print("支持 LLM 深度分析和基础 NLP 分析")
