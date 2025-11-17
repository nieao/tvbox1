# A/B 测试框架完整指南

## 概述

Video-AI 项目集成了一个完整的 A/B 测试框架，用于科学地评估不同策略和功能的效果。该框架支持多变体实验、流量分配、指标收集、统计分析和详细报告生成。

## 核心特性

### 1. 实验管理
- **创建实验**: 定义变体、流量分配和指标
- **生命周期控制**: 支持草稿、运行、暂停、完成等状态
- **数据持久化**: 自动保存和加载实验配置
- **元数据支持**: 为实验添加标签和自定义信息

### 2. 流量分配
- **灵活的流量分配**: 支持任意比例的变体分配
- **用户一致性**: 同一用户始终被分配到同一变体
- **随机种子**: 支持可重现的分配（用于测试）

### 3. 指标收集
- **自动化指标记录**: 简单的 API 记录各种指标
- **元数据记录**: 为每个数据点附加额外信息
- **灵活的指标类型**: 支持任意数值指标

### 4. 统计分析
- **t-test**: 对两个变体的差异进行统计检验
- **ANOVA**: 对多个变体进行方差分析
- **置信区间**: 计算 95% 置信区间
- **相对提升**: 自动计算改进百分比

### 5. 报告生成
- **详细报告**: 包含所有统计指标和分析结果
- **多格式导出**: 支持 JSON 和 CSV 格式
- **摘要信息**: 快速获取实验的关键信息

## 快速开始

### 安装依赖

```bash
pip install numpy scipy
```

### 基础使用

#### 1. 创建实验

```python
from src.services.ab_testing import ABTestingFramework

# 初始化框架
framework = ABTestingFramework(storage_dir="data/ab_tests")

# 定义变体
variants = {
    'control': {'description': '对照组'},
    'variant_a': {'description': '新策略 A'},
    'variant_b': {'description': '新策略 B'}
}

# 创建实验
experiment = framework.create_experiment(
    experiment_id='exp_001',
    name='策略优化实验',
    description='测试不同策略的效果',
    variants=variants,
    traffic_split={'control': 0.34, 'variant_a': 0.33, 'variant_b': 0.33},
    metrics=['completion_rate', 'user_rating', 'watch_time']
)
```

#### 2. 启动实验

```python
# 启动实验
framework.start_experiment('exp_001')

# 可选：暂停实验
# framework.pause_experiment('exp_001')

# 可选：停止实验
# framework.stop_experiment('exp_001')
```

#### 3. 分配用户和记录指标

```python
# 为用户分配变体
variant = framework.assign_variant('user_123', 'exp_001')
print(f"用户被分配到: {variant}")

# 记录指标
framework.record_metric(
    user_id='user_123',
    experiment_id='exp_001',
    metric_name='completion_rate',
    value=0.85,
    metadata={'timestamp': '2025-11-17T10:00:00'}
)

# 记录更多指标
framework.record_metric('user_123', 'exp_001', 'user_rating', 4.5)
framework.record_metric('user_123', 'exp_001', 'watch_time', 300)
```

#### 4. 分析结果

```python
# 分析单个指标
analysis = framework.analyze_experiment(
    experiment_id='exp_001',
    metric_name='completion_rate',
    control_variant='control'
)

# 显示结果
for variant, result in analysis['results'].items():
    print(f"{variant}:")
    print(f"  平均值: {result['mean']:.4f}")
    print(f"  样本量: {result['count']}")

    if variant != 'control':
        print(f"  相对提升: {result['improvement']:+.2f}%")
        print(f"  P-value: {result['p_value']:.6f}")
        print(f"  显著: {'是' if result['significant'] else '否'}")
```

#### 5. 生成报告

```python
# 生成详细报告
report = framework.generate_report('exp_001', control_variant='control')
print(report)

# 导出数据
json_data = framework.export_data('exp_001', output_format='json')
csv_data = framework.export_data('exp_001', output_format='csv')
```

## 与视频编辑器集成

### 集成编辑器

```python
from src.core.editor import VideoEditor

# 创建编辑器实例，启用 A/B 测试
editor = VideoEditor(
    user_interests=['AI', 'Technology'],
    ab_experiment_id='exp_001',  # 实验ID
    user_id='user_123',           # 用户ID
    ab_storage_dir='data/ab_tests'
)

# 处理视频 - 会自动记录指标
result = editor.process_video(
    input_path='input.mp4',
    output_path='output.mp4'
)

# 后续的指标会自动被记录到 A/B 测试框架
```

### 自动记录的指标

编辑器会自动记录以下指标：

| 指标 | 描述 | 范围 |
|------|------|------|
| `completion_rate` | 视频处理完成率 | 0-1 |
| `density_improvement` | 信息密度提升 | ≥0 |
| `efficiency_score` | 处理效率评分 | 0-1 |

## 高级功能

### 多变体对比（ANOVA）

```python
# 对比多个变体
result = framework.compare_variants(
    experiment_id='exp_001',
    metric_name='user_rating',
    variants=['control', 'variant_a', 'variant_b']
)

# 获取 ANOVA 结果
if 'anova' in result['results']:
    anova = result['results']['anova']
    print(f"F 统计量: {anova['f_statistic']:.4f}")
    print(f"P-value: {anova['p_value']:.6f}")
    print(f"显著: {'是' if anova['significant'] else '否'}")
```

### 实验摘要

```python
# 获取实验摘要
summary = framework.get_experiment_summary('exp_001')

print(f"总用户数: {summary['total_users']}")
print(f"变体分布: {summary['variant_distribution']}")
print(f"指标数据: {summary['metrics']}")
```

### 缓存和性能

框架会自动缓存分析结果，提高性能：

```python
# 使用缓存（默认）
analysis = framework.analyze_experiment('exp_001', 'completion_rate', 'control')

# 跳过缓存
analysis = framework.analyze_experiment(
    'exp_001',
    'completion_rate',
    'control',
    use_cache=False  # 禁用缓存
)
```

## 实验设计最佳实践

### 1. 样本量估计

- **一般规则**: 每个变体至少 100-200 个样本
- **复杂指标**: 需要更多样本（500+）
- **在线计算器**: 使用标准的 A/B 测试样本量计算器

### 2. 流量分配

```python
# 对于新功能的初期测试
traffic_split = {
    'control': 0.9,      # 90% 流量用于对照组
    'variant_a': 0.1     # 10% 流量用于测试变体
}

# 对于成熟的对比测试
traffic_split = {
    'control': 0.5,
    'variant_a': 0.5
}
```

### 3. 运行时长

- **最少 1 周**: 捕捉周期性变化
- **避免节假日**: 可能影响用户行为
- **考虑季节性**: 长期趋势变化

### 4. 选择关键指标

```python
# 确保选择的指标是：
# 1. 可测量的（Measurable）
# 2. 业务相关的（Business relevant）
# 3. 可控的（Controllable）

metrics = [
    'completion_rate',      # 用户完成率
    'user_rating',          # 用户评分
    'watch_time',           # 观看时长
    'engagement_score'      # 参与度评分
]
```

## API 参考

### ABTestingFramework

#### 主要方法

| 方法 | 描述 |
|------|------|
| `create_experiment()` | 创建新实验 |
| `start_experiment()` | 启动实验 |
| `pause_experiment()` | 暂停实验 |
| `stop_experiment()` | 停止实验 |
| `assign_variant()` | 为用户分配变体 |
| `record_metric()` | 记录指标 |
| `analyze_experiment()` | 分析实验结果 |
| `compare_variants()` | 多变体对比 |
| `generate_report()` | 生成报告 |
| `export_data()` | 导出数据 |
| `get_experiment_summary()` | 获取摘要 |

### VideoEditorABTesting

#### 方法

| 方法 | 描述 |
|------|------|
| `set_experiment()` | 设置当前实验和用户 |
| `record_metric()` | 记录指标 |
| `get_variant_config()` | 获取变体配置 |

## 示例场景

### 场景 1: 测试新 UI 设计

```python
# 创建实验
framework.create_experiment(
    experiment_id='exp_ui_redesign',
    name='UI 重设计测试',
    description='测试新 UI 对用户体验的影响',
    variants={
        'old_ui': {'style': 'classic'},
        'new_ui': {'style': 'modern'}
    },
    traffic_split={'old_ui': 0.5, 'new_ui': 0.5},
    metrics=['completion_rate', 'time_to_complete', 'user_satisfaction']
)

framework.start_experiment('exp_ui_redesign')

# 记录用户交互数据...
# 最后分析结果
```

### 场景 2: 测试推荐算法

```python
# 创建实验
framework.create_experiment(
    experiment_id='exp_recommendation_algo',
    name='推荐算法优化',
    description='测试不同推荐算法的效果',
    variants={
        'baseline': {'algorithm': 'collaborative_filtering'},
        'ml_v1': {'algorithm': 'simple_ml'},
        'ml_v2': {'algorithm': 'advanced_ml'}
    },
    metrics=['click_through_rate', 'conversion_rate', 'user_satisfaction']
)

framework.start_experiment('exp_recommendation_algo')

# 分析多个指标...
```

### 场景 3: 性能优化对比

```python
# 创建实验
framework.create_experiment(
    experiment_id='exp_performance',
    name='性能优化实验',
    description='对比不同的优化策略',
    variants={
        'control': {'optimization': 'none'},
        'opt_a': {'optimization': 'aggressive_caching'},
        'opt_b': {'optimization': 'lazy_loading'},
        'opt_c': {'optimization': 'combined'}
    },
    metrics=['load_time', 'memory_usage', 'cpu_usage', 'user_experience_score']
)
```

## 故障排查

### 问题 1: 没有数据被记录

```python
# 检查用户是否被分配
variant = framework.user_assignments.get('user_123', {}).get('exp_001')
if not variant:
    print("用户未被分配到实验")
    # 手动分配
    variant = framework.assign_variant('user_123', 'exp_001')
```

### 问题 2: P-value 为 1.0

可能原因：
- 样本量太小（< 30）
- 两个变体的数据分布太相似
- 存在数据记录错误

解决方案：
```python
# 增加样本量
# 检查数据质量
for variant, metrics in framework.metrics_data['exp_001'].items():
    print(f"{variant}: {len(metrics)} 个数据点")
```

### 问题 3: 导入错误

确保依赖已安装：
```bash
pip install numpy scipy
```

## 性能考虑

- **内存**: 框架将数据缓存在内存中，适合中小规模实验
- **分析速度**: 使用缓存可减少重复计算
- **持久化**: 定期导出数据以备份

## 扩展功能

### 自定义指标计算

```python
# 在记录指标时添加元数据
framework.record_metric(
    user_id='user_123',
    experiment_id='exp_001',
    metric_name='custom_score',
    value=0.85,
    metadata={
        'calculation': 'weighted_average',
        'weights': {'factor_a': 0.6, 'factor_b': 0.4},
        'version': 'v2.0'
    }
)
```

### 自定义统计分析

```python
# 扩展框架添加自定义分析
from src.services.ab_testing import ABTestingFramework
import numpy as np

# 实现自定义分析逻辑
def custom_analysis(framework, experiment_id, metric_name):
    data = framework.metrics_data[experiment_id]
    # 自定义分析代码...
    return results
```

## 参考资源

- [A/B Testing 最佳实践](https://www.optimizely.com/experiment-resources/)
- [统计显著性指南](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- [样本量计算器](https://www.evanmiller.org/ab-testing/sample-size.html)

## FAQ

**Q: 一个用户可以被分配到多个实验吗？**
A: 可以。框架支持一个用户同时参与多个实验。

**Q: 如何恢复暂停的实验？**
A: 暂停的实验无法直接恢复。请启动一个新的实验或手动修改状态。

**Q: 实验数据什么时候可以删除？**
A: 建议保留至少 90 天以供审计和分析。

**Q: 支持多少个变体？**
A: 理论上无限制，但建议不超过 5 个以保持统计效力。

## 许可证

A/B 测试框架作为 Video-AI 项目的一部分发布。
