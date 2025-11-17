"""
用户画像可视化工具

使用 matplotlib 生成雷达图展示15+维用户画像
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# 添加源目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'video-ai' / 'src'))

from models.enhanced_profile import EnhancedProfileManager, LifecycleStage


# 设置中文字体
rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'WenQuanYi Micro Hei']
rcParams['axes.unicode_minus'] = False


class ProfileVisualizer:
    """用户画像可视化器"""

    def __init__(self):
        """初始化可视化器"""
        self.manager = EnhancedProfileManager()

    def create_radar_chart(
        self,
        user_id: str,
        save_path: Optional[str] = None,
        figsize: tuple = (14, 14)
    ):
        """
        创建用户画像雷达图

        Args:
            user_id: 用户ID
            save_path: 保存路径
            figsize: 图表大小
        """
        profile = self.manager.get_profile(user_id)
        if not profile:
            print(f"用户 {user_id} 不存在")
            return

        # 定义15个主要维度及其标签
        dimensions = [
            ('参与度', profile.like_rate + profile.comment_rate + profile.share_rate / 3),
            ('观看频率', min(profile.watch_frequency / 2, 1.0)),
            ('完成率', profile.completion_rate),
            ('内容多样性', min(len(profile.favorite_topics) / 10, 1.0)),
            ('交互率', profile.comment_rate),
            ('分享倾向', profile.share_rate),
            ('设备多样性', profile.device_diversity),
            ('活动专注度', 1.0 - (len(profile.peak_hours) / 24 if profile.peak_hours else 0.5)),
            ('社交影响力', profile.social_influence_score),
            ('学习速度', profile.learning_speed),
            ('注意力跨度', min(profile.attention_span / 30, 1.0)),
            ('内容深度偏好', profile.depth_preference),
            ('探索倾向', profile.exploration_rate),
            ('反馈质量', profile.feedback_detail_score),
            ('付费意愿', profile.premium_probability),
        ]

        labels = [d[0] for d in dimensions]
        values = [d[1] for d in dimensions]

        # 确保值在0-1范围内
        values = [max(0, min(1, v)) for v in values]

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]  # 闭合多边形
        angles += angles[:1]

        # 创建图表
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))

        # 绘制数据多边形
        ax.plot(angles, values, 'o-', linewidth=2, label='用户画像', color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=10, weight='bold')

        # 设置径向轴
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=8)
        ax.grid(True, linestyle='--', alpha=0.7)

        # 设置标题
        lifecycle_label = {
            LifecycleStage.NEW: '新用户',
            LifecycleStage.GROWING: '成长中',
            LifecycleStage.MATURE: '成熟用户',
            LifecycleStage.AT_RISK: '高风险',
            LifecycleStage.CHURNED: '已流失',
        }.get(profile.lifecycle_stage, '未知')

        title = (
            f"用户画像分析报告\n"
            f"用户ID: {user_id} | "
            f"生命周期阶段: {lifecycle_label} | "
            f"流失风险: {profile.churn_risk:.1%}"
        )
        plt.title(title, size=14, weight='bold', pad=20)

        plt.tight_layout()

        # 保存
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")

        return fig, ax

    def create_dimension_comparison(
        self,
        user_ids: List[str],
        dimensions: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ):
        """
        创建用户维度对比图

        Args:
            user_ids: 用户ID列表
            dimensions: 要比较的维度
            save_path: 保存路径
        """
        if dimensions is None:
            dimensions = ['参与度', '完成率', '学习速度', '社交影响力', '流失风险']

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, dimension in enumerate(dimensions):
            ax = axes[idx]

            values = []
            labels = []

            for user_id in user_ids:
                profile = self.manager.get_profile(user_id)
                if not profile:
                    continue

                labels.append(user_id)

                # 根据维度获取值
                if dimension == '参与度':
                    val = (profile.like_rate + profile.comment_rate + profile.share_rate) / 3
                elif dimension == '完成率':
                    val = profile.completion_rate
                elif dimension == '学习速度':
                    val = profile.learning_speed
                elif dimension == '社交影响力':
                    val = profile.social_influence_score
                elif dimension == '流失风险':
                    val = profile.churn_risk
                else:
                    val = 0.5

                values.append(val)

            # 绘制柱状图
            colors = ['#2E86AB' if v < 0.5 else '#A23B72' if v < 0.7 else '#F18F01' for v in values]
            ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylim(0, 1)
            ax.set_title(dimension, fontsize=12, weight='bold')
            ax.set_ylabel('得分')
            ax.grid(axis='y', alpha=0.3)

            for i, v in enumerate(values):
                ax.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=9)

        # 隐藏多余的子图
        for idx in range(len(dimensions), len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle('用户维度对比分析', fontsize=14, weight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"对比图已保存到: {save_path}")

        return fig

    def create_lifecycle_distribution(
        self,
        user_ids: List[str],
        save_path: Optional[str] = None
    ):
        """
        创建生命周期分布饼图

        Args:
            user_ids: 用户ID列表
            save_path: 保存路径
        """
        lifecycle_counts = {}

        for user_id in user_ids:
            profile = self.manager.get_profile(user_id)
            if profile:
                stage = profile.lifecycle_stage.value
                lifecycle_counts[stage] = lifecycle_counts.get(stage, 0) + 1

        if not lifecycle_counts:
            print("没有用户数据")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        labels = list(lifecycle_counts.keys())
        sizes = list(lifecycle_counts.values())
        colors = {
            'new': '#2E86AB',
            'growing': '#A23B72',
            'mature': '#F18F01',
            'at_risk': '#C73E1D',
            'churned': '#808080'
        }
        color_list = [colors.get(label, '#999999') for label in labels]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=color_list,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )

        plt.title('用户生命周期分布', fontsize=14, weight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"生命周期分布图已保存到: {save_path}")

        return fig, ax

    def create_risk_profile_chart(
        self,
        user_id: str,
        save_path: Optional[str] = None
    ):
        """
        创建流失风险分析图

        Args:
            user_id: 用户ID
            save_path: 保存路径
        """
        profile = self.manager.get_profile(user_id)
        if not profile:
            print(f"用户 {user_id} 不存在")
            return

        # 计算流失风险得分
        self.manager.calculate_churn_risk(user_id)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 左侧：风险因素
        risk_factors = {
            '最后活跃天数': min(profile.days_since_last_active / 30, 1.0),
            '活动频率衰减': profile.activity_decline,
            '参与度低': 1 - (profile.like_rate + profile.comment_rate + profile.share_rate) / 3,
            '完成率低': 1 - profile.completion_rate,
        }

        factors = list(risk_factors.keys())
        values = list(risk_factors.values())

        colors_risk = ['#2E86AB' if v < 0.33 else '#F18F01' if v < 0.67 else '#C73E1D' for v in values]
        bars = ax1.barh(factors, values, color=colors_risk, alpha=0.7, edgecolor='black')

        ax1.set_xlim(0, 1)
        ax1.set_xlabel('风险程度')
        ax1.set_title('流失风险因素分析', fontsize=12, weight='bold')
        ax1.grid(axis='x', alpha=0.3)

        for i, v in enumerate(values):
            ax1.text(v + 0.02, i, f'{v:.2f}', va='center', fontsize=10, weight='bold')

        # 右侧：整体风险评分
        risk_level = profile.churn_risk
        risk_color = '#2E86AB' if risk_level < 0.33 else '#F18F01' if risk_level < 0.67 else '#C73E1D'

        circle = plt.Circle((0.5, 0.5), 0.3, color=risk_color, alpha=0.7)
        ax2.add_patch(circle)

        ax2.text(0.5, 0.5, f'{risk_level:.1%}', ha='center', va='center',
                fontsize=32, weight='bold', color='white')

        ax2.text(0.5, 0.15, '总体流失风险', ha='center', fontsize=12, weight='bold')

        # 风险等级判断
        if risk_level < 0.33:
            risk_text = "低风险"
            recommend = "保持当前策略"
        elif risk_level < 0.67:
            risk_text = "中等风险"
            recommend = "建议提高内容推荐相关性"
        else:
            risk_text = "高风险"
            recommend = "需要重点关注和激活"

        ax2.text(0.5, 0.05, f"{risk_text} - {recommend}", ha='center', fontsize=10, style='italic')

        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')

        plt.suptitle(f'用户 {user_id} - 流失风险分析', fontsize=14, weight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"风险分析图已保存到: {save_path}")

        return fig

    def create_ltv_analysis(
        self,
        user_ids: List[str],
        save_path: Optional[str] = None
    ):
        """
        创建用户生命周期价值分析

        Args:
            user_ids: 用户ID列表
            save_path: 保存路径
        """
        user_labels = []
        ltv_values = []
        risk_values = []

        for user_id in user_ids:
            profile = self.manager.get_profile(user_id)
            if profile:
                self.manager.calculate_lifetime_value(user_id)
                user_labels.append(user_id[-8:])  # 显示用户ID的后8位
                ltv_values.append(profile.estimated_lifetime_value)
                risk_values.append(profile.churn_risk)

        if not user_labels:
            print("没有用户数据")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # 按LTV值排序
        sorted_data = sorted(zip(user_labels, ltv_values, risk_values), key=lambda x: x[1], reverse=True)
        user_labels, ltv_values, risk_values = zip(*sorted_data)

        # 绘制LTV柱状图
        colors = ['#2E86AB' if r < 0.33 else '#F18F01' if r < 0.67 else '#C73E1D' for r in risk_values]
        bars = ax.bar(range(len(user_labels)), ltv_values, color=colors, alpha=0.7, edgecolor='black')

        # 添加值标签
        for i, (ltv, risk) in enumerate(zip(ltv_values, risk_values)):
            ax.text(i, ltv + 5, f'${ltv:.0f}', ha='center', fontsize=9, weight='bold')

        ax.set_xticks(range(len(user_labels)))
        ax.set_xticklabels(user_labels, rotation=45, ha='right')
        ax.set_ylabel('生命周期价值 (USD)', fontsize=11, weight='bold')
        ax.set_title('用户生命周期价值分析', fontsize=14, weight='bold')
        ax.grid(axis='y', alpha=0.3)

        # 添加图例
        low_risk = mpatches.Patch(color='#2E86AB', label='低风险')
        medium_risk = mpatches.Patch(color='#F18F01', label='中风险')
        high_risk = mpatches.Patch(color='#C73E1D', label='高风险')
        ax.legend(handles=[low_risk, medium_risk, high_risk], loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"LTV分析图已保存到: {save_path}")

        return fig

    def create_comprehensive_dashboard(
        self,
        user_id: str,
        save_path: Optional[str] = None
    ):
        """
        创建用户画像综合仪表板

        Args:
            user_id: 用户ID
            save_path: 保存路径
        """
        profile = self.manager.get_profile(user_id)
        if not profile:
            print(f"用户 {user_id} 不存在")
            return

        self.manager.calculate_churn_risk(user_id)
        self.manager.calculate_lifetime_value(user_id)

        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. 雷达图（占用左上3个位置）
        ax_radar = fig.add_subplot(gs[0:2, 0:2], projection='polar')

        dimensions = [
            ('参与度', (profile.like_rate + profile.comment_rate + profile.share_rate) / 3),
            ('完成率', profile.completion_rate),
            ('学习速度', profile.learning_speed),
            ('社交影响力', profile.social_influence_score),
            ('注意力', min(profile.attention_span / 30, 1.0)),
            ('探索倾向', profile.exploration_rate),
        ]

        labels = [d[0] for d in dimensions]
        values = [max(0, min(1, d[1])) for d in dimensions]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values_plot = values + values[:1]
        angles_plot = angles + angles[:1]

        ax_radar.plot(angles_plot, values_plot, 'o-', linewidth=2, color='#2E86AB')
        ax_radar.fill(angles_plot, values_plot, alpha=0.25, color='#2E86AB')
        ax_radar.set_xticks(angles)
        ax_radar.set_xticklabels(labels, size=9)
        ax_radar.set_ylim(0, 1)
        ax_radar.set_title('核心维度', fontsize=11, weight='bold', pad=10)
        ax_radar.grid(True)

        # 2. 关键指标卡片（右上）
        ax_metrics = fig.add_subplot(gs[0, 2])
        ax_metrics.axis('off')

        metrics_text = (
            f"关键指标\n"
            f"━━━━━━━━━━━\n"
            f"总观看小时: {profile.total_watch_hours:.1f}\n"
            f"观看频率: {profile.watch_frequency:.2f}次/天\n"
            f"生命周期价值: ${profile.estimated_lifetime_value:.0f}\n"
            f"专长领域: {len(profile.expertise_areas)}\n"
        )

        ax_metrics.text(0.1, 0.95, metrics_text, transform=ax_metrics.transAxes,
                       fontsize=10, verticalalignment='top', family='monospace',
                       bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.8))

        # 3. 生命周期信息（中右）
        ax_lifecycle = fig.add_subplot(gs[1, 2])
        ax_lifecycle.axis('off')

        lifecycle_label = {
            LifecycleStage.NEW: '新用户',
            LifecycleStage.GROWING: '成长中',
            LifecycleStage.MATURE: '成熟用户',
            LifecycleStage.AT_RISK: '高风险',
            LifecycleStage.CHURNED: '已流失',
        }.get(profile.lifecycle_stage, '未知')

        lifecycle_text = (
            f"生命周期\n"
            f"━━━━━━━━━━━\n"
            f"当前阶段: {lifecycle_label}\n"
            f"注册天数: {profile.days_since_signup}\n"
            f"最后活跃: {profile.days_since_last_active}天前\n"
            f"流失风险: {profile.churn_risk:.1%}\n"
        )

        risk_color = '#E8F4F8' if profile.churn_risk < 0.33 else '#FFF3E0' if profile.churn_risk < 0.67 else '#FFEBEE'
        ax_lifecycle.text(0.1, 0.95, lifecycle_text, transform=ax_lifecycle.transAxes,
                         fontsize=10, verticalalignment='top', family='monospace',
                         bbox=dict(boxstyle='round', facecolor=risk_color, alpha=0.8))

        # 4. 内容偏好（下左）
        ax_content = fig.add_subplot(gs[2, 0])

        if profile.favorite_topics:
            topics = profile.favorite_topics[:5]
            interests_vals = [profile.interests.get(t, 0) for t in topics]
            colors_content = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#808080']
            ax_content.barh(topics, interests_vals, color=colors_content[:len(topics)], alpha=0.7)
            ax_content.set_xlabel('兴趣权重')
            ax_content.set_title('热门兴趣标签', fontsize=11, weight='bold')
            ax_content.grid(axis='x', alpha=0.3)

        # 5. 交互行为（下中）
        ax_interaction = fig.add_subplot(gs[2, 1])

        interaction_types = ['点赞', '分享', '评论', '保存']
        interaction_rates = [
            profile.like_rate,
            profile.share_rate,
            profile.comment_rate,
            profile.save_rate
        ]
        colors_interaction = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        bars = ax_interaction.bar(interaction_types, interaction_rates, color=colors_interaction, alpha=0.7, edgecolor='black')

        ax_interaction.set_ylim(0, max(interaction_rates) * 1.2 if max(interaction_rates) > 0 else 0.5)
        ax_interaction.set_title('交互行为分布', fontsize=11, weight='bold')
        ax_interaction.set_ylabel('交互率')
        ax_interaction.grid(axis='y', alpha=0.3)

        for bar, rate in zip(bars, interaction_rates):
            height = bar.get_height()
            ax_interaction.text(bar.get_x() + bar.get_width()/2., height,
                              f'{rate:.1%}', ha='center', va='bottom', fontsize=9)

        # 6. 设备信息（下右）
        ax_device = fig.add_subplot(gs[2, 2])
        ax_device.axis('off')

        device_text = (
            f"设备与平台\n"
            f"━━━━━━━━━━━\n"
            f"主要设备: {profile.primary_device}\n"
            f"主要平台: {profile.primary_platform}\n"
            f"设备多样性: {profile.device_diversity:.2f}\n"
            f"活跃时段: {profile.active_period}\n"
        )

        ax_device.text(0.1, 0.95, device_text, transform=ax_device.transAxes,
                      fontsize=10, verticalalignment='top', family='monospace',
                      bbox=dict(boxstyle='round', facecolor='#F0F4F8', alpha=0.8))

        plt.suptitle(f'用户画像综合分析仪表板 - {user_id}', fontsize=16, weight='bold')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"仪表板已保存到: {save_path}")

        return fig


def main():
    """演示可视化功能"""
    print("=" * 60)
    print("用户画像可视化工具演示")
    print("=" * 60)

    visualizer = ProfileVisualizer()

    # 创建示例数据
    print("\n创建示例用户数据...")
    manager = visualizer.manager

    # 用户1：高参与度用户
    manager.create_profile("user_001")
    for i in range(20):
        manager.update_from_watch_event(
            user_id="user_001",
            video_id=f"video_{i}",
            category="Technology" if i % 2 == 0 else "Education",
            tags=["AI", "机器学习"] if i % 2 == 0 else ["编程", "Python"],
            watch_time=1800 + i * 100,
            watch_percentage=0.85 + (i % 3) * 0.05,
            device="mobile" if i % 2 == 0 else "desktop",
            platform="web"
        )
        manager.update_from_interaction_event(
            user_id="user_001",
            video_id=f"video_{i}",
            action="like" if i % 3 == 0 else "comment" if i % 3 == 1 else "share"
        )

    # 用户2：低参与度用户
    manager.create_profile("user_002")
    for i in range(10):
        manager.update_from_watch_event(
            user_id="user_002",
            video_id=f"video_{i}",
            category="Entertainment",
            tags=["娱乐", "搞笑"],
            watch_time=300 + i * 50,
            watch_percentage=0.4 + (i % 2) * 0.1,
            device="mobile",
            platform="web"
        )

    # 用户3：成长中的用户
    manager.create_profile("user_003")
    for i in range(15):
        manager.update_from_watch_event(
            user_id="user_003",
            video_id=f"video_{i}",
            category="Education",
            tags=["学习", "知识"],
            watch_time=1200 + i * 150,
            watch_percentage=0.75 + (i % 4) * 0.05,
            device="tablet" if i % 2 == 0 else "mobile",
            platform="web"
        )
        if i % 2 == 0:
            manager.update_from_interaction_event(
                user_id="user_003",
                video_id=f"video_{i}",
                action="save"
            )

    print(f"✓ 已创建3个示例用户")

    # 创建输出目录
    output_dir = Path("/home/user/tvbox1/video-ai/examples/profile_visualizations")
    output_dir.mkdir(exist_ok=True)

    print("\n生成可视化图表...")

    # 1. 单用户雷达图
    visualizer.create_radar_chart(
        "user_001",
        save_path=output_dir / "radar_chart_user001.png"
    )

    # 2. 综合仪表板
    visualizer.create_comprehensive_dashboard(
        "user_001",
        save_path=output_dir / "dashboard_user001.png"
    )

    # 3. 流失风险分析
    visualizer.create_risk_profile_chart(
        "user_002",
        save_path=output_dir / "risk_analysis_user002.png"
    )

    # 4. 维度对比
    visualizer.create_dimension_comparison(
        ["user_001", "user_002", "user_003"],
        save_path=output_dir / "dimension_comparison.png"
    )

    # 5. 生命周期分布
    visualizer.create_lifecycle_distribution(
        ["user_001", "user_002", "user_003"],
        save_path=output_dir / "lifecycle_distribution.png"
    )

    # 6. LTV分析
    visualizer.create_ltv_analysis(
        ["user_001", "user_002", "user_003"],
        save_path=output_dir / "ltv_analysis.png"
    )

    print("\n✓ 所有图表已生成")
    print(f"输出目录: {output_dir}")

    print("\n用户画像统计:")
    for user_id in ["user_001", "user_002", "user_003"]:
        summary = manager.get_profile_summary(user_id)
        print(f"\n{user_id}:")
        print(f"  - 参与度: {(summary['交互行为']['点赞率'])}")
        print(f"  - 完成率: {(summary['观看习惯']['完成率'])}")
        print(f"  - 学习速度: {(summary['学习曲线']['学习速度'])}")
        print(f"  - 生命周期: {(summary['生命周期']['当前阶段'])}")

    # 显示图表
    plt.show()


if __name__ == "__main__":
    main()
