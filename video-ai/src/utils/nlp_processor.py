"""
NLP文本处理模块

处理转录文本的关键词提取、主题识别、情感分析
"""

from typing import List, Dict, Tuple, Set
from collections import Counter
import re
import math

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


class TextPreprocessor:
    """文本预处理器"""

    # 中文停用词
    CHINESE_STOPWORDS = {
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '他', '她', '它', '们', '你', '我们', '他们', '这', '那',
        '什么', '哪', '怎样', '为什么', '多少', '几', '如何', '着',
        '呢', '啊', '吗', '吧', '嗯', '哦', '哎', '唉', '啦'
    }

    # 英文停用词
    ENGLISH_STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'
    }

    @staticmethod
    def clean_text(text: str) -> str:
        """清洁文本"""
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # 移除邮箱
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)

        # 移除特殊符号，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fff\w\s\.\,\!\?\:\;\-\(\)\[\]\《\》\【\】]', '', text)

        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def tokenize(text: str, language: str = 'zh') -> List[str]:
        """分词"""
        text = TextPreprocessor.clean_text(text)

        if language == 'zh' or language == 'zh-CN':
            if JIEBA_AVAILABLE:
                tokens = list(jieba.cut(text))
            else:
                # 简单的字符级分词
                tokens = list(text.replace(' ', ''))
        else:
            # 英文分词：基于空格和标点
            tokens = re.findall(r'\b\w+\b', text.lower())

        return tokens

    @staticmethod
    def remove_stopwords(tokens: List[str], language: str = 'zh') -> List[str]:
        """移除停用词"""
        if language == 'zh' or language == 'zh-CN':
            stopwords = TextPreprocessor.CHINESE_STOPWORDS
        else:
            stopwords = TextPreprocessor.ENGLISH_STOPWORDS

        filtered = [token for token in tokens if token not in stopwords and len(token) > 1]
        return filtered


class KeywordExtractor:
    """关键词提取器"""

    @staticmethod
    def tfidf(documents: List[str], top_n: int = 20, language: str = 'zh') -> Dict[str, float]:
        """
        TF-IDF关键词提取

        Args:
            documents: 文档列表
            top_n: 返回的关键词数量
            language: 语言

        Returns:
            关键词-权重字典
        """
        # 分词和预处理
        tokenized_docs = []
        for doc in documents:
            tokens = TextPreprocessor.tokenize(doc, language)
            tokens = TextPreprocessor.remove_stopwords(tokens, language)
            tokenized_docs.append(tokens)

        # 计算IDF
        idf = {}
        doc_count = len(tokenized_docs)

        for tokens in tokenized_docs:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                if token not in idf:
                    idf[token] = 0
                idf[token] += 1

        # IDF = log(总文档数 / 包含该词的文档数)
        for token in idf:
            idf[token] = math.log(doc_count / idf[token])

        # 合并所有文档并计算TF-IDF
        all_tokens = []
        for tokens in tokenized_docs:
            all_tokens.extend(tokens)

        # 计算TF（简化版：直接用词频）
        token_freq = Counter(all_tokens)
        total_tokens = len(all_tokens)

        tfidf_scores = {}
        for token, freq in token_freq.items():
            tf = freq / total_tokens
            idf_score = idf.get(token, 1.0)
            tfidf_scores[token] = tf * idf_score

        # 排序并返回Top-N
        sorted_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_keywords[:top_n])

    @staticmethod
    def textrank(text: str, top_n: int = 20, language: str = 'zh', window_size: int = 5) -> Dict[str, float]:
        """
        TextRank关键词提取

        Args:
            text: 输入文本
            top_n: 返回的关键词数量
            language: 语言
            window_size: 窗口大小（用于建立词语共现图）

        Returns:
            关键词-权重字典
        """
        # 分词和预处理
        tokens = TextPreprocessor.tokenize(text, language)
        tokens = TextPreprocessor.remove_stopwords(tokens, language)

        if len(tokens) < 3:
            return {}

        # 建立词语共现图
        graph = {}
        for i, token in enumerate(tokens):
            if token not in graph:
                graph[token] = set()

            # 构建窗口内的共现关系
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)

            for j in range(start, end):
                if j != i and j < len(tokens):
                    graph[token].add(tokens[j])

        # PageRank算法
        scores = {token: 1.0 for token in graph}
        d = 0.85  # 阻尼系数
        iterations = 10

        for _ in range(iterations):
            new_scores = {}
            for token in graph:
                score = (1 - d) + d * sum(
                    scores[neighbor] / len(graph[neighbor])
                    for neighbor in graph
                    if token in graph[neighbor] and len(graph[neighbor]) > 0
                )
                new_scores[token] = score
            scores = new_scores

        # 排序并返回Top-N
        sorted_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_keywords[:top_n])

    @staticmethod
    def extract_phrases(tokens: List[str], min_length: int = 2, max_length: int = 4) -> List[str]:
        """
        提取关键短语（连续的关键词组合）

        Args:
            tokens: 分词结果
            min_length: 最小短语长度
            max_length: 最大短语长度

        Returns:
            短语列表
        """
        phrases = []

        for length in range(min_length, max_length + 1):
            for i in range(len(tokens) - length + 1):
                phrase = ''.join(tokens[i:i + length])
                if len(phrase) > 1:
                    phrases.append(phrase)

        # 按频率排序
        phrase_freq = Counter(phrases)
        sorted_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)

        return [phrase for phrase, _ in sorted_phrases]


class TopicExtractor:
    """主题识别器"""

    @staticmethod
    def identify_topics(text: str, language: str = 'zh', num_topics: int = 5) -> List[Tuple[str, float]]:
        """
        识别主要主题（基于关键词）

        Args:
            text: 输入文本
            language: 语言
            num_topics: 主题数量

        Returns:
            [(主题名称, 权重), ...]
        """
        # 使用TF-IDF提取关键词
        keywords_dict = KeywordExtractor.tfidf([text], top_n=num_topics * 3, language=language)

        # 将关键词作为主题
        topics = sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)[:num_topics]

        return topics

    @staticmethod
    def extract_entities(text: str, language: str = 'zh') -> List[str]:
        """
        命名实体识别（简化版）

        Args:
            text: 输入文本
            language: 语言

        Returns:
            实体列表
        """
        tokens = TextPreprocessor.tokenize(text, language)

        # 简化实体识别：找出长度较长的连续词组
        entities = []
        current_entity = []

        for token in tokens:
            if len(token) >= 2:
                current_entity.append(token)
            else:
                if len(current_entity) > 1:
                    entities.append(''.join(current_entity))
                current_entity = []

        if len(current_entity) > 1:
            entities.append(''.join(current_entity))

        return entities


class SentimentAnalyzer:
    """情感分析器"""

    # 积极词表
    POSITIVE_WORDS = {
        '好', '优秀', '棒', '喜欢', '热爱', '成功', '赞', '厉害', '太好了',
        '非常好', '很好', '不错', '相当不错', '完美', '太完美了', '令人惊喜',
        'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic',
        'awesome', 'brilliant', 'outstanding', 'superb', 'love', 'best',
        'perfect', 'beautiful', 'great', 'nice', 'happy', 'delighted'
    }

    # 消极词表
    NEGATIVE_WORDS = {
        '差', '糟糕', '失败', '问题', '讨厌', '恨', '坏', '太差了', '垃圾',
        '不行', '很差', '烂', '太烂了', '讨人厌', '令人失望',
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'dreadful',
        'hate', 'dislike', 'worst', 'ugly', 'sad', 'disappointed',
        'disappointing', 'failed', 'failure', 'wrong', 'bad'
    }

    @staticmethod
    def analyze(text: str, language: str = 'zh') -> Tuple[str, float]:
        """
        分析文本情感

        Args:
            text: 输入文本
            language: 语言

        Returns:
            (情感标签, 置信度)
        """
        text_lower = text.lower()

        # 统计积极和消极词数
        positive_count = sum(1 for word in SentimentAnalyzer.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in SentimentAnalyzer.NEGATIVE_WORDS if word in text_lower)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return 'neutral', 0.0

        # 计算情感分数
        sentiment_score = (positive_count - negative_count) / total_sentiment_words

        # 分类和置信度
        if sentiment_score > 0.3:
            return 'positive', abs(sentiment_score)
        elif sentiment_score < -0.3:
            return 'negative', abs(sentiment_score)
        else:
            return 'neutral', 1 - abs(sentiment_score)


if __name__ == "__main__":
    print("NLP文本处理模块已加载")

    # 示例使用
    test_text = "这个视频非常好，讲解得太清楚了，我很喜欢这个内容，学到了很多有用的知识"

    # 关键词提取
    print("\n关键词提取（TF-IDF）:")
    keywords = KeywordExtractor.tfidf([test_text], top_n=5)
    for keyword, score in keywords.items():
        print(f"  {keyword}: {score:.3f}")

    # TextRank
    print("\nTextRank关键词:")
    keywords_tr = KeywordExtractor.textrank(test_text, top_n=5)
    for keyword, score in keywords_tr.items():
        print(f"  {keyword}: {score:.3f}")

    # 主题识别
    print("\n主题识别:")
    topics = TopicExtractor.identify_topics(test_text, num_topics=3)
    for topic, weight in topics:
        print(f"  {topic}: {weight:.3f}")

    # 情感分析
    print("\n情感分析:")
    sentiment, confidence = SentimentAnalyzer.analyze(test_text)
    print(f"  情感: {sentiment}")
    print(f"  置信度: {confidence:.3f}")
