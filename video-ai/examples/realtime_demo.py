"""
实时推荐引擎演示脚本

演示实时推荐引擎的核心功能：
1. 模拟用户行为流
2. 实时兴趣更新
3. 推荐结果变化
4. 性能测试
"""

import sys
from pathlib import Path
import time
import random
from typing import List, Dict
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.realtime_recommendation import (
    RealtimeRecommendationEngine,
    UserBehavior
)


class RealtimeRecommendationDemo:
    """实时推荐引擎演示类"""

    def __init__(self):
        """初始化演示环境"""
        print("=" * 80)
        print("实时推荐引擎演示")
        print("=" * 80)
        print()

        # 创建推荐引擎
        self.engine = RealtimeRecommendationEngine(
            window_size=100,
            update_interval=10.0,  # 10秒更新间隔（演示用）
            decay_factor=0.95,
            trending_window=300  # 5分钟热门窗口
        )

        # 准备测试数据
        self._prepare_test_data()

    def _prepare_test_data(self):
        """准备测试数据"""
        print("📦 准备测试数据...")

        # 视频元数据
        self.videos = {
            # AI 相关
            'ai_intro_001': {'topics': ['AI', '机器学习', '教育'], 'category': '技术教育'},
            'ai_advanced_002': {'topics': ['AI', '深度学习', '高级'], 'category': '技术教育'},
            'ai_practice_003': {'topics': ['AI', '实践', '项目'], 'category': '实战'},

            # 编程相关
            'python_basic_001': {'topics': ['编程', 'Python', '入门'], 'category': '编程'},
            'python_advanced_002': {'topics': ['编程', 'Python', '高级'], 'category': '编程'},
            'javascript_001': {'topics': ['编程', 'JavaScript', 'Web'], 'category': '编程'},

            # 数据科学
            'data_science_001': {'topics': ['数据科学', 'Python', '分析'], 'category': '数据'},
            'data_viz_002': {'topics': ['数据科学', '可视化', 'Python'], 'category': '数据'},

            # 娱乐
            'game_review_001': {'topics': ['游戏', '评测', '娱乐'], 'category': '娱乐'},
            'vlog_daily_001': {'topics': ['生活', 'Vlog', '日常'], 'category': '生活'},

            # 商业
            'business_001': {'topics': ['商业', '创业', '管理'], 'category': '商业'},
            'marketing_002': {'topics': ['商业', '营销', '策略'], 'category': '商业'},
        }

        # 添加到引擎
        for video_id, metadata in self.videos.items():
            self.engine.add_video_metadata(video_id, metadata)

        # 用户配置
        self.users = {
            'user_alice': {'interests': ['AI', '机器学习'], 'style': 'technical'},
            'user_bob': {'interests': ['编程', 'Python'], 'style': 'practical'},
            'user_charlie': {'interests': ['数据科学', '分析'], 'style': 'analytical'},
            'user_diana': {'interests': ['游戏', '娱乐'], 'style': 'casual'},
        }

        print(f"✅ 已加载 {len(self.videos)} 个视频")
        print(f"✅ 已配置 {len(self.users)} 个用户")
        print()

    def demo_1_user_behavior_tracking(self):
        """演示1: 用户行为追踪"""
        print("\n" + "=" * 80)
        print("演示 1: 用户行为追踪")
        print("=" * 80)

        user_id = 'user_alice'
        print(f"\n👤 用户: {user_id}")
        print(f"兴趣: {self.users[user_id]['interests']}")

        # 模拟一系列行为
        behaviors = [
            UserBehavior(user_id, 'view', 'ai_intro_001', duration=300),
            UserBehavior(user_id, 'like', 'ai_intro_001'),
            UserBehavior(user_id, 'view', 'python_basic_001', duration=180),
            UserBehavior(user_id, 'view', 'ai_advanced_002', duration=450),
            UserBehavior(user_id, 'share', 'ai_advanced_002'),
        ]

        print(f"\n📊 模拟 {len(behaviors)} 个行为...")
        for i, behavior in enumerate(behaviors, 1):
            self.engine.track_behavior(behavior)
            print(f"  {i}. {behavior.action.upper():8s} - {behavior.video_id} "
                  f"({behavior.duration}s)")
            time.sleep(0.1)  # 模拟时间间隔

        # 获取用户洞察
        print("\n🔍 用户洞察:")
        insights = self.engine.get_user_insights(user_id)

        print(f"  总行为数: {insights['total_behaviors']}")
        print(f"  参与度评分: {insights['engagement_score']:.2f}")
        print(f"  主要兴趣: {', '.join(insights['top_interests'][:3])}")

        print("\n  兴趣分布:")
        for topic, score in sorted(
            insights['interest_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            print(f"    {topic:15s}: {'█' * int(score * 50)} {score:.2%}")

    def demo_2_realtime_interest_update(self):
        """演示2: 实时兴趣更新"""
        print("\n" + "=" * 80)
        print("演示 2: 实时兴趣更新")
        print("=" * 80)

        user_id = 'user_bob'
        print(f"\n👤 用户: {user_id}")
        print(f"初始兴趣: {self.users[user_id]['interests']}")

        # 第一阶段：Python 相关
        print("\n📺 阶段 1: 观看 Python 相关内容...")
        for _ in range(3):
            self.engine.track_behavior(
                UserBehavior(user_id, 'view', 'python_basic_001', duration=200)
            )
            self.engine.track_behavior(
                UserBehavior(user_id, 'like', 'python_basic_001')
            )

        insights_1 = self.engine.get_user_insights(user_id)
        print(f"  主要兴趣: {insights_1['top_interests'][:3]}")

        # 第二阶段：转向 AI
        print("\n📺 阶段 2: 转向 AI 相关内容...")
        time.sleep(1)  # 模拟时间流逝

        for _ in range(5):
            self.engine.track_behavior(
                UserBehavior(user_id, 'view', 'ai_intro_001', duration=300)
            )
            self.engine.track_behavior(
                UserBehavior(user_id, 'like', 'ai_intro_001')
            )

        # 强制更新兴趣
        profile = self.engine.profiles[user_id]
        self.engine._update_interests(profile)

        insights_2 = self.engine.get_user_insights(user_id)
        print(f"  主要兴趣: {insights_2['top_interests'][:3]}")

        # 显示兴趣变化
        print("\n📊 兴趣变化对比:")
        all_topics = set(insights_1['interest_scores'].keys()) | set(
            insights_2['interest_scores'].keys()
        )

        for topic in sorted(all_topics):
            score_1 = insights_1['interest_scores'].get(topic, 0)
            score_2 = insights_2['interest_scores'].get(topic, 0)
            change = score_2 - score_1

            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"  {topic:15s}: {score_1:.2%} {arrow} {score_2:.2%} "
                  f"({change:+.2%})")

    def demo_3_recommendation_evolution(self):
        """演示3: 推荐结果演化"""
        print("\n" + "=" * 80)
        print("演示 3: 推荐结果演化")
        print("=" * 80)

        user_id = 'user_charlie'
        print(f"\n👤 用户: {user_id}")

        # 冷启动
        print("\n❄️ 冷启动阶段（无历史数据）:")
        recs_cold = self.engine.get_recommendations(user_id, num_recommendations=5)

        if recs_cold:
            for i, rec in enumerate(recs_cold, 1):
                print(f"  {i}. {rec['video_id']:20s} - {rec['reason']}")
        else:
            print("  （无推荐结果 - 需要热门内容数据）")

        # 添加一些行为
        print("\n📺 开始观看数据科学相关内容...")
        behaviors = [
            ('view', 'data_science_001', 400),
            ('like', 'data_science_001', 0),
            ('view', 'data_viz_002', 300),
            ('share', 'data_viz_002', 0),
            ('view', 'python_advanced_002', 250),
        ]

        for action, video_id, duration in behaviors:
            self.engine.track_behavior(
                UserBehavior(user_id, action, video_id, duration=duration)
            )
            print(f"  ✓ {action} - {video_id}")

        # 强制更新兴趣
        profile = self.engine.profiles[user_id]
        self.engine._update_interests(profile)

        # 获取新推荐
        print("\n🎯 基于行为的推荐:")
        recs_warm = self.engine.get_recommendations(
            user_id,
            num_recommendations=5,
            exclude_watched=True
        )

        for i, rec in enumerate(recs_warm, 1):
            print(f"  {i}. {rec['video_id']:20s} "
                  f"(分数: {rec['score']:.3f}) - {rec['reason']}")

    def demo_4_collaborative_filtering(self):
        """演示4: 协同过滤"""
        print("\n" + "=" * 80)
        print("演示 4: 协同过滤推荐")
        print("=" * 80)

        # 创建相似用户
        print("\n👥 创建用户群体...")

        # Alice 和 Bob 都喜欢 AI
        alice_behaviors = [
            ('view', 'ai_intro_001', 300),
            ('like', 'ai_intro_001', 0),
            ('view', 'ai_advanced_002', 400),
            ('like', 'ai_advanced_002', 0),
            ('view', 'python_advanced_002', 200),
        ]

        bob_behaviors = [
            ('view', 'ai_intro_001', 350),
            ('like', 'ai_intro_001', 0),
            ('view', 'ai_advanced_002', 450),
            ('like', 'ai_advanced_002', 0),
            ('view', 'data_science_001', 300),  # Bob 还喜欢这个
            ('like', 'data_science_001', 0),
        ]

        print("  Alice 的行为...")
        for action, video_id, duration in alice_behaviors:
            self.engine.track_behavior(
                UserBehavior('user_alice', action, video_id, duration=duration)
            )

        print("  Bob 的行为...")
        for action, video_id, duration in bob_behaviors:
            self.engine.track_behavior(
                UserBehavior('user_bob', action, video_id, duration=duration)
            )

        # 更新兴趣
        for user_id in ['user_alice', 'user_bob']:
            if user_id in self.engine.profiles:
                self.engine._update_interests(self.engine.profiles[user_id])

        # 计算相似度
        similarity = self.engine._calculate_user_similarity('user_alice', 'user_bob')
        print(f"\n🔗 Alice 和 Bob 的相似度: {similarity:.3f}")

        # 为 Alice 推荐
        print("\n🎯 为 Alice 推荐（应该包含 Bob 喜欢的 data_science_001）:")
        recs = self.engine.get_recommendations('user_alice', num_recommendations=5)

        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec['video_id']:20s} "
                  f"(分数: {rec['score']:.3f}) - {rec['method']}")

    def demo_5_trending_content(self):
        """演示5: 热门内容检测"""
        print("\n" + "=" * 80)
        print("演示 5: 热门内容检测")
        print("=" * 80)

        print("\n📈 模拟多个用户观看行为...")

        # 模拟多个用户观看相同的热门视频
        hot_video = 'ai_intro_001'
        users_count = 20

        for i in range(users_count):
            user_id = f'temp_user_{i}'

            # 大部分用户观看热门视频
            if random.random() < 0.7:  # 70% 概率
                self.engine.track_behavior(
                    UserBehavior(user_id, 'view', hot_video, duration=300)
                )
                if random.random() < 0.5:  # 50% 点赞
                    self.engine.track_behavior(
                        UserBehavior(user_id, 'like', hot_video)
                    )

            # 随机观看其他视频
            other_video = random.choice(list(self.videos.keys()))
            self.engine.track_behavior(
                UserBehavior(user_id, 'view', other_video, duration=200)
            )

        # 更新热门内容
        print("  正在分析热门内容...")
        self.engine.update_trending()

        # 显示热门内容
        print("\n🔥 当前热门内容 Top 5:")
        trending = sorted(
            self.engine.trending_cache.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        for i, (video_id, score) in enumerate(trending, 1):
            bar = '█' * int(score * 40)
            print(f"  {i}. {video_id:20s}: {bar} {score:.3f}")

    def demo_6_performance_test(self):
        """演示6: 性能测试"""
        print("\n" + "=" * 80)
        print("演示 6: 性能测试")
        print("=" * 80)

        # 测试1: 行为追踪性能
        print("\n⚡ 测试 1: 行为追踪性能")
        num_behaviors = 1000

        start_time = time.time()
        for i in range(num_behaviors):
            user_id = f'perf_user_{i % 10}'  # 10个用户
            video_id = random.choice(list(self.videos.keys()))
            action = random.choice(['view', 'like', 'skip'])

            self.engine.track_behavior(
                UserBehavior(user_id, action, video_id, duration=random.randint(60, 600))
            )

        elapsed = time.time() - start_time
        avg_latency = (elapsed / num_behaviors) * 1000  # 毫秒

        print(f"  总行为数: {num_behaviors}")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  平均延迟: {avg_latency:.2f} ms")
        print(f"  吞吐量: {num_behaviors / elapsed:.0f} 行为/秒")

        if avg_latency < 10:
            print("  ✅ 满足性能目标 (< 10ms)")
        else:
            print("  ⚠️  未达到性能目标")

        # 测试2: 推荐生成性能
        print("\n⚡ 测试 2: 推荐生成性能")
        num_recommendations = 100

        start_time = time.time()
        for i in range(num_recommendations):
            user_id = f'perf_user_{i % 10}'
            recs = self.engine.get_recommendations(user_id, num_recommendations=10)

        elapsed = time.time() - start_time
        avg_latency = (elapsed / num_recommendations) * 1000

        print(f"  推荐次数: {num_recommendations}")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  平均延迟: {avg_latency:.2f} ms")

        if avg_latency < 100:
            print("  ✅ 满足性能目标 (< 100ms)")
        else:
            print("  ⚠️  未达到性能目标")

        # 系统统计
        print("\n📊 系统统计:")
        stats = self.engine.get_statistics()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")

    def run_all_demos(self):
        """运行所有演示"""
        demos = [
            self.demo_1_user_behavior_tracking,
            self.demo_2_realtime_interest_update,
            self.demo_3_recommendation_evolution,
            self.demo_4_collaborative_filtering,
            self.demo_5_trending_content,
            self.demo_6_performance_test,
        ]

        for demo in demos:
            demo()
            print()
            input("按 Enter 继续下一个演示...")

        print("\n" + "=" * 80)
        print("✅ 所有演示完成!")
        print("=" * 80)


def main():
    """主函数"""
    demo = RealtimeRecommendationDemo()

    # 运行所有演示
    demo.run_all_demos()


if __name__ == "__main__":
    main()
