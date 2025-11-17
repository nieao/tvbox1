# 阶段二快速开始：AI 视频过渡

## 快速安装

```bash
# 1. 安装基础依赖
pip install -r requirements.txt

# 2. 验证 AI 过渡模块
python -c "from src.core.ai_transition import AITransitionGenerator; print('✓ AI 过渡可用')"
```

## 5 分钟上手

### 方法 1: 使用便捷函数

```python
from src.core.ai_transition import create_ai_transition

# 生成 AI 过渡
frames = create_ai_transition(
    prompt_start="a beautiful sunset over the ocean",
    prompt_end="a starry night sky",
    num_frames=10,
    output_dir="./transitions",
    device="cuda"  # 或 "cpu"
)

print(f"生成了 {len(frames)} 帧过渡")
```

### 方法 2: 使用完整 API

```python
from src.core.ai_transition import AITransitionGenerator, TransitionConfig

# 配置
config = TransitionConfig(
    num_frames=10,
    num_inference_steps=4,
    height=512,
    width=512
)

# 创建生成器
generator = AITransitionGenerator(config=config, verbose=True)

# 生成过渡
frames = generator.generate_transition(
    prompt_start="a peaceful beach",
    prompt_end="a mountain landscape"
)

# 保存帧
generator.save_frames(frames, "./output")

# 清理
generator.cleanup()
```

### 方法 3: 集成到视频编辑

```python
from src.core.generator import TransitionGenerator

# 创建 AI 过渡生成器
gen = TransitionGenerator(
    transition_style="ai_generated",
    duration=2.0,
    enable_ai=True
)

# 生成过渡 (返回 MoviePy 视频片段)
transition_clip = gen.create_transition(
    prompt_start="scene 1 description",
    prompt_end="scene 2 description",
    size=(512, 512),
    fps=30
)

# 使用过渡片段
# transition_clip.write_videofile("transition.mp4")
```

## 运行演示

```bash
# 基础演示 (快速)
python examples/ai_transition_demo.py --mode basic

# 性能基准测试
python examples/ai_transition_demo.py --mode benchmark

# 完整演示
python examples/ai_transition_demo.py --mode all
```

## 性能参考

| 配置 | GPU | 帧数 | 耗时 | 显存 |
|------|-----|------|------|------|
| MVP | RTX 4090 | 5 | ~10s | ~8GB |
| Balanced | RTX 4090 | 10 | ~25s | ~9GB |
| MVP | CPU | 5 | ~120s | ~4GB RAM |

## 常见问题

### Q: GPU 内存不足怎么办？

A: 使用低内存配置：

```python
config = TransitionConfig(
    num_frames=5,
    height=512,
    width=512,
    enable_vae_slicing=True,
    enable_attention_slicing=True
)
```

### Q: 可以在 CPU 上运行吗？

A: 可以，但速度较慢：

```python
config = TransitionConfig(device="cpu")
```

### Q: 如何提高质量？

A: 增加步数和分辨率：

```python
config = TransitionConfig(
    num_frames=20,
    num_inference_steps=6,
    height=768,
    width=768
)
```

## 完整文档

- **使用指南**: [docs/AI_TRANSITION_GUIDE.md](AI_TRANSITION_GUIDE.md)
- **完成报告**: [docs/PHASE_2_AI_TRANSITION_REPORT.md](PHASE_2_AI_TRANSITION_REPORT.md)
- **研究文档**: [docs/LATENT_BLENDING_RESEARCH.md](LATENT_BLENDING_RESEARCH.md)

## 下一步

1. 尝试不同的提示词组合
2. 调整配置参数
3. 运行性能基准测试
4. 集成到你的视频编辑工作流

---

**版本**: 2.0 (阶段二)
**状态**: ✅ MVP 完成
