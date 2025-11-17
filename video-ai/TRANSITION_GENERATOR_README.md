# 视频过渡效果生成器 (TransitionGenerator)

## 概述

`TransitionGenerator` 是 video-ai 项目的核心组件，提供灵活的视频过渡效果生成能力。支持多种过渡风格和文字模板，为视频编辑提供专业的视觉效果。

## 功能特性

### 支持的过渡类型 (5 种)

1. **text** - 文字过渡
   - 支持 5 种文字模板
   - 可自定义过渡时长
   - 支持淡入淡出效果

2. **fade** - 淡入淡出过渡
   - 黑屏淡出效果
   - 简洁流畅
   - 适用于大多数场景

3. **blur** - 模糊过渡
   - 灰色背景
   - 高斯模糊效果
   - 柔和过渡

4. **zoom** - 缩放过渡
   - 中心点缩放
   - 动态效果
   - 吸引眼球

5. **gradient** - 渐变过渡
   - 平滑颜色过渡
   - 多色渐变
   - 专业视觉效果

### 文字模板 (5 种)

1. **minimal** - 简约风格
   - 白色背景 + 黑色文字
   - 简单动画
   - 适合素雅视频

2. **modern** - 现代风格
   - 蓝色到紫色渐变背景
   - 白色文字
   - 简洁现代设计

3. **classic** - 经典风格
   - 黑色背景 + 白色文字
   - 居中显示
   - 永不过时

4. **colorful** - 彩色风格
   - 彩虹渐变背景
   - 白色文字带阴影
   - 充满活力

5. **info_card** - 信息卡片风格
   - 渐变背景 + 白色卡片
   - 分层文字设计
   - 专业卡片式布局

## 使用方法

### 基础使用

```python
from src.core.generator import TransitionGenerator

# 创建过渡生成器
generator = TransitionGenerator(
    transition_style="text",  # 过渡类型
    duration=2.0              # 过渡时长（秒）
)

# 创建文字过渡
transition = generator.create_transition(
    text="第二部分：深度学习",
    size=(1920, 1080),
    template="modern"
)
```

### 不同过渡类型示例

```python
# 淡入淡出过渡
fade_gen = TransitionGenerator(style="fade", duration=1.5)
fade_transition = fade_gen.create_transition(size=(1920, 1080))

# 模糊过渡
blur_gen = TransitionGenerator(style="blur", duration=2.0)
blur_transition = blur_gen.create_transition(size=(1920, 1080))

# 渐变过渡
gradient_gen = TransitionGenerator(style="gradient", duration=2.5)
gradient_transition = gradient_gen.create_transition(size=(1920, 1080))
```

### 文字模板示例

```python
generator = TransitionGenerator(style="text")

# 简约风格
minimal = generator.create_transition(
    text="第二部分",
    template="minimal"
)

# 现代风格
modern = generator.create_transition(
    text="第二部分",
    template="modern"
)

# 彩色风格
colorful = generator.create_transition(
    text="第二部分",
    template="colorful"
)

# 信息卡片（支持冒号分隔的标题和副标题）
card = generator.create_transition(
    text="第二部分：深度学习",
    template="info_card"
)
```

### 为视频片段添加过渡

```python
from src.core.generator import TransitionGenerator

generator = TransitionGenerator(style="text", duration=2.0)

# 假设有视频片段列表和主题列表
clips = [clip1, clip2, clip3]
topics = ["基础概念", "深度学习", "实践应用"]

# 自动在片段间添加过渡
clips_with_transitions = generator.apply_to_clips(clips, topics)
```

### 与 VideoEditor 集成

```python
from src.core.editor import VideoEditor

# 创建编辑器，指定过渡风格和模板
editor = VideoEditor(
    user_interests=["编程", "AI"],
    transition_style="text",        # 过渡类型
    transition_template="modern"    # 文字模板
)

# 处理视频时会自动应用过渡
result = editor.process_video(
    input_path="input.mp4",
    output_path="output.mp4"
)
```

## API 参考

### TransitionGenerator 类

#### 初始化参数

```python
TransitionGenerator(
    transition_style: str = "text",  # 过渡类型
    duration: float = 2.0            # 过渡时长（秒）
)
```

#### 主要方法

##### `create_transition()`

创建单个过渡效果

```python
def create_transition(
    text: Optional[str] = None,
    size: Tuple[int, int] = (1920, 1080),
    template: str = "default",
    **kwargs
)
```

参数：
- `text` (str, 可选): 过渡文字，仅用于文字过渡
- `size` (Tuple[int, int]): 视频尺寸，默认 (1920, 1080)
- `template` (str): 文字模板名称，仅用于文字过渡
- `**kwargs`: 额外的配置参数

返回：
- VideoClip: 过渡视频片段

##### `apply_to_clips()`

为多个视频片段间添加过渡

```python
def apply_to_clips(
    clips: list,
    topics: Optional[list] = None
) -> list
```

参数：
- `clips` (list): 视频片段列表
- `topics` (list, 可选): 主题列表，用于生成过渡文字

返回：
- list: 添加过渡后的片段列表

## 技术细节

### 依赖

- **moviepy** (必需): 视频处理库
- **pillow** (可选): 图像处理，用于创建渐变和卡片
- **numpy** (可选): 数值计算，用于生成图像数组
- **scipy** (可选): 科学计算
- **colorsys** (标准库): 颜色空间转换

### 特点

1. **优雅的降级**: 缺少可选依赖时使用简单替代方案
2. **灵活的配置**: 支持多种参数组合
3. **高效的性能**: 即时生成过渡，不需要预先渲染
4. **易于扩展**: 可轻松添加新的过渡类型和模板

## 测试

运行示例脚本查看各种过渡效果：

```bash
python examples/transition_demo.py
```

这将演示：
1. 文字过渡 - 各种模板
2. 其他过渡类型
3. 为多个片段添加过渡
4. 自定义参数
5. 错误处理

## 常见问题

### Q: 如何自定义过渡时长？
A: 在创建 TransitionGenerator 时设置 `duration` 参数：
```python
generator = TransitionGenerator(duration=3.0)  # 3 秒
```

### Q: 如何创建自定义模板？
A: 可以扩展 TransitionGenerator 类并添加新的 `_template_*` 方法

### Q: 支持哪些字体？
A: 默认使用 Arial 字体，可以扩展支持更多字体

### Q: 如何调整文字大小？
A: 可以在模板方法中修改 `fontsize` 参数

## 后续规划 (阶段二)

1. **AI 过渡生成**: 使用 AI 模型智能生成过渡文字
2. **动画效果**: 添加更多复杂的动画效果
3. **音频同步**: 过渡与音频的同步
4. **自定义品牌**: 支持自定义品牌元素和风格
5. **实时预览**: 实时预览过渡效果

## 贡献

欢迎提交问题和改进建议！
