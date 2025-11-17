# 叙事排序快速开始指南

## 快速使用

### 1. 自动启用（推荐）

叙事排序已经集成到 VideoEditor 中，无需额外配置：

```python
from src.core.editor import VideoEditor

# 创建编辑器（自动启用混合排序策略）
editor = VideoEditor(
    user_interests=["AI", "技术"],
    output_length="medium"
)

# 处理视频（自动应用叙事排序）
result = editor.process_video("input.mp4", "output.mp4")
```

**输出示例**:
```
步骤 3/4: 剪辑视频...
  智能排序片段...
    排序前连贯性: 0.612
    排序后连贯性: 0.854
    连贯性提升: +39.5%
```

### 2. 独立使用排序器

如果需要单独使用排序功能：

```python
from src.core.narrative_sorter import NarrativeSorter

# 创建排序器
sorter = NarrativeSorter(strategy="hybrid")  # 推荐使用 hybrid

# 排序片段
sorted_segments = sorter.sort_segments(segments)

# 评估连贯性
coherence = sorter.evaluate_coherence(sorted_segments)
print(f"连贯性评分: {coherence:.3f}")
```

### 3. 比较不同策略

```python
# 比较所有策略的效果
results = sorter.compare_strategies(
    segments,
    strategies=['time', 'semantic', 'topic', 'graph', 'hybrid']
)

# 查看各策略的连贯性评分
for strategy, result in results.items():
    if 'error' not in result:
        print(f"{strategy}: {result['coherence_score']:.3f}")
```

## 排序策略选择

| 策略 | 适用场景 | 特点 |
|------|----------|------|
| `time` | 时间线性叙事、教程 | 保持原始顺序 |
| `semantic` | 知识讲解、观点论述 | 内容连贯性强 |
| `topic` | 多主题视频 | 主题连续性好 |
| `graph` | 复杂叙事结构 | 综合多种因素 |
| `hybrid` ⭐ | 通用场景 | 最佳综合效果 |

**推荐**: 大多数情况下使用 `hybrid` 策略。

## 演示脚本

### 运行完整演示

```bash
cd /home/user/tvbox1/video-ai
python examples/narrative_demo.py --mode compare
```

**输出**:
- 创建8个示例片段
- 比较5种排序策略
- 生成可视化图表
- 推荐最佳策略

### 单一策略演示

```bash
python examples/narrative_demo.py --mode single --strategy hybrid
```

### 交互式演示

```bash
python examples/narrative_demo.py --mode interactive
```

## 安装依赖

```bash
pip install sentence-transformers>=2.2.0
pip install networkx>=3.0
```

**注意**: 如果这些库不可用，系统会自动降级到基础排序方法。

## 性能优化建议

1. **启用缓存**: 默认已启用，避免重复计算嵌入向量
2. **选择合适策略**:
   - 片段 < 50个: 任意策略
   - 片段 50-100个: hybrid 或 semantic
   - 片段 > 100个: time 或 topic
3. **调整参数**:
   - `max_gap`: 控制时间跳跃容忍度（默认60秒）
   - `preserve_order`: 是否保持部分原始顺序

## 常见问题

### Q1: 排序后连贯性反而下降？

**原因**: 可能原始顺序已经很好，或者策略不适合

**解决**:
1. 尝试其他策略
2. 使用 `compare_strategies()` 找最佳策略
3. 设置 `preserve_order=True` 保持部分原始顺序

### Q2: 排序速度慢？

**原因**: 片段太多或首次加载语义模型

**解决**:
1. 模型加载只发生一次（约3秒）
2. 片段数 < 50时速度很快（< 1秒）
3. 片段数 > 100时考虑使用 `topic` 策略

### Q3: sentence-transformers 安装失败？

**解决**: 系统会自动降级到基础方法，不影响使用

## 进阶功能

### 自定义策略切换

```python
# 动态切换策略
sorter.strategy = "semantic"
sorted_segs_1 = sorter.sort_segments(segments)

sorter.strategy = "topic"
sorted_segs_2 = sorter.sort_segments(segments)
```

### 评估详细信息

```python
# 获取详细的连贯性信息
coherence = sorter.evaluate_coherence(segments)

# 手动检测因果关系
narrative_segs = sorter._convert_to_narrative_segments(segments)
causal_relations = sorter._detect_causal_relations(narrative_segs)
print(f"因果关系: {causal_relations}")
```

## 更多资源

- **详细文档**: `/home/user/tvbox1/video-ai/docs/NARRATIVE_SORTER.md`
- **实现报告**: `/home/user/tvbox1/video-ai/docs/NARRATIVE_SORTER_REPORT.md`
- **源代码**: `/home/user/tvbox1/video-ai/src/core/narrative_sorter.py`
- **测试代码**: `/home/user/tvbox1/video-ai/tests/test_narrative_sorter.py`

## 反馈与支持

如有问题或建议，请在项目 Issues 中反馈。

---

**版本**: 1.0.0
**最后更新**: 2025-11-17
