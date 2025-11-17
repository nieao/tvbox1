# 实时推荐引擎 - 快速开始

5分钟快速上手 Video-AI 实时推荐引擎。

## 快速测试

### 1. 基础功能测试

```bash
cd /home/user/tvbox1/video-ai

# 测试导入
python -c "from src.services.realtime_recommendation import RealtimeRecommendationEngine; print('✓ 导入成功')"
```

### 2. 运行演示

```bash
# 交互式演示（推荐）
python examples/realtime_demo.py

# 按 Enter 键逐步查看各个演示
```

演示内容：
- 用户行为追踪
- 实时兴趣更新
- 推荐结果演化
- 协同过滤
- 热门内容检测
- 性能测试

### 3. 性能测试

```bash
# 完整性能测试（需要几分钟）
python examples/performance_test.py
```

### 4. Web UI 体验

```bash
# 启动 Web UI
streamlit run examples/web_ui.py

# 打开浏览器访问显示的 URL（通常是 http://localhost:8501）
# 切换到"处理历史"标签页查看推荐功能
```

## 代码示例

### 简单示例（5行代码）

```python
from src.services.personalization import PersonalizationService

# 创建服务
service = PersonalizationService(enable_realtime=True)

# 添加视频
service.add_video_metadata('video_ai', {'topics': ['AI', '技术'], 'category': '教育'})

# 追踪行为
service.track_user_action('user_1', 'view', 'video_ai', duration=300)

# 获取推荐
recs = service.get_realtime_recommendations('user_1', num=5)
print(f"推荐数量: {len(recs)}")
```

### 完整示例

```python
from src.services.realtime_recommendation import RealtimeRecommendationEngine, UserBehavior

# 1. 创建引擎
engine = RealtimeRecommendationEngine()

# 2. 添加视频元数据
videos = {
    'ai_tutorial': {'topics': ['AI', '机器学习'], 'category': '教育'},
    'python_course': {'topics': ['编程', 'Python'], 'category': '编程'},
    'web_dev': {'topics': ['Web开发', 'JavaScript'], 'category': '编程'}
}

for vid, meta in videos.items():
    engine.add_video_metadata(vid, meta)

# 3. 模拟用户行为
behaviors = [
    UserBehavior('user_1', 'view', 'ai_tutorial', duration=300),
    UserBehavior('user_1', 'like', 'ai_tutorial'),
    UserBehavior('user_1', 'view', 'python_course', duration=200),
]

for behavior in behaviors:
    engine.track_behavior(behavior)

# 4. 获取推荐
recommendations = engine.get_recommendations('user_1', num_recommendations=5)

# 5. 显示结果
print("推荐结果:")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['video_id']}")
    print(f"   分数: {rec['score']:.3f}")
    print(f"   理由: {rec['reason']}")
    print(f"   方法: {rec['method']}")
    print()

# 6. 获取用户洞察
insights = engine.get_user_insights('user_1')
print("用户洞察:")
print(f"  总行为数: {insights['total_behaviors']}")
print(f"  参与度: {insights['engagement_score']:.2f}")
print(f"  主要兴趣: {insights['top_interests']}")
```

## 验证安装

运行此脚本验证功能是否正常：

```python
# save as test_realtime.py
from src.services.realtime_recommendation import RealtimeRecommendationEngine, UserBehavior

def test_basic_functionality():
    """测试基本功能"""
    print("测试实时推荐引擎...")

    # 创建引擎
    engine = RealtimeRecommendationEngine()
    print("✓ 引擎创建成功")

    # 添加视频
    engine.add_video_metadata('test_video', {
        'topics': ['测试'],
        'category': '测试'
    })
    print("✓ 视频添加成功")

    # 追踪行为
    engine.track_behavior(UserBehavior('test_user', 'view', 'test_video', duration=100))
    print("✓ 行为追踪成功")

    # 获取推荐
    recs = engine.get_recommendations('test_user', num_recommendations=3)
    print(f"✓ 推荐生成成功 (数量: {len(recs)})")

    # 获取洞察
    insights = engine.get_user_insights('test_user')
    print(f"✓ 用户洞察成功 (行为数: {insights['total_behaviors']})")

    # 统计
    stats = engine.get_statistics()
    print(f"✓ 系统统计成功 (用户数: {stats['total_users']})")

    print("\n✅ 所有测试通过!")

if __name__ == "__main__":
    test_basic_functionality()
```

运行测试：
```bash
python test_realtime.py
```

## 常见问题

### Q: 如何启用/禁用实时推荐？

```python
# 启用
service = PersonalizationService(enable_realtime=True)

# 禁用
service = PersonalizationService(enable_realtime=False)
```

### Q: 如何查看推荐原因？

推荐结果中包含 `reason` 字段：
```python
for rec in recommendations:
    print(rec['reason'])  # "基于您的兴趣", "相似用户也喜欢", 等
```

### Q: 如何调整推荐数量？

```python
# 获取 10 个推荐
recs = service.get_realtime_recommendations('user_id', num=10)

# 获取 5 个推荐
recs = service.get_realtime_recommendations('user_id', num=5)
```

### Q: 性能如何？

预期性能：
- 行为追踪: < 10ms
- 推荐生成: < 100ms
- 并发用户: 1000+

运行性能测试查看实际数据：
```bash
python examples/performance_test.py
```

## 下一步

- 📖 阅读完整文档: `docs/REALTIME_RECOMMENDATION.md`
- 🎯 查看性能报告: `docs/STAGE3_COMPLETION_REPORT.md`
- 💻 查看 API 参考: `docs/REALTIME_RECOMMENDATION.md#api-参考`
- 🚀 运行演示脚本: `examples/realtime_demo.py`

## 获取帮助

- 查看文档: `docs/REALTIME_RECOMMENDATION.md`
- 运行演示: `python examples/realtime_demo.py`
- 性能测试: `python examples/performance_test.py`

---

**准备好开始了吗？运行演示脚本体验实时推荐！** 🚀

```bash
python examples/realtime_demo.py
```
