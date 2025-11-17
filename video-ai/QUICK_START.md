# 场景检测 - 快速开始指南

## 5分钟上手

### 安装依赖

```bash
pip install opencv-python numpy
```

### 基础示例

```python
from src.core.scene_detector import SceneDetector

# 创建检测器
detector = SceneDetector(method="hybrid")

# 检测场景
scenes = detector.detect_scenes("video.mp4")

# 显示结果
for i, scene in enumerate(scenes, 1):
    print(f"场景 {i}: {scene.start_time:.2f}s - {scene.end_time:.2f}s")
    print(f"  类型: {scene.scene_type.value}")
    print(f"  置信度: {scene.confidence:.1%}\n")
```

## 常见用法

### 1. 快速检测

```python
from src.core.scene_detector import SceneDetector

detector = SceneDetector(method="frame_diff")
scenes = detector.detect_scenes("video.mp4")
print(f"检测到 {len(scenes)} 个场景")
```

### 2. 获取统计信息

```python
stats = detector.get_statistics(scenes)
print(f"平均时长: {stats['average_duration']:.2f}s")
print(f"平均置信度: {stats['confidence_stats']['average']:.1%}")
```

### 3. 保存和加载

```python
# 保存
detector.save_scenes(scenes, "output/scenes.json")

# 加载
loaded_scenes = detector.load_scenes("output/scenes.json")
```

### 4. 与分析器集成

```python
from src.core.analyzer import ContentAnalyzer

analyzer = ContentAnalyzer(
    use_scene_detection=True,
    scene_detection_method="hybrid"
)

result = analyzer.analyze(
    transcript=transcript,
    video_path="video.mp4"
)

# 访问场景
for scene in result.scenes:
    print(f"时间: {scene.start_time:.2f}s")
```

## 运行演示

```bash
# 交互菜单
python examples/scene_demo.py

# 自定义视频
python examples/scene_demo.py input/video.mp4 hybrid

# 集成演示
python examples/integration_demo.py
```

## 方法选择

| 需求 | 推荐方法 | 阈值 |
|------|---------|------|
| 最快 | frame_diff | 25 |
| 精度最好 | hybrid | 30 |
| 色彩敏感 | histogram | 40 |
| 运动分析 | motion | 25 |

## 参数调优

```python
detector = SceneDetector(
    method="hybrid",
    threshold=30.0,          # 调整灵敏度
    min_scene_length=1.0,    # 最小场景(秒)
    max_scene_length=120.0,  # 最大场景(秒)
    smooth_window=5,         # 平滑(越大越平缓)
    frame_sampling=1         # 采样(越大越快)
)
```

## 输出格式

### Scene 对象属性

```python
scene.start_time          # 开始时间(秒)
scene.end_time            # 结束时间(秒)
scene.duration            # 时长(秒)
scene.scene_type.value    # 场景类型 (string)
scene.confidence          # 置信度 (0-1)
scene.motion_level        # 运动强度 (0-1)
scene.color_change        # 颜色变化 (0-1)
```

### 统计信息结构

```python
{
    'total_scenes': 15,
    'total_duration': 600.0,
    'average_duration': 40.0,
    'scene_types': {'scene_change': 9, ...},
    'confidence_stats': {'average': 0.85, ...}
}
```

## 文件位置

```
video-ai/
├── src/core/
│   └── scene_detector.py        ← 核心模块
├── examples/
│   ├── scene_demo.py            ← 基础演示
│   └── integration_demo.py       ← 集成演示
├── tests/
│   └── test_scene_detector.py    ← 单元测试
└── SCENE_DETECTION.md           ← 详细文档
```

## 故障排除

### 导入错误

```
ModuleNotFoundError: No module named 'cv2'
→ 安装: pip install opencv-python numpy
```

### 视频加载失败

```
FileNotFoundError: 视频文件不存在
→ 检查视频路径是否正确
```

### 检测结果过多/过少

```
调整 threshold 参数:
- 检测过多: 增加 threshold (如 40)
- 检测过少: 减少 threshold (如 20)
```

## 更多信息

- 完整 API: 见 `SCENE_DETECTION.md`
- 实现细节: 见 `IMPLEMENTATION_SUMMARY.md`
- 源代码: `/src/core/scene_detector.py`

---

**Happy Scene Detecting!** 🎬
