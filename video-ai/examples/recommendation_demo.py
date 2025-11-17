"""
推荐系统完整示例

展示如何使用推荐引擎、用户画像管理和NLP处理
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.recommendation import HybridRecommender
from src.models.user_profile import UserProfile
from src.utils.nlp_processor import (
    KeywordExtractor, TextPreprocessor, TopicExtractor, SentimentAnalyzer
)


def demo_nlp_processing():
    """演示NLP文本处理功能"""
    print("=" * 70)
    print("演示1: NLP文本处理")
    print("=" * 70)

    # 示例转录文本
    transcript = """
    大家好，今天我们将深入学习深度学习的基础概念。深度学习是机器学习的一个重要分支。
    在这个视频中，我们会讨论神经网络、反向传播算法和梯度下降。
    深度学习在计算机视觉、自然语言处理等领域都有重要应用。
    通过学习本课程，你将能够理解深度学习的核心原理。
    这个知识非常重要，希望对你有帮助！
    """

    print("\n原始文本:")
    print(transcript[:100] + "...")

    # 1. 关键词提取
    print("\n1. 关键词提取 (TF-IDF):")
    keywords_tfidf = KeywordExtractor.tfidf([transcript], top_n=10, language='zh')
    for i, (keyword, score) in enumerate(keywords_tfidf.items(), 1):
        print(f"   {i}. {keyword}: {score:.3f}")

    # 2. TextRank关键词
    print("\n2. TextRank关键词提取:")
    keywords_textrank = KeywordExtractor.textrank(transcript, top_n=8, language='zh')
    for i, (keyword, score) in enumerate(keywords_textrank.items(), 1):
        print(f"   {i}. {keyword}: {score:.3f}")

    # 3. 主题识别
    print("\n3. 主题识别:")
    topics = TopicExtractor.identify_topics(transcript, language='zh', num_topics=5)
    for i, (topic, weight) in enumerate(topics, 1):
        print(f"   {i}. {topic}: {weight:.3f}")

    # 4. 情感分析
    print("\n4. 情感分析:")
    sentiment, confidence = SentimentAnalyzer.analyze(transcript, language='zh')
    print(f"   情感: {sentiment}")
    print(f"   置信度: {confidence:.3f}")

    # 5. 文本预处理演示
    print("\n5. 文本预处理:")
    cleaned_text = TextPreprocessor.clean_text(transcript)
    tokens = TextPreprocessor.tokenize(transcript, language='zh')
    print(f"   清洁后文本: {cleaned_text[:80]}...")
    print(f"   分词结果数: {len(tokens)}")
    print(f"   前10个词: {tokens[:10]}")


def demo_user_profile():
    """演示用户画像建模"""
    print("\n" + "=" * 70)
    print("演示2: 用户画像建模")
    print("=" * 70)

    # 创建用户
    user = UserProfile(
        user_id="user_demo_001",
        age_range="25-34",
        location="Beijing",
        device_type="mobile"
    )

    print(f"\n用户ID: {user.user_id}")
    print(f"年龄段: {user.age_range}")
    print(f"位置: {user.location}")

    # 添加观看历史
    print("\n添加观看历史:")

    watch_events = [
        ("video_001", "Technology", ["AI", "深度学习", "机器学习"], 1200, 0.95),
        ("video_002", "Technology", ["编程", "Python", "代码"], 800, 0.85),
        ("video_003", "Education", ["教学", "在线教育", "学习"], 600, 0.80),
        ("video_004", "Technology", ["计算机视觉", "CNN", "图像识别"], 900, 0.90),
        ("video_005", "Technology", ["NLP", "自然语言处理", "BERT"], 1000, 0.92),
    ]

    for video_id, category, tags, watch_time, watch_pct in watch_events:
        user.add_watch_event(video_id, category, tags, watch_time, watch_pct)
        print(f"   - {video_id}: {category} ({watch_pct*100:.0f}%观看)")

    # 添加反馈
    print("\n添加反馈:")
    feedbacks = [
        ("video_001", "like"),
        ("video_002", "like"),
        ("video_003", "save"),
        ("video_004", "like"),
        ("video_005", "share"),
    ]

    for video_id, action in feedbacks:
        user.add_feedback_event(video_id, action)
        print(f"   - {video_id}: {action}")

    # 计算指标
    print("\n用户指标:")
    engagement = user.calculate_engagement_score()
    loyalty = user.calculate_loyalty_score()
    user.update_activity_level()

    print(f"   参与度评分: {engagement:.3f}")
    print(f"   忠诚度评分: {loyalty:.3f}")
    print(f"   活跃度: {user.activity_level}")

    # 展示Top兴趣
    print("\nTop兴趣标签:")
    top_interests = user.get_top_interests(k=8)
    for i, interest in enumerate(top_interests, 1):
        print(f"   {i}. {interest.topic}")
        print(f"      权重: {interest.weight:.3f}, 置信度: {interest.confidence:.3f}")

    # 展示分类兴趣
    print("\nTop分类:")
    top_categories = user.get_top_categories(k=5)
    for i, (category, weight) in enumerate(top_categories, 1):
        print(f"   {i}. {category}: {weight:.3f}")


def demo_recommendation():
    """演示混合推荐系统"""
    print("\n" + "=" * 70)
    print("演示3: 混合推荐系统")
    print("=" * 70)

    # 创建推荐器
    recommender = HybridRecommender(
        cf_weight=0.40,
        cb_weight=0.35,
        popularity_weight=0.15,
        diversity_weight=0.10
    )

    print("\n推荐权重配置:")
    print(f"   协同过滤: {recommender.cf_weight*100:.0f}%")
    print(f"   内容推荐: {recommender.cb_weight*100:.0f}%")
    print(f"   热度算法: {recommender.popularity_weight*100:.0f}%")
    print(f"   多样性: {recommender.diversity_weight*100:.0f}%")

    # 添加用户交互数据
    print("\n添加用户交互数据:")
    interactions = [
        ("user_001", "video_001", 0.9),
        ("user_001", "video_002", 0.8),
        ("user_002", "video_001", 0.95),
        ("user_002", "video_003", 0.7),
        ("user_003", "video_002", 0.85),
        ("user_003", "video_003", 0.9),
    ]

    for user_id, video_id, rating in interactions:
        recommender.add_video_interaction(user_id, video_id, rating)
        print(f"   用户{user_id} 观看 {video_id} (评分: {rating})")

    # 添加视频特征
    print("\n添加视频特征:")
    video_features = {
        "video_001": {"AI": 0.9, "deep_learning": 0.85, "tech": 0.8},
        "video_002": {"programming": 0.9, "python": 0.8, "code": 0.75},
        "video_003": {"education": 0.85, "teaching": 0.8, "online": 0.7},
        "video_004": {"CV": 0.95, "CNN": 0.9, "vision": 0.85},
        "video_005": {"NLP": 0.9, "BERT": 0.85, "language": 0.8},
    }

    for video_id, features in video_features.items():
        recommender.add_video_features(video_id, features)
        print(f"   {video_id}: {', '.join(f'{k}:{v:.2f}' for k, v in features.items())}")

    # 添加视频统计
    print("\n添加视频统计:")
    video_stats = {
        "video_001": (100000, 5000, 500, 1000),
        "video_002": (50000, 2000, 200, 500),
        "video_003": (30000, 1500, 150, 300),
        "video_004": (150000, 8000, 800, 1500),
        "video_005": (80000, 4000, 400, 800),
    }

    for video_id, (views, likes, shares, comments) in video_stats.items():
        recommender.add_video_stats(video_id, views, likes, shares, comments)
        print(f"   {video_id}: 浏览{views}, 赞{likes}, 分享{shares}, 评论{comments}")

    # 获取推荐
    print("\n推荐结果 (为user_001):")
    recommendations = recommender.recommend(
        user_id="user_001",
        k=5,
        seed_video_id="video_001"
    )

    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. {rec.video_id}")
        print(f"      总分: {rec.score:.3f}")
        print(f"      协同过滤: {rec.cf_score:.3f}")
        print(f"      内容推荐: {rec.cb_score:.3f}")
        print(f"      热度: {rec.popularity_score:.3f}")
        print(f"      推荐原因: {rec.reason}")

    # 获取探索性推荐
    print("\n探索性推荐 (多样化内容):")
    exploration = recommender.get_recommendations_for_exploration(k=3)
    for i, (video_id, score) in enumerate(exploration, 1):
        print(f"   {i}. {video_id}: {score:.3f}")


def demo_integrated_workflow():
    """演示完整工作流程"""
    print("\n" + "=" * 70)
    print("演示4: 完整工作流程集成")
    print("=" * 70)

    # 步骤1: NLP处理转录文本
    print("\n步骤1: 处理视频转录...")
    transcript = """
    今天我们学习深度学习和神经网络。深度学习是AI的核心技术。
    我们将讨论前向传播和反向传播的原理。这个很有用。
    """

    keywords = KeywordExtractor.tfidf([transcript], top_n=5, language='zh')
    topics = TopicExtractor.identify_topics(transcript, language='zh', num_topics=3)
    sentiment, conf = SentimentAnalyzer.analyze(transcript, language='zh')

    print(f"   提取关键词: {', '.join(list(keywords.keys())[:3])}")
    print(f"   识别主题: {', '.join(t[0] for t in topics[:2])}")
    print(f"   情感分析: {sentiment} (置信度: {conf:.2f})")

    # 步骤2: 构建视频特征
    print("\n步骤2: 构建视频特征向量...")
    video_features = dict(keywords)
    video_features.update({f"topic_{t[0]}": t[1] for t in topics})
    print(f"   特征维度: {len(video_features)}")

    # 步骤3: 更新用户画像
    print("\n步骤3: 更新用户画像...")
    user = UserProfile(user_id="user_integrated")
    user.add_watch_event(
        video_id="current_video",
        category=topics[0][0] if topics else "General",
        tags=list(keywords.keys())[:5],
        watch_time=600,
        watch_percentage=0.85
    )
    user.add_feedback_event("current_video", "like")

    engagement = user.calculate_engagement_score()
    print(f"   用户参与度: {engagement:.3f}")

    # 步骤4: 生成推荐
    print("\n步骤4: 生成个性化推荐...")
    recommender = HybridRecommender()

    # 添加示例数据
    for i in range(1, 6):
        video_id = f"video_{i}"
        recommender.add_video_features(video_id, {f"tag_{j}": 0.5 + j*0.1 for j in range(3)})
        recommender.add_video_stats(video_id, views=50000*i, likes=2500*i, shares=250*i, comments=500*i)
        recommender.add_video_interaction("user_integrated", video_id, 0.5 + i*0.1)

    recommendations = recommender.recommend(
        user_id="user_integrated",
        k=3,
        seed_video_id="current_video"
    )

    print(f"   推荐结果:")
    for rec in recommendations[:3]:
        print(f"     - {rec.video_id} (分数: {rec.score:.3f})")


def main():
    """运行所有演示"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║            Video-AI 推荐系统完整演示                                ║
║                                                                    ║
║     包含: NLP处理、用户画像、混合推荐、完整集成                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # 运行所有演示
        demo_nlp_processing()
        demo_user_profile()
        demo_recommendation()
        demo_integrated_workflow()

        print("\n" + "=" * 70)
        print("演示完成!")
        print("=" * 70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
