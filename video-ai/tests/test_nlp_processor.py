"""
测试 NLP 处理器

测试关键词提取、主题识别、情感分析等功能
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.nlp_processor import (
    TextPreprocessor,
    KeywordExtractor,
    TopicExtractor,
    SentimentAnalyzer
)


def test_text_preprocessing():
    """测试文本预处理"""
    print("\n=== 测试文本预处理 ===\n")

    # 测试中文文本
    text_zh = "这个视频非常好,讲解得太清楚了! 我很喜欢这个内容。"

    print("原文本:", text_zh)

    # 清洁
    cleaned = TextPreprocessor.clean_text(text_zh)
    print(f"清洁后: {cleaned}")

    # 分词
    tokens = TextPreprocessor.tokenize(text_zh, language='zh')
    print(f"分词结果: {tokens[:10]}")

    # 去停用词
    filtered = TextPreprocessor.remove_stopwords(tokens, language='zh')
    print(f"去停用词: {filtered}")

    print("\n✓ 文本预处理测试通过")


def test_keyword_extraction_tfidf():
    """测试 TF-IDF 关键词提取"""
    print("\n=== 测试 TF-IDF 关键词提取 ===\n")

    documents = [
        "这个视频讲解了人工智能和机器学习的基础知识",
        "深度学习是机器学习的一个重要分支",
        "神经网络是深度学习的核心技术"
    ]

    print("文档数:", len(documents))
    print("提取关键词...")

    keywords = KeywordExtractor.tfidf(documents, top_n=10, language='zh')

    print("\n关键词 (TF-IDF):")
    for keyword, score in keywords.items():
        print(f"  {keyword}: {score:.3f}")

    print("\n✓ TF-IDF 测试通过")


def test_keyword_extraction_textrank():
    """测试 TextRank 关键词提取"""
    print("\n=== 测试 TextRank 关键词提取 ===\n")

    text = """
    人工智能是计算机科学的一个重要分支,它研究如何让计算机模拟人类的智能。
    机器学习是人工智能的核心技术,通过算法让计算机从数据中学习规律。
    深度学习是机器学习的一种方法,它使用神经网络来处理复杂的模式识别任务。
    """

    print("文本长度:", len(text), "字符")
    print("提取关键词...")

    keywords = KeywordExtractor.textrank(text, top_n=10, language='zh')

    print("\n关键词 (TextRank):")
    for keyword, score in keywords.items():
        print(f"  {keyword}: {score:.3f}")

    print("\n✓ TextRank 测试通过")


def test_phrase_extraction():
    """测试短语提取"""
    print("\n=== 测试短语提取 ===\n")

    text = "人工智能和机器学习是现代科技的重要组成部分"

    tokens = TextPreprocessor.tokenize(text, language='zh')
    tokens = TextPreprocessor.remove_stopwords(tokens, language='zh')

    print(f"分词: {tokens}")

    phrases = KeywordExtractor.extract_phrases(tokens, min_length=2, max_length=4)

    print(f"\n提取的短语 (前10个):")
    for phrase in phrases[:10]:
        print(f"  {phrase}")

    print("\n✓ 短语提取测试通过")


def test_topic_identification():
    """测试主题识别"""
    print("\n=== 测试主题识别 ===\n")

    text = """
    今天我们要讨论人工智能技术的发展。
    机器学习是人工智能的重要组成部分,包括监督学习、无监督学习和强化学习。
    深度学习使用神经网络来解决复杂问题,在图像识别和自然语言处理领域取得了重大突破。
    自然语言处理帮助计算机理解和生成人类语言。
    """

    print("文本长度:", len(text), "字符")
    print("识别主题...")

    topics = TopicExtractor.identify_topics(text, language='zh', num_topics=5)

    print("\n识别的主题:")
    for topic, weight in topics:
        print(f"  {topic}: {weight:.3f}")

    print("\n✓ 主题识别测试通过")


def test_entity_extraction():
    """测试实体识别"""
    print("\n=== 测试实体识别 ===\n")

    text = "今天在北京大学听了一场关于人工智能的讲座,主讲人是李明教授"

    print("文本:", text)
    print("提取实体...")

    entities = TopicExtractor.extract_entities(text, language='zh')

    print(f"\n提取的实体:")
    for entity in entities:
        print(f"  {entity}")

    print("\n✓ 实体识别测试通过")


def test_sentiment_analysis():
    """测试情感分析"""
    print("\n=== 测试情感分析 ===\n")

    test_texts = [
        "这个视频非常好,讲解得太清楚了,我很喜欢!",
        "内容很差,浪费时间,完全不值得看。",
        "这个视频介绍了人工智能的基本概念。"
    ]

    for text in test_texts:
        sentiment, confidence = SentimentAnalyzer.analyze(text, language='zh')
        print(f"文本: {text}")
        print(f"  情感: {sentiment} (置信度: {confidence:.3f})")
        print()

    print("✓ 情感分析测试通过")


def test_english_support():
    """测试英文支持"""
    print("\n=== 测试英文支持 ===\n")

    text = "Artificial intelligence and machine learning are transforming technology. Deep learning uses neural networks to solve complex problems."

    print("英文文本:", text)

    # 关键词提取
    keywords = KeywordExtractor.tfidf([text], top_n=5, language='en')
    print("\n关键词:")
    for keyword, score in keywords.items():
        print(f"  {keyword}: {score:.3f}")

    # 情感分析
    sentiment, confidence = SentimentAnalyzer.analyze(text, language='en')
    print(f"\n情感: {sentiment} (置信度: {confidence:.3f})")

    print("\n✓ 英文支持测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("NLP 处理器测试套件")
    print("=" * 60)

    test_text_preprocessing()
    test_keyword_extraction_tfidf()
    test_keyword_extraction_textrank()
    test_phrase_extraction()
    test_topic_identification()
    test_entity_extraction()
    test_sentiment_analysis()
    test_english_support()

    print("\n" + "=" * 60)
    print("所有测试通过! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
