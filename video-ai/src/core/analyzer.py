"""
内容分析模块

分析视频转录内容，提取关键信息、主题、情感等。
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


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
        api_provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化内容分析器

        Args:
            api_provider: API提供商 ('openai', 'gemini')
            api_key: API密钥
            model: 模型名称
        """
        self.api_provider = api_provider
        self.api_key = api_key

        if api_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("请安装 openai: pip install openai")
            self.model = model or "gpt-4-turbo-preview"
            if api_key:
                openai.api_key = api_key

        elif api_provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("请安装 google-generativeai: pip install google-generativeai")
            self.model = model or "gemini-pro"
            if api_key:
                genai.configure(api_key=api_key)

    def analyze(
        self,
        transcript,
        user_interests: Optional[List[str]] = None,
        max_segments: int = 10
    ) -> AnalysisResult:
        """
        分析转录内容

        Args:
            transcript: 转录对象
            user_interests: 用户兴趣列表
            max_segments: 最大返回片段数

        Returns:
            AnalysisResult对象
        """
        print("开始分析视频内容...")

        # 提取关键词
        keywords = self._extract_keywords(transcript.full_text)

        # 识别主题
        main_topics = self._identify_topics(transcript.full_text, keywords)

        # 生成摘要
        summary = self._generate_summary(transcript.full_text)

        # 分析情感
        sentiment = self._analyze_sentiment(transcript.full_text)

        # 识别关键片段
        key_segments = self._identify_key_segments(
            transcript.segments,
            user_interests,
            keywords,
            main_topics,
            max_segments
        )

        print(f"分析完成！识别到 {len(key_segments)} 个关键片段")

        return AnalysisResult(
            key_segments=key_segments,
            main_topics=main_topics,
            summary=summary,
            keywords=keywords,
            sentiment=sentiment
        )

    def _extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """提取关键词（简化版，实际应使用TF-IDF或TextRank）"""
        # 简单实现：基于词频
        # TODO: 使用更高级的算法如 TF-IDF, TextRank
        words = re.findall(r'\b\w+\b', text.lower())

        # 过滤停用词（简化版）
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

    def _identify_topics(
        self,
        text: str,
        keywords: List[str],
        num_topics: int = 5
    ) -> List[str]:
        """识别主题（简化版）"""
        # TODO: 使用LDA或NMF进行主题建模
        # 这里返回关键词作为主题（简化实现）
        return keywords[:num_topics]

    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成摘要"""
        # 简化实现：返回前N个字符
        # TODO: 使用LLM生成更智能的摘要
        if len(text) <= max_length:
            return text

        return text[:max_length] + "..."

    def _analyze_sentiment(self, text: str) -> str:
        """分析情感"""
        # 简化实现：基于关键词
        # TODO: 使用情感分析模型
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
        keywords: List[str],
        topics: List[str],
        max_segments: int
    ) -> List[KeySegment]:
        """识别关键片段"""
        key_segments = []

        for segment in segments:
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

        # 文本长度（更长的片段可能更重要）
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

    def analyze_with_llm(
        self,
        transcript,
        user_interests: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        使用LLM进行深度分析（阶段二功能）

        Args:
            transcript: 转录对象
            user_interests: 用户兴趣列表

        Returns:
            AnalysisResult对象
        """
        # TODO: 实现基于LLM的深度分析
        print("使用LLM进行深度分析...")

        prompt = self._build_analysis_prompt(
            transcript.full_text,
            user_interests
        )

        if self.api_provider == "openai":
            result = self._analyze_with_openai(prompt)
        elif self.api_provider == "gemini":
            result = self._analyze_with_gemini(prompt)
        else:
            raise ValueError(f"不支持的API提供商: {self.api_provider}")

        # 解析LLM返回结果并构建AnalysisResult
        # TODO: 实现结果解析逻辑

        return result

    def _build_analysis_prompt(
        self,
        text: str,
        user_interests: Optional[List[str]]
    ) -> str:
        """构建分析提示词"""
        interest_text = ""
        if user_interests:
            interest_text = f"\n用户关注的话题: {', '.join(user_interests)}"

        prompt = f"""请分析以下视频转录内容，提取关键信息：
{interest_text}

转录内容:
{text[:3000]}...

请提供：
1. 主要主题（5个）
2. 关键片段（10个，包括时间范围和原因）
3. 内容摘要（200字以内）
4. 关键词（20个）
5. 整体情感倾向

请以JSON格式返回结果。
"""
        return prompt

    def _analyze_with_openai(self, prompt: str) -> str:
        """使用OpenAI进行分析"""
        # TODO: 实现OpenAI API调用
        raise NotImplementedError("OpenAI分析功能待实现")

    def _analyze_with_gemini(self, prompt: str) -> str:
        """使用Gemini进行分析"""
        # TODO: 实现Gemini API调用
        raise NotImplementedError("Gemini分析功能待实现")


if __name__ == "__main__":
    # 测试代码
    analyzer = ContentAnalyzer(api_provider="openai")
    print("ContentAnalyzer 模块已加载")
