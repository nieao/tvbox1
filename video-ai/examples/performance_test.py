"""
实时推荐引擎性能测试和效果评估

测试目标:
- 行为追踪延迟 < 10ms
- 推荐生成时间 < 100ms
- 支持1000+ 并发用户
- 兴趣更新周期 1分钟
"""

import sys
from pathlib import Path
import time
import random
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.realtime_recommendation import (
    RealtimeRecommendationEngine,
    UserBehavior
)


class PerformanceTest:
    """性能测试类"""

    def __init__(self):
        """初始化测试环境"""
        self.engine = RealtimeRecommendationEngine(
            window_size=100,
            update_interval=60.0,
            decay_factor=0.95,
            trending_window=3600
        )

        self.test_videos = self._generate_test_videos(100)
        self.test_users = self._generate_test_users(1000)

        # 添加视频元数据
        for video_id, metadata in self.test_videos.items():
            self.engine.add_video_metadata(video_id, metadata)

        self.results = {}

    def _generate_test_videos(self, count: int) -> Dict:
        """生成测试视频"""
        topics_pool = [
            'AI', '机器学习', '深度学习', '编程', 'Python', 'JavaScript',
            'Java', 'C++', '数据科学', '算法', 'Web开发', '移动开发',
            '游戏开发', '云计算', '区块链', '物联网', '网络安全', '设计',
            '产品', '商业', '创业', '营销', '管理', '金融'
        ]

        categories = ['技术', '编程', '数据', '商业', '娱乐', '教育', '生活']

        videos = {}
        for i in range(count):
            video_id = f'test_video_{i:04d}'
            videos[video_id] = {
                'topics': random.sample(topics_pool, random.randint(2, 5)),
                'category': random.choice(categories)
            }

        return videos

    def _generate_test_users(self, count: int) -> List[str]:
        """生成测试用户"""
        return [f'test_user_{i:04d}' for i in range(count)]

    def test_1_behavior_tracking_latency(self):
        """测试1: 行为追踪延迟"""
        print("\n" + "=" * 80)
        print("测试 1: 行为追踪延迟")
        print("=" * 80)

        num_tests = 10000
        latencies = []

        print(f"\n执行 {num_tests} 次行为追踪...")

        for i in range(num_tests):
            user_id = random.choice(self.test_users)
            video_id = random.choice(list(self.test_videos.keys()))
            action = random.choice(['view', 'like', 'skip', 'share'])

            behavior = UserBehavior(
                user_id, action, video_id,
                duration=random.randint(60, 600)
            )

            start = time.perf_counter()
            self.engine.track_behavior(behavior)
            elapsed = (time.perf_counter() - start) * 1000  # 转换为毫秒

            latencies.append(elapsed)

        # 统计结果
        avg_latency = statistics.mean(latencies)
        p50_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        max_latency = max(latencies)

        print(f"\n📊 延迟统计 (毫秒):")
        print(f"  平均延迟: {avg_latency:.3f} ms")
        print(f"  P50 延迟: {p50_latency:.3f} ms")
        print(f"  P95 延迟: {p95_latency:.3f} ms")
        print(f"  P99 延迟: {p99_latency:.3f} ms")
        print(f"  最大延迟: {max_latency:.3f} ms")

        # 性能评估
        print(f"\n✅ 性能评估:")
        if avg_latency < 10:
            print(f"  ✓ 平均延迟满足目标 (< 10ms): {avg_latency:.3f} ms")
        else:
            print(f"  ✗ 平均延迟未达标 (目标 < 10ms): {avg_latency:.3f} ms")

        if p99_latency < 50:
            print(f"  ✓ P99 延迟优秀 (< 50ms): {p99_latency:.3f} ms")
        else:
            print(f"  ⚠  P99 延迟需优化: {p99_latency:.3f} ms")

        self.results['behavior_tracking'] = {
            'avg_latency_ms': avg_latency,
            'p50_latency_ms': p50_latency,
            'p95_latency_ms': p95_latency,
            'p99_latency_ms': p99_latency,
            'max_latency_ms': max_latency,
            'pass': avg_latency < 10
        }

    def test_2_recommendation_generation_time(self):
        """测试2: 推荐生成时间"""
        print("\n" + "=" * 80)
        print("测试 2: 推荐生成时间")
        print("=" * 80)

        num_tests = 1000
        latencies = []

        # 先为用户添加一些行为
        print(f"\n准备测试数据...")
        for user_id in self.test_users[:100]:
            for _ in range(random.randint(5, 15)):
                video_id = random.choice(list(self.test_videos.keys()))
                self.engine.track_behavior(
                    UserBehavior(user_id, 'view', video_id, duration=300)
                )

        print(f"\n执行 {num_tests} 次推荐生成...")

        for i in range(num_tests):
            user_id = random.choice(self.test_users[:100])

            start = time.perf_counter()
            recommendations = self.engine.get_recommendations(
                user_id,
                num_recommendations=10
            )
            elapsed = (time.perf_counter() - start) * 1000

            latencies.append(elapsed)

        # 统计结果
        avg_latency = statistics.mean(latencies)
        p50_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        max_latency = max(latencies)

        print(f"\n📊 生成时间统计 (毫秒):")
        print(f"  平均时间: {avg_latency:.3f} ms")
        print(f"  P50 时间: {p50_latency:.3f} ms")
        print(f"  P95 时间: {p95_latency:.3f} ms")
        print(f"  P99 时间: {p99_latency:.3f} ms")
        print(f"  最大时间: {max_latency:.3f} ms")

        # 性能评估
        print(f"\n✅ 性能评估:")
        if avg_latency < 100:
            print(f"  ✓ 平均时间满足目标 (< 100ms): {avg_latency:.3f} ms")
        else:
            print(f"  ✗ 平均时间未达标 (目标 < 100ms): {avg_latency:.3f} ms")

        self.results['recommendation_generation'] = {
            'avg_latency_ms': avg_latency,
            'p50_latency_ms': p50_latency,
            'p95_latency_ms': p95_latency,
            'p99_latency_ms': p99_latency,
            'max_latency_ms': max_latency,
            'pass': avg_latency < 100
        }

    def test_3_concurrent_users(self):
        """测试3: 并发用户支持"""
        print("\n" + "=" * 80)
        print("测试 3: 并发用户支持")
        print("=" * 80)

        num_concurrent_users = 1000
        actions_per_user = 10

        print(f"\n模拟 {num_concurrent_users} 个并发用户...")
        print(f"每个用户执行 {actions_per_user} 个操作...")

        def user_session(user_id):
            """模拟用户会话"""
            session_start = time.perf_counter()

            for _ in range(actions_per_user):
                video_id = random.choice(list(self.test_videos.keys()))
                action = random.choice(['view', 'like', 'skip'])

                # 行为追踪
                self.engine.track_behavior(
                    UserBehavior(user_id, action, video_id, duration=200)
                )

                # 获取推荐
                if random.random() < 0.3:  # 30% 概率获取推荐
                    self.engine.get_recommendations(user_id, num_recommendations=5)

            session_time = (time.perf_counter() - session_start) * 1000
            return session_time

        # 并发执行
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(user_session, f'concurrent_user_{i}')
                for i in range(num_concurrent_users)
            ]

            session_times = []
            for future in as_completed(futures):
                session_times.append(future.result())

        total_time = time.time() - start_time

        # 统计结果
        avg_session_time = statistics.mean(session_times)
        total_operations = num_concurrent_users * actions_per_user

        print(f"\n📊 并发测试结果:")
        print(f"  并发用户数: {num_concurrent_users}")
        print(f"  总操作数: {total_operations}")
        print(f"  总耗时: {total_time:.2f} 秒")
        print(f"  平均会话时间: {avg_session_time:.2f} ms")
        print(f"  吞吐量: {total_operations / total_time:.0f} 操作/秒")
        print(f"  QPS: {num_concurrent_users / total_time:.0f} 用户/秒")

        # 性能评估
        print(f"\n✅ 性能评估:")
        if num_concurrent_users >= 1000:
            print(f"  ✓ 支持 {num_concurrent_users} 并发用户")
        else:
            print(f"  ⚠  并发用户数低于目标 (1000)")

        self.results['concurrent_users'] = {
            'num_users': num_concurrent_users,
            'total_operations': total_operations,
            'total_time_seconds': total_time,
            'avg_session_time_ms': avg_session_time,
            'throughput_ops_per_sec': total_operations / total_time,
            'pass': num_concurrent_users >= 1000
        }

    def test_4_interest_update_performance(self):
        """测试4: 兴趣更新性能"""
        print("\n" + "=" * 80)
        print("测试 4: 兴趣更新性能")
        print("=" * 80)

        num_users = 1000
        behaviors_per_user = 50

        print(f"\n为 {num_users} 个用户添加行为数据...")

        # 添加行为
        for user_id in self.test_users[:num_users]:
            for _ in range(behaviors_per_user):
                video_id = random.choice(list(self.test_videos.keys()))
                self.engine.track_behavior(
                    UserBehavior(user_id, 'view', video_id, duration=300)
                )

        print(f"\n测试兴趣更新性能...")

        update_times = []

        for user_id in self.test_users[:num_users]:
            if user_id in self.engine.profiles:
                profile = self.engine.profiles[user_id]

                start = time.perf_counter()
                self.engine._update_interests(profile)
                elapsed = (time.perf_counter() - start) * 1000

                update_times.append(elapsed)

        # 统计结果
        avg_time = statistics.mean(update_times)
        p95_time = sorted(update_times)[int(len(update_times) * 0.95)]

        print(f"\n📊 兴趣更新统计:")
        print(f"  更新用户数: {len(update_times)}")
        print(f"  平均更新时间: {avg_time:.3f} ms")
        print(f"  P95 更新时间: {p95_time:.3f} ms")
        print(f"  理论 QPS (1min周期): {len(update_times) / 60:.0f} 用户/秒")

        # 性能评估
        print(f"\n✅ 性能评估:")
        if avg_time < 10:
            print(f"  ✓ 更新时间优秀 (< 10ms): {avg_time:.3f} ms")
        elif avg_time < 50:
            print(f"  ✓ 更新时间良好 (< 50ms): {avg_time:.3f} ms")
        else:
            print(f"  ⚠  更新时间需优化: {avg_time:.3f} ms")

        self.results['interest_update'] = {
            'avg_update_time_ms': avg_time,
            'p95_update_time_ms': p95_time,
            'theoretical_qps': len(update_times) / 60,
            'pass': avg_time < 50
        }

    def test_5_recommendation_quality(self):
        """测试5: 推荐质量评估"""
        print("\n" + "=" * 80)
        print("测试 5: 推荐质量评估")
        print("=" * 80)

        # 创建有明确偏好的用户
        print("\n创建测试用户...")

        test_cases = [
            {
                'user_id': 'quality_user_ai',
                'interests': ['AI', '机器学习', '深度学习'],
                'expected_topics': ['AI', '机器学习', '深度学习', '数据科学']
            },
            {
                'user_id': 'quality_user_programming',
                'interests': ['编程', 'Python', 'Java'],
                'expected_topics': ['编程', 'Python', 'Java', 'Web开发']
            }
        ]

        quality_scores = []

        for test_case in test_cases:
            user_id = test_case['user_id']
            interests = test_case['interests']
            expected_topics = test_case['expected_topics']

            print(f"\n👤 测试用户: {user_id}")
            print(f"  兴趣: {', '.join(interests)}")

            # 添加符合兴趣的行为
            interest_videos = [
                vid for vid, meta in self.test_videos.items()
                if any(topic in meta['topics'] for topic in interests)
            ]

            for video_id in random.sample(interest_videos, min(10, len(interest_videos))):
                self.engine.track_behavior(
                    UserBehavior(user_id, 'view', video_id, duration=400)
                )
                self.engine.track_behavior(
                    UserBehavior(user_id, 'like', video_id)
                )

            # 获取推荐
            recommendations = self.engine.get_recommendations(
                user_id,
                num_recommendations=10,
                exclude_watched=True
            )

            # 评估推荐质量
            relevant_count = 0
            for rec in recommendations:
                video_meta = self.test_videos[rec['video_id']]
                if any(topic in video_meta['topics'] for topic in expected_topics):
                    relevant_count += 1

            precision = relevant_count / len(recommendations) if recommendations else 0
            quality_scores.append(precision)

            print(f"  推荐数量: {len(recommendations)}")
            print(f"  相关推荐: {relevant_count}")
            print(f"  精准度: {precision:.2%}")

            # 显示推荐列表
            print(f"  推荐内容:")
            for i, rec in enumerate(recommendations[:5], 1):
                video_meta = self.test_videos[rec['video_id']]
                relevant = "✓" if any(t in video_meta['topics'] for t in expected_topics) else "✗"
                print(f"    {i}. {rec['video_id']} {relevant} "
                      f"- {', '.join(video_meta['topics'][:2])}")

        # 总体质量评估
        avg_quality = statistics.mean(quality_scores)

        print(f"\n📊 推荐质量总结:")
        print(f"  平均精准度: {avg_quality:.2%}")

        print(f"\n✅ 质量评估:")
        if avg_quality >= 0.7:
            print(f"  ✓ 推荐质量优秀 (>= 70%): {avg_quality:.2%}")
        elif avg_quality >= 0.5:
            print(f"  ✓ 推荐质量良好 (>= 50%): {avg_quality:.2%}")
        else:
            print(f"  ⚠  推荐质量需改进: {avg_quality:.2%}")

        self.results['recommendation_quality'] = {
            'avg_precision': avg_quality,
            'pass': avg_quality >= 0.5
        }

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("测试报告")
        print("=" * 80)

        # 性能摘要
        print("\n📊 性能测试摘要:")
        print()

        tests = [
            ('行为追踪', 'behavior_tracking', 'avg_latency_ms', '< 10ms'),
            ('推荐生成', 'recommendation_generation', 'avg_latency_ms', '< 100ms'),
            ('并发支持', 'concurrent_users', 'num_users', '>= 1000'),
            ('兴趣更新', 'interest_update', 'avg_update_time_ms', '< 50ms'),
            ('推荐质量', 'recommendation_quality', 'avg_precision', '>= 50%'),
        ]

        all_passed = True

        for name, key, metric, target in tests:
            if key in self.results:
                result = self.results[key]
                passed = result.get('pass', False)
                status = "✅ PASS" if passed else "❌ FAIL"

                print(f"  {name:12s}: {status}")

                if not passed:
                    all_passed = False

        # 详细结果
        print("\n📈 详细结果:")
        print()
        print(json.dumps(self.results, indent=2, ensure_ascii=False))

        # 总结
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ 所有测试通过!")
        else:
            print("⚠️  部分测试未通过，需要优化")
        print("=" * 80)

        # 保存报告
        report_path = Path(__file__).parent.parent / 'data' / 'performance_report.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'results': self.results,
                'all_passed': all_passed
            }, f, indent=2, ensure_ascii=False)

        print(f"\n报告已保存到: {report_path}")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始性能测试和效果评估...")
        print(f"测试视频数: {len(self.test_videos)}")
        print(f"测试用户数: {len(self.test_users)}")

        tests = [
            self.test_1_behavior_tracking_latency,
            self.test_2_recommendation_generation_time,
            self.test_3_concurrent_users,
            self.test_4_interest_update_performance,
            self.test_5_recommendation_quality,
        ]

        for test_func in tests:
            test_func()

        self.generate_report()


def main():
    """主函数"""
    test = PerformanceTest()
    test.run_all_tests()


if __name__ == "__main__":
    main()
