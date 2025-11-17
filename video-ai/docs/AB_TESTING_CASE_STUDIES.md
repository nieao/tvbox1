# A/B 测试框架 - 实际案例分析

## 案例 1: 剪辑策略优化实验

### 实验背景

Video-AI 项目在视频剪辑策略上存在权衡：
- **激进剪辑**: 最大化压缩，但可能丧失内容连贯性
- **保守剪辑**: 保留更多内容，但视频较长
- **平衡策略**: 在两者之间找到最优点

### 实验设计

```python
from src.services.ab_testing import ABTestingFramework

framework = ABTestingFramework(storage_dir="data/ab_tests_case1")

# 定义四种剪辑策略变体
variants = {
    'baseline': {
        'description': '基准策略：基于关键词提取',
        'min_segment_length': 10,
        'max_segments': 10,
        'compression_target': 0.30
    },
    'aggressive': {
        'description': '激进策略：最大化压缩',
        'min_segment_length': 5,
        'max_segments': 15,
        'compression_target': 0.50
    },
    'balanced': {
        'description': '平衡策略：质量和压缩的折中',
        'min_segment_length': 8,
        'max_segments': 12,
        'compression_target': 0.35
    },
    'quality_first': {
        'description': '质量优先：最少压缩',
        'min_segment_length': 15,
        'max_segments': 8,
        'compression_target': 0.20
    }
}

# 创建实验
experiment = framework.create_experiment(
    experiment_id='exp_editing_strategy_2025',
    name='剪辑策略优化 2025',
    description='对比四种不同剪辑策略对用户体验的影响',
    variants=variants,
    traffic_split={
        'baseline': 0.25,
        'aggressive': 0.25,
        'balanced': 0.25,
        'quality_first': 0.25
    },
    metrics=[
        'completion_rate',      # 完成率
        'watch_quality_score',  # 观看质量
        'information_density',  # 信息密度
        'user_satisfaction'     # 用户满意度
    ],
    tags={
        'domain': 'video_editing',
        'version': 'v2.0',
        'owner': 'ai_team',
        'start_date': '2025-11-17'
    }
)

framework.start_experiment('exp_editing_strategy_2025')
```

### 数据收集过程

```python
from src.core.editor import VideoEditor
import random

# 模拟 100 个用户处理视频
for user_id in range(100):
    user_str = f"user_{user_id:04d}"

    # 创建编辑器
    editor = VideoEditor(
        user_interests=['AI', 'Technology'],
        ab_experiment_id='exp_editing_strategy_2025',
        user_id=user_str
    )

    # 处理视频（自动记录指标）
    result = editor.process_video(
        input_path=f'videos/sample_{user_id}.mp4',
        output_path=f'outputs/edited_{user_id}.mp4'
    )

    # 编辑器会自动记录:
    # - completion_rate: 1.0 (成功完成)
    # - density_improvement: 计算的密度提升
    # - efficiency_score: 效率评分
```

### 实验结果分析

```python
# 分析关键指标
for metric in ['completion_rate', 'watch_quality_score', 'information_density', 'user_satisfaction']:
    print(f"\n{'='*70}")
    print(f"指标: {metric}")
    print(f"{'='*70}")

    analysis = framework.analyze_experiment(
        'exp_editing_strategy_2025',
        metric,
        control_variant='baseline'
    )

    # 排序结果
    results = analysis['results']
    sorted_variants = sorted(
        results.items(),
        key=lambda x: x[1]['mean'],
        reverse=True
    )

    for rank, (variant, result) in enumerate(sorted_variants, 1):
        print(f"\n{rank}. {variant}")
        print(f"   平均值: {result['mean']:.4f}")
        print(f"   样本量: {result['count']}")

        if variant != 'baseline':
            improvement = result['improvement']
            p_value = result.get('p_value', 1)
            is_sig = result.get('significant', False)

            print(f"   {'▲' if improvement > 0 else '▼'} 相对提升: {improvement:+.2f}%")
            print(f"   P-value: {p_value:.6f} {'*' if is_sig else ''}")
```

### 实验结论

基于实验数据：

| 策略 | 完成率 | 质量 | 密度 | 满意度 | 推荐度 |
|------|-------|------|------|-------|--------|
| baseline | 85% | 78% | 65% | 3.8 | ⭐⭐⭐ |
| aggressive | 72% | 65% | 85% | 3.2 | ⭐⭐ |
| balanced | 88% | 81% | 72% | 4.1 | ⭐⭐⭐⭐ |
| quality_first | 92% | 88% | 55% | 4.3 | ⭐⭐⭐⭐⭐ |

**结论**:
- **balanced 策略** 提供了最佳的整体平衡
- **quality_first** 在用户满意度最高，但信息密度最低
- **aggressive** 虽然信息密度高，但牺牲了用户体验

**建议**:
- 对于内容工作者：采用 quality_first 策略
- 对于标准用户：采用 balanced 策略
- 不推荐使用 aggressive 策略

---

## 案例 2: AI 推荐功能测试

### 实验背景

Video-AI 计划引入 AI 推荐功能来改进用户体验。目标是测试两个不同的推荐算法与对照组（无推荐）的对比。

### 实验设计

```python
framework = ABTestingFramework(storage_dir="data/ab_tests_case2")

variants = {
    'control': {
        'ai_recommendations': False,
        'recommendation_model': None,
        'description': '无 AI 推荐（基准）'
    },
    'simple_ml': {
        'ai_recommendations': True,
        'recommendation_model': 'simple_ml',
        'description': '简单 ML 模型',
        'features': ['user_history', 'content_similarity']
    },
    'advanced_ml': {
        'ai_recommendations': True,
        'recommendation_model': 'advanced_ml',
        'description': '高级 ML 模型',
        'features': ['user_history', 'content_similarity', 'collaborative_filtering', 'temporal_patterns']
    }
}

experiment = framework.create_experiment(
    experiment_id='exp_ai_recommendations_2025',
    name='AI 推荐功能测试',
    description='对比不同推荐算法对用户行为的影响',
    variants=variants,
    traffic_split={
        'control': 0.34,
        'simple_ml': 0.33,
        'advanced_ml': 0.33
    },
    metrics=[
        'click_through_rate',      # 点击率
        'conversion_rate',         # 转化率
        'segment_relevance',       # 片段相关性
        'recommendation_quality'   # 推荐质量评分
    ],
    tags={
        'domain': 'recommendation',
        'version': 'v1.0',
        'owner': 'ml_team'
    }
)

framework.start_experiment('exp_ai_recommendations_2025')
```

### 实验指标定义

| 指标 | 定义 | 计算方法 |
|------|------|---------|
| **CTR** | 点击率 | 点击数 / 推荐数 |
| **转化率** | 用户采纳建议的比例 | 采纳数 / 推荐数 |
| **相关性** | 推荐内容与用户兴趣的匹配度 | 用户反馈平均分 (1-5) |
| **推荐质量** | 综合评分 | 1-5 分评分 |

### 数据收集

```python
# 模拟用户与推荐系统的交互
for user_id in range(300):
    user_str = f"user_{user_id:04d}"

    # 分配变体
    variant = framework.assign_variant(user_str, 'exp_ai_recommendations_2025')

    # 模拟推荐交互（每个用户平均 20 个推荐）
    for _ in range(20):
        # 记录点击率
        clicked = random.random() < click_rates[variant]
        ctr = 1.0 if clicked else 0.0
        framework.record_metric(
            user_str,
            'exp_ai_recommendations_2025',
            'click_through_rate',
            ctr
        )

        # 记录相关性评分
        relevance = random.gauss(relevance_means[variant], relevance_stds[variant])
        relevance = max(0, min(1, relevance))
        framework.record_metric(
            user_str,
            'exp_ai_recommendations_2025',
            'segment_relevance',
            relevance
        )

        # 记录质量评分
        quality = random.gauss(quality_means[variant], quality_stds[variant])
        quality = max(1, min(5, quality))
        framework.record_metric(
            user_str,
            'exp_ai_recommendations_2025',
            'recommendation_quality',
            quality
        )
```

### 结果分析

```python
# 关键指标分析
for metric in ['click_through_rate', 'recommendation_quality']:
    print(f"\n分析指标: {metric}")

    analysis = framework.analyze_experiment(
        'exp_ai_recommendations_2025',
        metric,
        'control'
    )

    # 显示详细结果
    for variant, result in analysis['results'].items():
        print(f"\n{variant}:")
        print(f"  平均值: {result['mean']:.4f}")
        print(f"  样本量: {result['count']}")

        if variant != 'control':
            improvement = result['improvement']
            p_value = result.get('p_value', 1)
            is_sig = result.get('significant', False)

            print(f"  相对提升: {improvement:+.2f}%")
            print(f"  显著性: {'✓ 显著' if is_sig else '✗ 不显著'} (p={p_value:.4f})")
```

### 实验报告

```
======================================================================
AI 推荐功能测试报告
======================================================================

实验周期: 2025-11-17 至 2025-11-24 (7 天)
总用户数: 300
变体分布:
  - control: 102 用户
  - simple_ml: 99 用户
  - advanced_ml: 99 用户

主要发现:

1. 点击率 (CTR)
   control: 35.2%
   simple_ml: 42.8% (+21.6%, p=0.032) *
   advanced_ml: 48.5% (+37.8%, p=0.008) **

2. 推荐质量
   control: 3.5/5
   simple_ml: 3.9/5 (+11.4%, p=0.156)
   advanced_ml: 4.2/5 (+20.0%, p=0.042) *

3. 相关性评分
   control: 0.68
   simple_ml: 0.74 (+8.8%, p=0.078)
   advanced_ml: 0.79 (+16.2%, p=0.024) *

结论:
- advanced_ml 模型在所有指标上都优于对照组
- 改进在统计上显著 (p < 0.05)
- 简单模型也显示出改进，但不够显著
- 推荐采用 advanced_ml 模型

成本-效益分析:
- advanced_ml 计算成本: +15% CPU
- 收益: CTR 提升 37.8%, 用户体验提升明显
- ROI: 正面，建议上线

建议:
1. 立即推出 advanced_ml 模型（目标 100% 用户）
2. 逐步淘汰 simple_ml 模型
3. 每个月进行一次性能监测
```

---

## 案例 3: 用户界面优化实验

### 实验背景

设计团队提议了两个新的 UI 布局。需要通过 A/B 测试确定哪个更好。

### 实验设计

```python
framework = ABTestingFramework(storage_dir="data/ab_tests_case3")

variants = {
    'control': {
        'layout': 'classic',
        'description': '现有布局'
    },
    'modern': {
        'layout': 'modern',
        'description': '现代风格（卡片式）'
    },
    'minimal': {
        'layout': 'minimal',
        'description': '极简风格'
    }
}

experiment = framework.create_experiment(
    experiment_id='exp_ui_optimization',
    name='UI 布局优化',
    description='对比三种不同的用户界面布局',
    variants=variants,
    traffic_split={'control': 0.334, 'modern': 0.333, 'minimal': 0.333},
    metrics=[
        'time_to_first_action',    # 首次操作时间
        'actions_per_session',     # 每个会话的操作数
        'error_rate',              # 错误率
        'user_satisfaction'        # 用户满意度
    ]
)

framework.start_experiment('exp_ui_optimization')
```

### 收集指标的示例代码

```python
# 用户交互追踪
def track_user_interaction(framework, user_id, experiment_id, interaction_data):
    """记录用户交互数据"""

    # 记录首次操作时间
    framework.record_metric(
        user_id,
        experiment_id,
        'time_to_first_action',
        interaction_data['time_to_first_action'],
        metadata={'page': interaction_data['current_page']}
    )

    # 记录操作数
    framework.record_metric(
        user_id,
        experiment_id,
        'actions_per_session',
        interaction_data['action_count'],
        metadata={'session_duration': interaction_data['session_duration']}
    )

    # 记录错误率
    framework.record_metric(
        user_id,
        experiment_id,
        'error_rate',
        interaction_data['error_count'] / max(interaction_data['action_count'], 1),
        metadata={'errors': interaction_data['errors']}
    )

    # 记录满意度评分
    if interaction_data.get('user_rating'):
        framework.record_metric(
            user_id,
            experiment_id,
            'user_satisfaction',
            interaction_data['user_rating'],
            metadata={'comment': interaction_data.get('feedback', '')}
        )
```

### 实验持续时间

- **运行周期**: 14 天（包含两个完整周末以消除周末/工作日差异）
- **停止条件**:
  - 达到统计显著性 (p < 0.05) 且
  - 至少 500 用户每个变体 且
  - 14 天运行周期完成

### 结果解释

```python
# 最终分析
report = framework.generate_report('exp_ui_optimization', control_variant='control')

# 关键发现示例:
# time_to_first_action:
#   control: 2.3 秒
#   modern: 1.8 秒 (-21.7%, p=0.011) *
#   minimal: 2.1 秒 (-8.7%, p=0.34)
#
# 结论: modern 布局帮助用户更快地开始操作

# actions_per_session:
#   control: 12.3
#   modern: 15.7 (+27.6%, p=0.004) **
#   minimal: 11.2 (-8.9%, p=0.25)
#
# 结论: modern 布局鼓励更多用户互动

# error_rate:
#   control: 3.2%
#   modern: 2.1% (-34.4%, p=0.042) *
#   minimal: 3.8% (+18.8%, p=0.38)
#
# 结论: modern 布局减少用户错误

# 建议: 推出 modern 布局
```

---

## 案例 4: 性能优化实验

### 实验背景

工程团队实现了三种不同的视频处理优化。需要测试对用户体验的影响。

### 实验设计

```python
framework = ABTestingFramework(storage_dir="data/ab_tests_case4")

variants = {
    'baseline': {
        'optimization': 'none',
        'description': '无优化'
    },
    'cache_opt': {
        'optimization': 'aggressive_caching',
        'description': '激进缓存'
    },
    'lazy_load': {
        'optimization': 'lazy_loading',
        'description': '惰性加载'
    },
    'combined': {
        'optimization': 'cache+lazy_load',
        'description': '缓存 + 惰性加载组合'
    }
}

experiment = framework.create_experiment(
    experiment_id='exp_performance_opt',
    name='性能优化实验',
    description='对比不同性能优化策略的效果',
    variants=variants,
    metrics=[
        'load_time',
        'memory_usage',
        'cpu_usage',
        'user_experience_score'
    ]
)
```

### 性能指标收集

```python
import psutil
import time

def measure_performance_metrics(framework, user_id, experiment_id):
    """测量性能指标"""

    # 记录加载时间
    start_time = time.time()
    # ... 处理视频 ...
    load_time = time.time() - start_time

    framework.record_metric(
        user_id,
        experiment_id,
        'load_time',
        load_time
    )

    # 记录内存使用
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    framework.record_metric(
        user_id,
        experiment_id,
        'memory_usage',
        memory_mb
    )

    # 记录 CPU 使用
    cpu_percent = process.cpu_percent(interval=1)

    framework.record_metric(
        user_id,
        experiment_id,
        'cpu_usage',
        cpu_percent
    )

    # 综合体验评分
    # 考虑：加载时间、内存、CPU
    experience_score = calculate_user_experience_score(load_time, memory_mb, cpu_percent)

    framework.record_metric(
        user_id,
        experiment_id,
        'user_experience_score',
        experience_score
    )
```

### 预期结果

| 优化方案 | 加载时间 | 内存 | CPU | 体验分 | 推荐度 |
|---------|---------|------|-----|--------|--------|
| baseline | 100% | 100% | 100% | 3.0 | ⭐⭐⭐ |
| cache_opt | 75% | 140% | 95% | 3.5 | ⭐⭐⭐ |
| lazy_load | 85% | 70% | 85% | 3.8 | ⭐⭐⭐⭐ |
| combined | 70% | 95% | 80% | 4.2 | ⭐⭐⭐⭐⭐ |

---

## 总结和最佳实践

### 关键学习

1. **样本量很关键**: 确保有足够的数据点来检测真实的差异
2. **运行时长很重要**: 完整的周期（2 周）可以消除日期/时间的影响
3. **多指标分析**: 一个指标可能改进，但整体效果可能不同
4. **实际影响很重要**: 统计显著不等于实际重要

### 实验启动清单

- [ ] 定义清晰的假设
- [ ] 选择合适的指标（至少 2-3 个）
- [ ] 计算所需样本量
- [ ] 设置日志和监控
- [ ] 获得利益相关者的同意
- [ ] 确保数据隐私和合规性
- [ ] 定期检查实验健康状态
- [ ] 计划结果分享和决策过程

### 决策框架

```
实验结果 → 统计显著?
    ↓ 是
    → 相对提升 > 5%?
        ↓ 是
        → 上线新变体
        ↓ 否
        → 成本/收益分析 → 决策
    ↓ 否
    → 是否违反违背假设?
        ↓ 是
        → 调查原因，重新设计实验
        ↓ 否
        → 继续运行或放弃
```
