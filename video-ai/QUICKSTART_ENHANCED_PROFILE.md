# 增强用户画像系统 - 快速开始指南

## 📦 安装

```bash
# 基本依赖已包含，仅需可视化：
pip install matplotlib
```

## 🚀 最简单的使用方式

### 1. 创建和更新用户画像

```python
from src.models.enhanced_profile import EnhancedProfileManager

# 创建管理器
manager = EnhancedProfileManager()

# 创建用户
manager.create_profile("user_123")

# 记录用户观看视频
manager.update_from_watch_event(
    user_id="user_123",
    video_id="video_456",
    category="Technology",
    tags=["AI", "机器学习"],
    watch_time=1800,  # 30分钟
    watch_percentage=0.9,  # 90%完成
    device="mobile",
    platform="web"
)

# 记录用户交互（点赞、评论等）
manager.update_from_interaction_event(
    user_id="user_123",
    video_id="video_456",
    action="like"  # like, share, comment, save
)
```

### 2. 查看用户画像摘要

```python
# 获取完整的用户画像摘要
summary = manager.get_profile_summary("user_123")

# 打印所有维度
for dimension, values in summary.items():
    print(f"\n{dimension}:")
    if isinstance(values, dict):
        for key, value in values.items():
            print(f"  - {key}: {value}")
    else:
        print(f"  {values}")
```

### 3. 评估用户价值和风险

```python
# 计算流失风险
churn_risk = manager.calculate_churn_risk("user_123")
profile = manager.get_profile("user_123")

print(f"流失风险: {profile.churn_risk:.2f}")
print(f"风险因素: {profile.risk_factors}")

# 计算生命周期价值
ltv = manager.calculate_lifetime_value("user_123")
print(f"生命周期价值: ${profile.estimated_lifetime_value:.2f}")
```

### 4. 获取推荐向量

```python
# 获取用于推荐系统的特征向量
vector = manager.get_personalization_vector("user_123")

# 向量包含31个维度
print(f"推荐向量维度数: {len(vector)}")

# 查看Top 10特征
top_features = sorted(vector.items(), key=lambda x: x[1], reverse=True)[:10]
for feature, value in top_features:
    print(f"{feature}: {value:.3f}")
```

## 📊 可视化用户画像

### 方式1: 运行完整演示

```bash
cd /home/user/tvbox1/video-ai
python examples/profile_analysis_demo.py
```

这会生成：
- 5个示例用户的完整分析
- JSON和文本格式的报告
- 可视化图表

### 方式2: 生成单个用户的雷达图

```python
from examples.profile_visualization import ProfileVisualizer

visualizer = ProfileVisualizer()
# 需要先有用户数据

visualizer.create_radar_chart(
    user_id="user_123",
    save_path="user_123_radar.png"
)
```

### 方式3: 生成综合仪表板

```python
visualizer.create_comprehensive_dashboard(
    user_id="user_123",
    save_path="user_123_dashboard.png"
)
```

## 💡 常见场景

### 场景1: 识别高价值用户

```python
high_value_users = []

for user_id in manager.profiles.keys():
    ltv = manager.calculate_lifetime_value(user_id)
    profile = manager.get_profile(user_id)

    if profile.estimated_lifetime_value > 100:
        high_value_users.append({
            'user_id': user_id,
            'ltv': profile.estimated_lifetime_value,
            'lifecycle': profile.lifecycle_stage.value
        })

# 按价值排序
high_value_users.sort(key=lambda x: x['ltv'], reverse=True)

print("高价值用户:")
for user in high_value_users[:10]:
    print(f"  {user['user_id']}: ${user['ltv']:.0f}")
```

### 场景2: 识别流失风险用户

```python
at_risk_users = []

for user_id in manager.profiles.keys():
    churn_risk = manager.calculate_churn_risk(user_id)
    profile = manager.get_profile(user_id)

    if profile.churn_risk > 0.6:
        at_risk_users.append({
            'user_id': user_id,
            'churn_risk': profile.churn_risk,
            'risk_factors': profile.risk_factors
        })

print("流失风险用户:")
for user in at_risk_users:
    print(f"  {user['user_id']}: {user['churn_risk']:.1%}")
    for factor in user['risk_factors']:
        print(f"    - {factor}")
```

### 场景3: 个性化推荐

```python
def get_recommendations_for_user(user_id):
    """为用户生成个性化推荐"""

    profile = manager.get_profile(user_id)
    vector = manager.get_personalization_vector(user_id)

    recommendations = {
        'content_type': 'educational' if profile.depth_preference > 0.5 else 'casual',
        'content_length': 'long' if profile.attention_span > 30 else 'short',
        'content_diversity': 'diverse' if profile.exploration_rate > 0.4 else 'focused',
        'priority_topics': profile.favorite_topics[:3],
    }

    return recommendations

recs = get_recommendations_for_user("user_123")
print("推荐配置:")
for key, value in recs.items():
    print(f"  {key}: {value}")
```

### 场景4: 用户分层

```python
def segment_users():
    """将用户分成不同的层级"""

    segments = {
        'vip': [],  # 高价值低风险
        'at_risk': [],  # 高价值高风险
        'growth': [],  # 低价值低风险，有增长潜力
        'churn': []  # 低价值高风险
    }

    for user_id in manager.profiles.keys():
        ltv = manager.calculate_lifetime_value(user_id)
        churn_risk = manager.calculate_churn_risk(user_id)
        profile = manager.get_profile(user_id)

        is_high_value = profile.estimated_lifetime_value > 80
        is_high_risk = churn_risk > 0.5

        if is_high_value and not is_high_risk:
            segments['vip'].append(user_id)
        elif is_high_value and is_high_risk:
            segments['at_risk'].append(user_id)
        elif not is_high_value and not is_high_risk:
            segments['growth'].append(user_id)
        else:
            segments['churn'].append(user_id)

    return segments

segments = segment_users()
for segment, users in segments.items():
    print(f"{segment}: {len(users)} 用户")
```

## 📈 了解15+维度

### 核心维度简介

| 维度 | 关键指标 | 含义 | 应用 |
|-----|--------|------|------|
| 观看习惯 | avg_watch_time | 用户观看时长和频率 | 内容推荐 |
| 内容偏好 | interests | 用户喜欢的话题 | 内容选择 |
| 交互行为 | like_rate | 用户的参与程度 | 参与度评估 |
| 设备信息 | primary_device | 主要使用设备 | 适配优化 |
| 时间模式 | peak_hours | 用户活跃时间 | 推送优化 |
| 社交属性 | influence_score | 社交影响力 | KOL识别 |
| 学习曲线 | learning_speed | 学习进度 | 进阶推荐 |
| 注意力模式 | attention_span | 专注度 | 内容调整 |
| 内容深度 | depth_preference | 深度vs浅层 | 难度调整 |
| 多样性需求 | exploration_rate | 探索欲望 | 推荐混合 |
| 反馈质量 | feedback_detail_score | 反馈质量 | 信任度评估 |
| 付费意愿 | premium_probability | 付费潜力 | 转化优化 |
| 流失风险 | churn_risk | 离开概率 | 留存策略 |
| 影响因子 | influence_score | 对他人影响 | 社区建设 |
| 生命周期 | lifecycle_stage | 用户阶段 | 阶段策略 |

### 快速查询特定维度

```python
profile = manager.get_profile("user_123")

# 观看习惯
print(f"平均观看时长: {profile.avg_watch_time}秒")
print(f"完成率: {profile.completion_rate:.1%}")

# 内容偏好
print(f"热门话题: {profile.favorite_topics}")

# 交互行为
print(f"点赞率: {profile.like_rate:.1%}")

# 风险评估
manager.calculate_churn_risk("user_123")
print(f"流失风险: {profile.churn_risk:.2f}")

# 生命周期
print(f"生命周期: {profile.lifecycle_stage.value}")
```

## 🔧 高级用法

### 保存和加载用户画像

```python
# 保存单个用户
manager.save_profile("user_123", "user_123_profile.json")

# 加载用户
profile = manager.load_profile("user_123_profile.json")
```

### 批量操作

```python
# 对所有用户计算流失风险
for user_id in manager.profiles.keys():
    manager.calculate_churn_risk(user_id)

# 对所有用户计算LTV
for user_id in manager.profiles.keys():
    manager.calculate_lifetime_value(user_id)
```

### 自定义分析

```python
# 获取特定条件的用户
def find_users_with_criteria(criteria_func):
    """根据自定义条件查找用户"""
    matching_users = []

    for user_id in manager.profiles.keys():
        profile = manager.get_profile(user_id)
        if criteria_func(profile):
            matching_users.append(user_id)

    return matching_users

# 查找深度学习爱好者
deep_learners = find_users_with_criteria(
    lambda p: p.depth_preference > 0.7 and 'AI' in p.favorite_topics
)

print(f"深度学习爱好者: {len(deep_learners)}")
```

## 📚 了解更多

### 文档位置

- **完整指南**: `/home/user/tvbox1/video-ai/ENHANCED_PROFILE_GUIDE.md`
  - 详细的维度说明
  - 完整的API参考
  - 集成示例
  - 最佳实践

- **交付报告**: `/home/user/tvbox1/video-ai/ENHANCED_PROFILE_DELIVERY.md`
  - 项目总结
  - 文件清单
  - 性能指标

### 代码位置

- **核心实现**: `/home/user/tvbox1/video-ai/src/models/enhanced_profile.py`
- **可视化工具**: `/home/user/tvbox1/video-ai/examples/profile_visualization.py`
- **演示脚本**: `/home/user/tvbox1/video-ai/examples/profile_analysis_demo.py`

## ❓ 常见问题

### Q: 我应该多久更新一次用户画像?
A: 建议：
- 实时更新用户观看和交互事件
- 每日批处理汇总指标
- 每周评估流失风险
- 每月审查生命周期阶段

### Q: 推荐向量的31个维度从哪来?
A: 从15+维标准特征自动生成：
- 基础维度直接转换
- 某些维度衍生多个特征
- 所有特征都归一化到0-1范围

### Q: 如何处理新用户的冷启动?
A: 对于新用户：
- 使用内容热度和流行度推荐
- 收集用户显式反馈(兴趣选择)
- 采用探索性推荐策略
- 快速更新画像维度

### Q: 流失风险的阈值是多少?
A: 建议：
- <0.33: 低风险，正常运营
- 0.33-0.67: 中等风险，监控和适度干预
- >0.67: 高风险，需要重点留存活动

## 🎯 下一步

1. **运行演示**: `python examples/profile_analysis_demo.py`
2. **查看示例输出**: `examples/profile_analysis_results/`
3. **阅读完整指南**: `ENHANCED_PROFILE_GUIDE.md`
4. **集成到您的系统**: 使用API示例进行集成
5. **生成可视化**: 使用可视化工具展示结果

---

**需要帮助?** 查看 `ENHANCED_PROFILE_GUIDE.md` 的"常见问题"部分。
