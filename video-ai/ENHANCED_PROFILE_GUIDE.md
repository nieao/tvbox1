# 增强用户画像系统使用指南

## 目录
1. [系统概述](#系统概述)
2. [15+维用户画像维度详解](#15维用户画像维度详解)
3. [API参考](#api参考)
4. [集成示例](#集成示例)
5. [应用场景](#应用场景)
6. [最佳实践](#最佳实践)

---

## 系统概述

### 什么是增强用户画像系统？

增强用户画像系统是一个综合的用户特征建模框架，从原始的7维扩展到15+维，实现对用户行为、偏好、价值和风险的全面评估。

### 核心特性

- **多维特征建模**: 从观看习惯到生命周期阶段的全面覆盖
- **实时更新**: 随着用户行为动态更新画像
- **个性化向量**: 为推荐系统生成优化的特征向量
- **风险预测**: 基于多因素的流失风险评估
- **价值评估**: 生命周期价值(LTV)计算
- **可视化展示**: 生成雷达图、仪表板等多种可视化形式

### 架构

```
┌─────────────────────────────────┐
│      用户行为事件流              │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   EnhancedProfileManager        │
│  (增强画像管理器)                │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐┌────────┐┌─────────┐
│ 观看   ││ 交互   ││ 设备/时间│
│ 习惯   ││ 行为   ││ 模式    │
└────────┘└────────┘└─────────┘
    │          │          │
    └──────────┼──────────┘
               ▼
    ┌──────────────────────┐
    │  EnhancedUserProfile  │
    │  (15+维用户画像)      │
    └──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐┌────────┐┌─────────┐
│推荐向量││风险评分││ 价值评估 │
│生成    ││计算    ││ 预测    │
└────────┘└────────┘└─────────┘
```

---

## 15维用户画像维度详解

### 维度1: 观看习惯 (Watching Habits)

**包含指标**:
- `avg_watch_time`: 平均观看时长(秒)
- `watch_frequency`: 观看频率(次/天)
- `completion_rate`: 完成率(0-1)
- `total_watch_hours`: 总观看小时数

**含义**: 描述用户的基础观看行为模式

**应用**:
- 内容时长建议
- 用户活跃度评估
- 内容消费量预测

```python
profile = manager.get_profile("user_001")
print(f"平均观看时长: {profile.avg_watch_time}秒")
print(f"观看频率: {profile.watch_frequency}次/天")
print(f"完成率: {profile.completion_rate:.1%}")
```

### 维度2: 内容偏好 (Content Preferences)

**包含指标**:
- `interests`: 标签权重映射
- `favorite_topics`: 热门话题列表
- `disliked_topics`: 不喜欢的话题
- `content_preferences`: 分类偏好详情

**含义**: 用户对不同内容的兴趣倾向

**应用**:
- 个性化内容推荐
- 内容分类策略
- 话题聚焦

### 维度3: 交互行为 (Interaction Behavior)

**包含指标**:
- `like_rate`: 点赞率(0-1)
- `share_rate`: 分享率(0-1)
- `comment_rate`: 评论率(0-1)
- `save_rate`: 保存率(0-1)
- `total_interactions`: 总交互数

**含义**: 用户对内容的反馈强度

**应用**:
- 参与度评估
- 社区活跃度指标
- 内容质量反馈

```python
engagement = (profile.like_rate + profile.comment_rate +
              profile.share_rate) / 3
print(f"平均参与度: {engagement:.1%}")
```

### 维度4: 设备信息 (Device Information)

**包含指标**:
- `primary_device`: 主要设备类型(mobile/desktop/tablet)
- `primary_platform`: 主要平台(web/ios/android)
- `device_diversity`: 设备多样性指数(0-1)
- `devices_used`: 设备统计

**含义**: 用户的设备使用习惯和多样性

**应用**:
- 跨设备内容同步
- 适配性建议
- 设备特定推荐

### 维度5: 时间模式 (Temporal Patterns)

**包含指标**:
- `peak_hours`: 高峰小时列表(0-23)
- `weekend_usage`: 周末使用率
- `weekday_usage`: 工作日使用率
- `active_period`: 活跃时段(morning/afternoon/evening/night)

**含义**: 用户的活跃时间规律

**应用**:
- 内容投放时间优化
- 通知推送时间选择
- 服务可用性规划

```python
print(f"高峰时段: {profile.peak_hours}")
print(f"活跃周期: {profile.active_period}")
print(f"周末使用率: {profile.weekend_usage:.1%}")
```

### 维度6: 社交属性 (Social Attributes)

**包含指标**:
- `share_frequency`: 分享频率
- `social_influence_score`: 社交影响力(0-1)
- `follower_count`: 粉丝数
- `following_count`: 关注数
- `share_targets`: 分享渠道统计

**含义**: 用户在社交层面的表现

**应用**:
- 影响力评估
- KOL识别
- 病毒式传播潜力评估

### 维度7: 学习曲线 (Learning Trajectory)

**包含指标**:
- `knowledge_level`: 各领域知识水平
- `learning_speed`: 学习速度(0-1)
- `learning_records`: 学习详细记录
- `skill_progression`: 技能进度历史
- `expertise_areas`: 专长领域列表

**含义**: 用户在平台上的成长和学习进度

**应用**:
- 进阶内容推荐
- 学习路径规划
- 专家识别

### 维度8: 注意力模式 (Attention Patterns)

**包含指标**:
- `attention_span`: 平均注意力持续时间(分钟)
- `skip_rate`: 跳过率(0-1)
- `rewatch_rate`: 重看率(0-1)
- `early_drop_rate`: 早期放弃率(0-1)

**含义**: 用户的注意力特性和内容耐受度

**应用**:
- 内容时长优化
- 关键内容位置调整
- 吸引力评估

### 维度9: 内容深度 (Content Depth Preference)

**包含指标**:
- `depth_preference`: 深度偏好(0=浅层, 1=深度)
- `complexity_tolerance`: 复杂度容受度(0-1)
- `educational_content_ratio`: 教育内容比例

**含义**: 用户对内容复杂度和深度的偏好

**应用**:
- 内容难度调整
- 用户分层推荐
- 学习资源匹配

### 维度10: 多样性需求 (Diversity Needs)

**包含指标**:
- `exploration_rate`: 探索新内容的比例(0-1)
- `exploitation_rate`: 利用已知兴趣的比例(0-1)
- `novelty_seeking`: 寻求新奇度(0-1)
- `category_diversity`: 分类多样性指数

**含义**: 用户在探索与利用之间的平衡

**应用**:
- 探索式vs利用式推荐混合
- 新内容导入比例
- 推荐策略动态调整

### 维度11: 反馈质量 (Feedback Quality)

**包含指标**:
- `feedback_count`: 反馈数量
- `feedback_detail_score`: 反馈详细度(0-1)
- `feedback_accuracy`: 反馈准确性(0-1)
- `avg_feedback_length`: 平均反馈长度

**含义**: 用户反馈的质量和可用性

**应用**:
- 反馈权重评估
- 用户意见可信度
- 评论质量排序

### 维度12: 付费意愿 (Monetization Potential)

**包含指标**:
- `premium_probability`: 付费概率(0-1)
- `estimated_lifetime_value`: 预估生命周期价值
- `premium_feature_interest`: 高级功能兴趣
- `price_sensitivity`: 价格敏感度(0=不敏感, 1=敏感)

**含义**: 用户的商业价值潜力

**应用**:
- 付费用户识别
- 付费策略定制
- 价格敏感度分析

```python
manager.calculate_lifetime_value("user_001")
print(f"生命周期价值: ${profile.estimated_lifetime_value:.2f}")
print(f"付费概率: {profile.premium_probability:.1%}")
```

### 维度13: 流失风险 (Churn Risk)

**包含指标**:
- `churn_risk`: 流失风险评分(0-1)
- `days_since_last_active`: 最后活跃天数
- `activity_decline`: 活动衰减趋势
- `risk_factors`: 风险因素列表

**含义**: 用户离开平台的风险程度

**应用**:
- 用户留存策略
- 风险用户识别和干预
- 重激活活动规划

```python
manager.calculate_churn_risk("user_001")
if profile.churn_risk > 0.7:
    print(f"高风险用户 - 风险因素: {profile.risk_factors}")
```

### 维度14: 影响因子 (Influence Metrics)

**包含指标**:
- `content_creator`: 是否内容创作者
- `community_contribution`: 社区贡献度(0-1)
- `influence_score`: 影响力评分
- `content_sharing_impact`: 内容分享影响力

**含义**: 用户对社区和其他用户的影响力

**应用**:
- KOL和种子用户识别
- 社区管理策略
- 内容传播力预测

### 维度15: 生命周期阶段 (Lifecycle Stage)

**包含指标**:
- `lifecycle_stage`: 当前生命周期阶段
  - `NEW`: 新用户(0-7天)
  - `GROWING`: 成长阶段(7-30天)
  - `MATURE`: 成熟用户(30+天，活跃)
  - `AT_RISK`: 高风险用户
  - `CHURNED`: 已流失用户
- `days_since_signup`: 注册天数
- `stage_transition_history`: 阶段变化历史

**含义**: 用户在平台上的生命周期位置

**应用**:
- 阶段特定的营销策略
- 留存计划设计
- 用户成熟度评估

```python
if profile.lifecycle_stage == LifecycleStage.NEW:
    # 新用户特定策略
    recommend_onboarding_content()
elif profile.lifecycle_stage == LifecycleStage.AT_RISK:
    # 高风险用户留存策略
    trigger_retention_campaign()
```

---

## API参考

### EnhancedProfileManager 类

#### 初始化

```python
from models.enhanced_profile import EnhancedProfileManager

manager = EnhancedProfileManager()
```

#### 创建用户画像

```python
profile = manager.create_profile(user_id="user_001")
```

#### 获取用户画像

```python
profile = manager.get_profile(user_id="user_001")
if profile:
    print(profile.avg_watch_time)
```

#### 更新观看事件

```python
manager.update_from_watch_event(
    user_id="user_001",
    video_id="video_123",
    category="Technology",
    tags=["AI", "机器学习"],
    watch_time=1800,  # 30分钟
    watch_percentage=0.85,  # 85%完成
    device="mobile",
    platform="web",
    timestamp=datetime.now()  # 可选
)
```

#### 更新交互事件

```python
manager.update_from_interaction_event(
    user_id="user_001",
    video_id="video_123",
    action="like",  # 可选: like, dislike, share, comment, save
    details={"comment_text": "很好的内容!"},  # 可选
    timestamp=datetime.now()  # 可选
)
```

#### 计算流失风险

```python
churn_risk = manager.calculate_churn_risk(user_id="user_001")
profile = manager.get_profile("user_001")
print(f"流失风险: {profile.churn_risk:.2f}")
print(f"风险因素: {profile.risk_factors}")
```

#### 计算生命周期价值

```python
ltv = manager.calculate_lifetime_value(user_id="user_001")
profile = manager.get_profile("user_001")
print(f"生命周期价值: ${profile.estimated_lifetime_value:.2f}")
```

#### 获取个性化推荐向量

```python
vector = manager.get_personalization_vector(user_id="user_001")

# vector是一个字典，包含31个推荐特征
for feature_name, value in sorted(vector.items(),
                                   key=lambda x: x[1],
                                   reverse=True)[:10]:
    print(f"{feature_name}: {value:.3f}")
```

#### 获取用户画像摘要

```python
summary = manager.get_profile_summary(user_id="user_001")

# 摘要包含所有15维的聚合信息
print(summary['观看习惯'])
print(summary['内容偏好'])
print(summary['流失风险'])
```

#### 保存和加载画像

```python
# 保存到JSON文件
manager.save_profile(user_id="user_001", filepath="user_001_profile.json")

# 从JSON文件加载
profile = manager.load_profile(filepath="user_001_profile.json")
```

---

## 集成示例

### 示例1: 基本的用户跟踪

```python
from models.enhanced_profile import EnhancedProfileManager
from datetime import datetime

manager = EnhancedProfileManager()

# 用户观看视频
manager.update_from_watch_event(
    user_id="user_123",
    video_id="video_456",
    category="Technology",
    tags=["Python", "编程入门"],
    watch_time=1800,
    watch_percentage=0.9,
    device="mobile",
    platform="web"
)

# 用户点赞
manager.update_from_interaction_event(
    user_id="user_123",
    video_id="video_456",
    action="like"
)

# 获取用户画像摘要
summary = manager.get_profile_summary("user_123")
print(summary)
```

### 示例2: 推荐系统集成

```python
def get_personalized_recommendations(user_id, all_videos):
    """基于用户画像生成个性化推荐"""

    # 获取用户特征向量
    vector = manager.get_personalization_vector(user_id)
    profile = manager.get_profile(user_id)

    # 计算视频与用户的匹配度
    scores = {}
    for video in all_videos:
        score = 0.0

        # 基于内容偏好
        if video.category in profile.favorite_topics:
            score += 0.3

        # 基于观看习惯
        if abs(video.duration - profile.avg_watch_time) < 600:
            score += 0.2

        # 基于深度偏好
        if (video.complexity - 0.5) * (profile.depth_preference - 0.5) > 0:
            score += 0.2

        # 基于多样性需求 - 倾向于推荐热门话题
        if vector['exploration_rate'] > 0.5:
            score += 0.15  # 更多新内容
        else:
            score += vector.get('interest_diversity', 0.5) * 0.15

        # 基于生命周期阶段
        if profile.lifecycle_stage == LifecycleStage.NEW:
            score += 0.15  # 新用户倾向于热门内容

        scores[video.id] = score

    # 返回排序后的推荐
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### 示例3: 留存策略

```python
def generate_retention_strategy(user_id):
    """基于用户画像生成留存策略"""

    profile = manager.get_profile(user_id)
    churn_risk = manager.calculate_churn_risk(user_id)

    strategies = []

    # 根据生命周期阶段
    if profile.lifecycle_stage == LifecycleStage.NEW:
        strategies.append("发送新手教程")
        strategies.append("推荐热门内容")
        strategies.append("邀请完成首次互动")

    elif profile.lifecycle_stage == LifecycleStage.GROWING:
        strategies.append("推荐深度内容")
        strategies.append("邀请参与社区讨论")

    elif profile.lifecycle_stage == LifecycleStage.AT_RISK:
        strategies.append("发送个性化推荐")
        strategies.append("提供优先访问新内容")
        strategies.append("提供优惠或激励")

    # 根据具体风险因素
    if "长期不活跃" in profile.risk_factors:
        strategies.append("发送重新激活活动邀请")

    if "参与度低" in profile.risk_factors:
        strategies.append("推荐更容易参与的内容")

    # 基于内容偏好
    if profile.completion_rate < 0.5:
        strategies.append("推荐更短的内容")

    return strategies
```

### 示例4: 价值评估和优先级

```python
def rank_users_by_value_and_risk():
    """将用户按价值和风险分类"""

    user_segments = {
        'high_value_low_risk': [],      # VIP用户
        'high_value_high_risk': [],     # 需要留存的用户
        'low_value_low_risk': [],       # 普通活跃用户
        'low_value_high_risk': [],      # 需要激活的用户
    }

    for user_id in manager.profiles.keys():
        ltv = manager.calculate_lifetime_value(user_id)
        churn_risk = manager.calculate_churn_risk(user_id)

        profile = manager.get_profile(user_id)

        is_high_value = profile.estimated_lifetime_value > 100
        is_high_risk = churn_risk > 0.5

        if is_high_value and not is_high_risk:
            user_segments['high_value_low_risk'].append(user_id)
        elif is_high_value and is_high_risk:
            user_segments['high_value_high_risk'].append(user_id)
        elif not is_high_value and not is_high_risk:
            user_segments['low_value_low_risk'].append(user_id)
        else:
            user_segments['low_value_high_risk'].append(user_id)

    return user_segments
```

---

## 应用场景

### 场景1: 个性化内容推荐

**目标**: 基于用户画像提高推荐精准度

**实现步骤**:
1. 收集用户的观看和交互事件
2. 更新用户画像的各维度
3. 生成个性化推荐向量
4. 使用向量与内容相似度计算匹配度
5. 根据生命周期阶段调整推荐策略

**关键维度**:
- 内容偏好
- 深度偏好
- 多样性需求
- 注意力模式
- 学习曲线

### 场景2: 用户留存和激活

**目标**: 识别流失风险用户并采取干预措施

**实现步骤**:
1. 计算用户的流失风险评分
2. 识别导致风险的关键因素
3. 根据生命周期阶段设计留存策略
4. 执行针对性的激活活动
5. 跟踪用户的响应和恢复情况

**关键维度**:
- 流失风险
- 生命周期阶段
- 参与度
- 最后活跃时间
- 活动衰减

### 场景3: 付费转化优化

**目标**: 最大化用户的商业价值

**实现步骤**:
1. 评估用户的付费概率
2. 分析用户对高级功能的兴趣
3. 评估价格敏感度
4. 设计针对性的付费转化策略
5. 跟踪转化漏斗指标

**关键维度**:
- 付费意愿
- 参与度
- 学习速度
- 社交影响力
- 生命周期价值

### 场景4: KOL和种子用户识别

**目标**: 识别具有高影响力的用户

**实现步骤**:
1. 评估社交属性和影响力
2. 分析内容创作和分享行为
3. 评估社区贡献度
4. 识别有潜力的KOL
5. 建立KOL合作计划

**关键维度**:
- 社交属性
- 影响因子
- 交互行为
- 共同语言能力
- 粉丝和关注度

### 场景5: A/B测试和策略优化

**目标**: 优化各种运营策略

**实现步骤**:
1. 根据用户画像维度进行分层
2. 设计针对不同层级的A/B实验
3. 收集和分析实验结果
4. 优化策略参数
5. 滚动更新所有用户

**关键维度**:
- 各个维度都可用于分层
- 关键指标追踪
- 长期效果评估

---

## 最佳实践

### 1. 数据收集和更新

```python
# 实时更新用户行为
def track_user_activity(user_id, event_type, event_data):
    """实时跟踪用户活动"""

    if event_type == 'watch':
        manager.update_from_watch_event(
            user_id=user_id,
            video_id=event_data['video_id'],
            category=event_data['category'],
            tags=event_data['tags'],
            watch_time=event_data['duration'],
            watch_percentage=event_data['completion'],
            device=event_data['device'],
            platform=event_data['platform']
        )

    elif event_type == 'interaction':
        manager.update_from_interaction_event(
            user_id=user_id,
            video_id=event_data['video_id'],
            action=event_data['action'],
            details=event_data.get('details', {})
        )
```

### 2. 定期批量更新

```python
# 每天午夜运行批处理更新
def batch_profile_update():
    """批量更新所有用户的聚合维度"""

    for user_id in get_all_active_users():
        # 重新计算和更新关键指标
        manager.calculate_churn_risk(user_id)
        manager.calculate_lifetime_value(user_id)

        # 获取最新的生命周期阶段
        profile = manager.get_profile(user_id)

        # 执行任何必要的操作
        if profile.lifecycle_stage == LifecycleStage.AT_RISK:
            trigger_retention_email(user_id)
```

### 3. 画像验证和清理

```python
def validate_profile_data(user_id):
    """验证用户画像数据的一致性"""

    profile = manager.get_profile(user_id)

    # 检查数据范围
    assert 0 <= profile.completion_rate <= 1, "完成率超出范围"
    assert 0 <= profile.churn_risk <= 1, "流失风险超出范围"
    assert profile.days_since_signup >= 0, "注册天数为负"

    # 检查逻辑一致性
    if profile.completion_rate == 0:
        assert len(profile.watch_history) == 0, "矛盾的观看历史"

    # 检查权重和
    total_interest = sum(profile.interests.values())
    if total_interest > 0:
        assert total_interest <= len(profile.interests), "兴趣权重异常"
```

### 4. 隐私和伦理考虑

```python
def anonymize_profile_data(user_id):
    """匿名化用户画像数据以保护隐私"""

    profile = manager.get_profile(user_id)

    # 不保存个人可识别信息
    # 使用哈希ID而不是真实用户ID
    # 实施数据访问控制

    return {
        'user_id_hash': hash(user_id),
        'profile_vector': manager.get_personalization_vector(user_id),
        # 不包括详细的行为历史
    }

def export_with_gdpr_compliance(user_id):
    """导出符合GDPR的用户数据"""

    profile = manager.get_profile(user_id)
    summary = manager.get_profile_summary(user_id)

    # 提供可读的格式
    # 允许数据导出
    # 实施删除权
```

### 5. 性能优化

```python
# 使用缓存减少重复计算
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_personalization_vector(user_id):
    """缓存个性化向量"""
    return manager.get_personalization_vector(user_id)

def batch_vector_computation():
    """批量计算所有用户的推荐向量"""

    # 并行计算
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=8) as executor:
        user_ids = list(manager.profiles.keys())
        vectors = list(executor.map(
            manager.get_personalization_vector,
            user_ids
        ))

    return dict(zip(user_ids, vectors))
```

---

## 常见问题

### Q: 如何处理新用户(冷启动)?

A: 新用户的画像维度会逐步完善。在此期间:
- 使用内容的热度和流行度进行推荐
- 使用显式反馈(用户填写的偏好)
- 采用探索性推荐策略
- 根据用户的首次行为快速更新画像

### Q: 流失风险多久更新一次?

A: 建议:
- 实时更新: 当用户完成操作时立即更新
- 每日批处理: 每天午夜重新计算汇总指标
- 周期分析: 每周进行趋势分析
- 月度回顾: 每月评估整体策略效果

### Q: 如何处理过期数据?

A: 建议采用时间衰减:
```python
# 最近数据权重更高
alpha = 0.3  # 学习率
new_value = (1 - alpha) * old_value + alpha * recent_value
```

### Q: 推荐向量的31个维度是什么?

A: 包括:
- 观看习惯相关: 3个
- 内容偏好相关: 2个
- 交互行为相关: 2个
- 设备相关: 2个
- 时间模式相关: 2个
- 社交相关: 2个
- 学习相关: 2个
- 注意力相关: 3个
- 内容深度相关: 2个
- 多样性相关: 2个
- 反馈相关: 1个
- 付费相关: 1个
- 流失风险相关: 2个
- 影响因子相关: 2个
- 生命周期相关: 3个

---

## 性能基准

基于示例数据(5个用户, 100+个事件):

| 操作 | 耗时 |
|-----|------|
| 创建用户 | <1ms |
| 更新观看事件 | <5ms |
| 更新交互事件 | <3ms |
| 计算流失风险 | <10ms |
| 计算LTV | <5ms |
| 生成推荐向量 | <8ms |
| 获取画像摘要 | <15ms |

---

## 参考资源

- [增强用户画像实现](../src/models/enhanced_profile.py)
- [可视化工具](../examples/profile_visualization.py)
- [分析演示](../examples/profile_analysis_demo.py)

---

## 更新日志

### v1.0 (2025-11-17)
- 初始版本发布
- 实现15+维用户画像
- 集成可视化和分析工具
- 提供完整的API文档
