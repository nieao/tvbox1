"""
增强用户画像系统演示脚本

展示15+维用户画像的完整功能:
- 用户画像构建
- 多维度特征提取
- 个性化推荐向量生成
- 流失风险预测
- 生命周期价值评估
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import List, Dict

# 添加源目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'video-ai' / 'src'))

from models.enhanced_profile import (
    EnhancedProfileManager,
    LifecycleStage,
)


class ProfileAnalysisDemo:
    """用户画像分析演示"""

    def __init__(self):
        """初始化演示"""
        self.manager = EnhancedProfileManager()
        self.demo_users = []

    def create_sample_users(self):
        """创建示例用户数据"""
        print("\n" + "=" * 70)
        print("创建示例用户数据")
        print("=" * 70)

        # 用户1: 高度活跃的高价值用户
        user_id = "user_high_value_001"
        self._create_active_user(user_id, "高价值用户", 30)
        self.demo_users.append(user_id)

        # 用户2: 新注册用户
        user_id = "user_new_002"
        self._create_new_user(user_id, "新用户", 2)
        self.demo_users.append(user_id)

        # 用户3: 流失风险用户
        user_id = "user_at_risk_003"
        self._create_at_risk_user(user_id, "高风险用户", 45)
        self.demo_users.append(user_id)

        # 用户4: 成长中用户
        user_id = "user_growing_004"
        self._create_growing_user(user_id, "成长中用户", 15)
        self.demo_users.append(user_id)

        # 用户5: 学习型用户
        user_id = "user_learning_005"
        self._create_learning_user(user_id, "学习型用户", 25)
        self.demo_users.append(user_id)

        print(f"✓ 已创建 {len(self.demo_users)} 个示例用户")

    def _create_active_user(self, user_id: str, description: str, days_active: int):
        """创建活跃用户"""
        print(f"\n  创建 {description} ({user_id})...")
        self.manager.create_profile(user_id)

        # 模拟持续的观看行为
        for day in range(days_active):
            timestamp = datetime.now() - timedelta(days=days_active - day)

            # 每天2-3个观看事件
            for i in range(2 + day % 2):
                category = ["Technology", "Business", "Education"][i % 3]
                tags = {
                    "Technology": ["AI", "深度学习", "机器学习"],
                    "Business": ["创业", "管理", "营销"],
                    "Education": ["在线教育", "编程教程"]
                }[category]

                self.manager.update_from_watch_event(
                    user_id=user_id,
                    video_id=f"video_{day}_{i}",
                    category=category,
                    tags=tags,
                    watch_time=1800 + (day % 10) * 100,  # 30-60分钟
                    watch_percentage=0.85 + (day % 3) * 0.05,  # 85-95%
                    device="mobile" if day % 2 == 0 else "desktop",
                    platform="web",
                    timestamp=timestamp
                )

            # 每3天一个交互
            if day % 3 == 0:
                actions = ["like", "comment", "share"]
                action = actions[day % 3]
                self.manager.update_from_interaction_event(
                    user_id=user_id,
                    video_id=f"video_{day}_0",
                    action=action,
                    details={"comment_text": "很有启发的内容！" * (5 if action == "comment" else 1)}
                    if action == "comment" else {},
                    timestamp=timestamp
                )

    def _create_new_user(self, user_id: str, description: str, days_active: int):
        """创建新用户"""
        print(f"\n  创建 {description} ({user_id})...")
        self.manager.create_profile(user_id)

        # 新用户只有少量浏览
        for day in range(days_active):
            timestamp = datetime.now() - timedelta(days=days_active - day)

            # 只在某些日期观看
            if day % 2 == 0:
                self.manager.update_from_watch_event(
                    user_id=user_id,
                    video_id=f"video_{day}",
                    category="Technology",
                    tags=["入门", "教程"],
                    watch_time=900,  # 15分钟
                    watch_percentage=0.6,  # 60%完成
                    device="mobile",
                    platform="web",
                    timestamp=timestamp
                )

    def _create_at_risk_user(self, user_id: str, description: str, days_active: int):
        """创建流失风险用户"""
        print(f"\n  创建 {description} ({user_id})...")
        self.manager.create_profile(user_id)

        # 初期活跃，然后衰退
        active_days = 15

        for day in range(active_days):
            timestamp = datetime.now() - timedelta(days=days_active - day)
            self.manager.update_from_watch_event(
                user_id=user_id,
                video_id=f"video_{day}",
                category="Entertainment",
                tags=["娱乐", "短视频"],
                watch_time=600 - (day * 30),  # 逐日递减
                watch_percentage=0.7 - (day * 0.02),  # 逐日递减
                device="mobile",
                platform="web",
                timestamp=timestamp
            )

    def _create_growing_user(self, user_id: str, description: str, days_active: int):
        """创建成长中用户"""
        print(f"\n  创建 {description} ({user_id})...")
        self.manager.create_profile(user_id)

        # 逐步增加活跃度
        for day in range(days_active):
            timestamp = datetime.now() - timedelta(days=days_active - day)

            watch_count = 1 + (day // 5)  # 每5天增加一个观看

            for i in range(watch_count):
                self.manager.update_from_watch_event(
                    user_id=user_id,
                    video_id=f"video_{day}_{i}",
                    category="Education",
                    tags=["学习", "知识", "成长"],
                    watch_time=1200 + (day * 50),  # 逐日增加
                    watch_percentage=0.7 + (day % 3) * 0.1,
                    device="tablet" if i % 2 == 0 else "mobile",
                    platform="web",
                    timestamp=timestamp
                )

                # 定期保存内容
                if day % 4 == 0:
                    self.manager.update_from_interaction_event(
                        user_id=user_id,
                        video_id=f"video_{day}_{i}",
                        action="save",
                        timestamp=timestamp
                    )

    def _create_learning_user(self, user_id: str, description: str, days_active: int):
        """创建学习型用户"""
        print(f"\n  创建 {description} ({user_id})...")
        self.manager.create_profile(user_id)

        # 深度学习内容
        topics = ["数据科学", "深度学习", "算法设计", "系统设计"]
        topic_idx = 0

        for day in range(days_active):
            timestamp = datetime.now() - timedelta(days=days_active - day)

            if day % 3 == 0:  # 每3天切换话题
                topic_idx = (topic_idx + 1) % len(topics)

            category = "Education"
            tags = [topics[topic_idx], "深度", "详细教程"]

            self.manager.update_from_watch_event(
                user_id=user_id,
                video_id=f"video_{day}",
                category=category,
                tags=tags,
                watch_time=2400 + (day % 5) * 300,  # 40-65分钟
                watch_percentage=0.9 + (day % 2) * 0.05,  # 90-95%
                device="desktop",  # 学习用户多用桌面
                platform="web",
                timestamp=timestamp
            )

            # 活跃交互
            if day % 2 == 0:
                self.manager.update_from_interaction_event(
                    user_id=user_id,
                    video_id=f"video_{day}",
                    action="comment",
                    details={
                        "comment_text": "这个讲解非常清楚！我对%s有了更深的理解。建议加入更多的实战项目。" % topics[topic_idx]
                    },
                    timestamp=timestamp
                )

    def analyze_profile_dimensions(self):
        """分析用户画像的15+维度"""
        print("\n" + "=" * 70)
        print("用户画像15+维度分析")
        print("=" * 70)

        for user_id in self.demo_users:
            profile = self.manager.get_profile(user_id)
            summary = self.manager.get_profile_summary(user_id)

            print(f"\n{'='*70}")
            print(f"用户: {user_id}")
            print(f"{'='*70}")

            # 维度1: 观看习惯
            print("\n1️⃣ 观看习惯")
            print(f"   平均观看时长: {profile.avg_watch_time:.0f}秒")
            print(f"   观看频率: {profile.watch_frequency:.2f}次/天")
            print(f"   完成率: {profile.completion_rate:.1%}")
            print(f"   总观看小时数: {profile.total_watch_hours:.1f}小时")

            # 维度2: 内容偏好
            print("\n2️⃣ 内容偏好")
            print(f"   热门话题: {', '.join(profile.favorite_topics[:3])}")
            print(f"   兴趣标签数: {len(profile.interests)}")

            # 维度3: 交互行为
            print("\n3️⃣ 交互行为")
            print(f"   点赞率: {profile.like_rate:.1%}")
            print(f"   分享率: {profile.share_rate:.1%}")
            print(f"   评论率: {profile.comment_rate:.1%}")
            print(f"   保存率: {profile.save_rate:.1%}")
            print(f"   总交互数: {profile.total_interactions}")

            # 维度4: 设备信息
            print("\n4️⃣ 设备信息")
            print(f"   主要设备: {profile.primary_device}")
            print(f"   主要平台: {profile.primary_platform}")
            print(f"   设备多样性: {profile.device_diversity:.2f}")

            # 维度5: 时间模式
            print("\n5️⃣ 时间模式")
            print(f"   高峰小时: {profile.peak_hours}")
            print(f"   活跃时段: {profile.active_period}")
            print(f"   周末使用率: {profile.weekend_usage:.1%}")

            # 维度6: 社交属性
            print("\n6️⃣ 社交属性")
            print(f"   社交影响力: {profile.social_influence_score:.2f}")
            print(f"   分享频率: {profile.share_frequency:.2f}")
            print(f"   粉丝数: {profile.follower_count}")

            # 维度7: 学习曲线
            print("\n7️⃣ 学习曲线")
            print(f"   学习速度: {profile.learning_speed:.2f}")
            print(f"   专长领域: {', '.join(profile.expertise_areas[:3]) if profile.expertise_areas else '未确定'}")

            # 维度8: 注意力模式
            print("\n8️⃣ 注意力模式")
            print(f"   注意力跨度: {profile.attention_span:.1f}分钟")
            print(f"   跳过率: {profile.skip_rate:.1%}")
            print(f"   重看率: {profile.rewatch_rate:.1%}")

            # 维度9: 内容深度
            print("\n9️⃣ 内容深度")
            print(f"   深度偏好: {profile.depth_preference:.2f} (0=浅层, 1=深度)")
            print(f"   复杂度容受度: {profile.complexity_tolerance:.2f}")

            # 维度10: 多样性需求
            print("\n🔟 多样性需求")
            print(f"   探索率: {profile.exploration_rate:.1%}")
            print(f"   利用率: {profile.exploitation_rate:.1%}")

            # 维度11-15: 其他指标
            print("\n1️⃣1️⃣ 反馈质量")
            print(f"   反馈数量: {profile.feedback_count}")
            print(f"   反馈详细度: {profile.feedback_detail_score:.2f}")

            print("\n1️⃣2️⃣ 付费意愿")
            print(f"   付费概率: {profile.premium_probability:.1%}")
            self.manager.calculate_lifetime_value(user_id)
            print(f"   生命周期价值: ${profile.estimated_lifetime_value:.2f}")

            print("\n1️⃣3️⃣ 流失风险")
            self.manager.calculate_churn_risk(user_id)
            print(f"   风险评分: {profile.churn_risk:.2f}")
            print(f"   最后活跃: {profile.days_since_last_active}天前")
            print(f"   风险因素: {', '.join(profile.risk_factors) if profile.risk_factors else '无'}")

            print("\n1️⃣4️⃣ 影响因子")
            print(f"   内容创作者: {'是' if profile.content_creator else '否'}")
            print(f"   社区贡献度: {profile.community_contribution:.2f}")
            print(f"   影响力评分: {profile.influence_score:.2f}")

            print("\n1️⃣5️⃣ 生命周期阶段")
            print(f"   当前阶段: {profile.lifecycle_stage.value}")
            print(f"   注册天数: {profile.days_since_signup}")

    def generate_recommendation_vectors(self):
        """生成个性化推荐向量"""
        print("\n" + "=" * 70)
        print("个性化推荐向量生成")
        print("=" * 70)

        for user_id in self.demo_users:
            vector = self.manager.get_personalization_vector(user_id)

            print(f"\n用户: {user_id}")
            print(f"推荐向量维度数: {len(vector)}")

            # 按重要性排序
            sorted_vector = sorted(vector.items(), key=lambda x: x[1], reverse=True)

            print("\n  Top 10 特征:")
            for i, (key, value) in enumerate(sorted_vector[:10], 1):
                print(f"    {i}. {key}: {value:.3f}")

    def generate_analysis_report(self):
        """生成分析报告"""
        print("\n" + "=" * 70)
        print("用户群体分析报告")
        print("=" * 70)

        # 统计聚合数据
        total_users = len(self.demo_users)
        total_watch_hours = 0
        total_interactions = 0
        lifecycle_distribution = {}
        risk_distribution = {"低": 0, "中": 0, "高": 0}

        for user_id in self.demo_users:
            profile = self.manager.get_profile(user_id)
            total_watch_hours += profile.total_watch_hours
            total_interactions += profile.total_interactions

            # 生命周期分布
            stage = profile.lifecycle_stage.value
            lifecycle_distribution[stage] = lifecycle_distribution.get(stage, 0) + 1

            # 流失风险分布
            churn_risk = self.manager.calculate_churn_risk(user_id)
            if churn_risk < 0.33:
                risk_distribution["低"] += 1
            elif churn_risk < 0.67:
                risk_distribution["中"] += 1
            else:
                risk_distribution["高"] += 1

        print(f"\n用户群体统计:")
        print(f"  总用户数: {total_users}")
        print(f"  总观看小时数: {total_watch_hours:.1f}")
        print(f"  总交互数: {total_interactions}")
        print(f"  平均观看小时数: {total_watch_hours / total_users:.1f}")
        print(f"  平均交互数: {total_interactions / total_users:.1f}")

        print(f"\n生命周期分布:")
        for stage, count in sorted(lifecycle_distribution.items()):
            percentage = (count / total_users) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {stage:8s}: {count:2d} 用户 {bar:20s} {percentage:.1f}%")

        print(f"\n流失风险分布:")
        for risk_level, count in sorted(risk_distribution.items()):
            percentage = (count / total_users) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {risk_level:2s}: {count:2d} 用户 {bar:20s} {percentage:.1f}%")

        print(f"\n参与度分析:")
        engagement_scores = [
            (profile.like_rate + profile.comment_rate + profile.share_rate) / 3
            for profile in [self.manager.get_profile(uid) for uid in self.demo_users]
        ]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        print(f"  平均参与度: {avg_engagement:.1%}")

        # 识别高价值用户
        print(f"\n高价值用户识别:")
        ltv_list = []
        for user_id in self.demo_users:
            profile = self.manager.get_profile(user_id)
            ltv = self.manager.calculate_lifetime_value(user_id)
            ltv_list.append((user_id, ltv, profile.churn_risk))

        ltv_list.sort(key=lambda x: x[1], reverse=True)
        for i, (user_id, ltv, risk) in enumerate(ltv_list[:3], 1):
            risk_label = "低风险" if risk < 0.33 else "中风险" if risk < 0.67 else "高风险"
            print(f"  {i}. {user_id}: LTV=${ltv:.0f}, {risk_label}")

        # 识别需要留存的用户
        print(f"\n留存关键用户 (高风险高价值):")
        at_risk_high_value = [
            (user_id, ltv, risk) for user_id, ltv, risk in ltv_list
            if risk > 0.5 and ltv > 100
        ]
        if at_risk_high_value:
            for i, (user_id, ltv, risk) in enumerate(at_risk_high_value[:3], 1):
                print(f"  {i}. {user_id}: LTV=${ltv:.0f}, 风险={risk:.1%}")
        else:
            print("  暂无高风险高价值用户")

    def export_analysis_results(self):
        """导出分析结果"""
        print("\n" + "=" * 70)
        print("导出分析结果")
        print("=" * 70)

        output_dir = Path("/home/user/tvbox1/video-ai/examples/profile_analysis_results")
        output_dir.mkdir(exist_ok=True)

        # 导出用户画像汇总
        results = {
            "analysis_date": datetime.now().isoformat(),
            "users": {}
        }

        for user_id in self.demo_users:
            profile = self.manager.get_profile(user_id)
            self.manager.calculate_churn_risk(user_id)
            self.manager.calculate_lifetime_value(user_id)

            results["users"][user_id] = {
                "基本信息": {
                    "user_id": user_id,
                    "生命周期": profile.lifecycle_stage.value,
                    "注册天数": profile.days_since_signup,
                },
                "观看习惯": {
                    "平均观看时长": f"{profile.avg_watch_time:.0f}秒",
                    "观看频率": f"{profile.watch_frequency:.2f}次/天",
                    "完成率": f"{profile.completion_rate:.1%}",
                    "总观看小时": f"{profile.total_watch_hours:.1f}",
                },
                "交互指标": {
                    "点赞率": f"{profile.like_rate:.1%}",
                    "分享率": f"{profile.share_rate:.1%}",
                    "评论率": f"{profile.comment_rate:.1%}",
                    "总交互数": profile.total_interactions,
                },
                "风险评估": {
                    "流失风险": f"{profile.churn_risk:.2f}",
                    "风险因素": profile.risk_factors,
                },
                "价值评估": {
                    "生命周期价值": f"${profile.estimated_lifetime_value:.0f}",
                    "付费概率": f"{profile.premium_probability:.1%}",
                },
            }

        # 保存为JSON
        json_path = output_dir / "profile_analysis_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"✓ 分析结果已导出: {json_path}")

        # 保存为文本报告
        report_path = output_dir / "profile_analysis_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("用户画像分析详细报告\n")
            f.write("=" * 70 + "\n")
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for user_id in self.demo_users:
                profile = self.manager.get_profile(user_id)
                f.write(f"\n{'='*70}\n")
                f.write(f"用户: {user_id}\n")
                f.write(f"{'='*70}\n")

                summary = self.manager.get_profile_summary(user_id)

                for dimension, values in summary.items():
                    f.write(f"\n{dimension}:\n")
                    if isinstance(values, dict):
                        for key, value in values.items():
                            f.write(f"  - {key}: {value}\n")
                    else:
                        f.write(f"  {values}\n")

        print(f"✓ 详细报告已保存: {report_path}")

        return json_path, report_path

    def run_full_demo(self):
        """运行完整演示"""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  增强用户画像系统 (15+维度) - 完整演示".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝")

        # 第一步: 创建示例用户
        self.create_sample_users()

        # 第二步: 分析画像维度
        self.analyze_profile_dimensions()

        # 第三步: 生成推荐向量
        self.generate_recommendation_vectors()

        # 第四步: 生成分析报告
        self.generate_analysis_report()

        # 第五步: 导出结果
        json_path, report_path = self.export_analysis_results()

        # 总结
        print("\n" + "=" * 70)
        print("演示完成总结")
        print("=" * 70)
        print(f"""
✓ 成功创建 {len(self.demo_users)} 个示例用户
✓ 分析了 15+ 维用户画像
✓ 生成了个性化推荐向量
✓ 评估了用户生命周期价值
✓ 预测了流失风险

📊 输出文件:
  - JSON结果: {json_path}
  - 文本报告: {report_path}

🎯 下一步:
  1. 使用可视化工具查看雷达图
  2. 整合推荐系统进行个性化推荐
  3. 建立留存策略和激活计划
        """)


def main():
    """主入口"""
    demo = ProfileAnalysisDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()
