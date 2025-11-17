# AI 视频过渡生成指南

## 概述

Video-AI 项目的阶段二核心功能：基于 Stable Diffusion XL 的 **Latent Blending** AI 视频过渡生成。

### 主要特性

✅ **真正的 AI 生成过渡** - 使用 Stable Diffusion XL 在潜在空间中插值
✅ **SLERP 插值** - 球面线性插值保证视觉平滑性
✅ **GPU 加速** - 完整的 CUDA 支持和内存优化
✅ **降级机制** - GPU 不可用时自动降级到简单过渡
✅ **灵活配置** - 多种质量预设 (MVP/Balanced/High Quality)
✅ **性能优化** - VAE slicing、Attention slicing、批处理支持

---

## 安装

### 1. 基础依赖

```bash
# 核心依赖 (如果已安装项目可跳过)
pip install -r requirements.txt
```

### 2. AI 过渡专用依赖

**关键依赖** (已包含在 requirements.txt):
- `torch>=2.1.0` - PyTorch 深度学习框架
- `diffusers>=0.24.0` - Hugging Face Diffusers (Stable Diffusion)
- `transformers>=4.35.0` - 文本编码器
- `accelerate>=0.25.0` - 加速库

**GPU 支持** (推荐):
```bash
# CUDA 版本的 PyTorch (根据你的 CUDA 版本)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 或 CPU 版本 (速度较慢)
pip install torch torchvision
```

### 3. 验证安装

```bash
python -c "from src.core.ai_transition import AITransitionGenerator; print('✓ AI 过渡模块可用')"
```

---

## 快速开始

### 基础示例

```python
from src.core.ai_transition import create_ai_transition

# 生成 AI 过渡
frames = create_ai_transition(
    prompt_start="a peaceful sunset over the ocean",
    prompt_end="a vibrant starry night sky",
    num_frames=10,
    output_dir="./output/transitions",
    device="cuda"  # 或 "cpu"
)

print(f"生成了 {len(frames)} 帧过渡")
```

### 使用 TransitionGenerator (集成方式)

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
    prompt_start="a beautiful beach at sunrise",
    prompt_end="a mountain landscape with snow",
    size=(512, 512),
    fps=30
)

# 保存或合并到视频中
# transition_clip.write_videofile("transition.mp4")
```

---

## 配置选项

### TransitionConfig 参数

```python
from src.core.ai_transition import TransitionConfig

# MVP 配置 (快速，适合测试)
mvp_config = TransitionConfig(
    model_name="stabilityai/sdxl-turbo",
    num_frames=5,
    num_inference_steps=2,
    height=512,
    width=512,
    device="cuda",
    interpolation_method="slerp"  # 或 "linear"
)

# 平衡配置 (质量与速度)
balanced_config = TransitionConfig(
    model_name="stabilityai/sdxl-turbo",
    num_frames=10,
    num_inference_steps=4,
    height=512,
    width=512,
    device="cuda"
)

# 高质量配置 (需要更多时间和内存)
hq_config = TransitionConfig(
    model_name="stabilityai/sdxl-turbo",
    num_frames=20,
    num_inference_steps=6,
    height=768,
    width=768,
    device="cuda",
    enable_vae_slicing=True,
    enable_attention_slicing=True
)
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `model_name` | `"stabilityai/sdxl-turbo"` | SDXL 模型名称 (SDXL Turbo 最快) |
| `num_frames` | `10` | 过渡帧数 |
| `num_inference_steps` | `5` | 去噪步数 (SDXL Turbo: 1-5) |
| `guidance_scale` | `0.0` | 引导强度 (SDXL Turbo 不需要) |
| `height` | `512` | 图像高度 |
| `width` | `512` | 图像宽度 |
| `device` | `"cuda"` | 设备 ("cuda" 或 "cpu") |
| `interpolation_method` | `"slerp"` | 插值方法 ("slerp" 或 "linear") |
| `crossfeed_power` | `0.3` | 跨馈送强度 (0-1) |
| `enable_vae_slicing` | `True` | 启用 VAE 切片 (节省内存) |
| `enable_attention_slicing` | `True` | 启用注意力切片 (节省内存) |

---

## 性能优化

### GPU 内存优化

```python
from src.core.ai_transition import AITransitionGenerator, TransitionConfig

# 低内存配置 (适合 8GB 显存)
config = TransitionConfig(
    num_frames=5,
    num_inference_steps=2,
    height=512,
    width=512,
    enable_vae_slicing=True,
    enable_attention_slicing=True,
    enable_cpu_offload=False  # 如果内存不足设为 True
)

generator = AITransitionGenerator(config=config)
```

### 性能基准测试

```python
# 运行基准测试
results = generator.benchmark()

print(f"总耗时: {results['total_time']:.2f}s")
print(f"每帧: {results['time_per_frame']:.2f}s")
print(f"内存占用: {results['memory_used_gb']:.2f}GB")
```

### 性能参考

| 配置 | GPU | 帧数 | 耗时 | 显存占用 |
|------|-----|------|------|----------|
| MVP | RTX 4090 | 5 | ~10s | ~8GB |
| MVP | RTX 3080 | 5 | ~15s | ~9GB |
| MVP | CPU | 5 | ~120s | ~4GB RAM |
| Balanced | RTX 4090 | 10 | ~25s | ~9GB |
| High Quality | RTX 4090 | 20 | ~60s | ~12GB |

---

## 高级用法

### 1. 批量生成过渡

```python
scenes = [
    ("beach at sunrise", "forest in morning mist"),
    ("city street at day", "same street at night"),
    ("desert landscape", "oasis with palm trees")
]

for i, (start, end) in enumerate(scenes):
    frames = generator.generate_transition(
        prompt_start=start,
        prompt_end=end,
        num_frames=10
    )
    generator.save_frames(frames, f"./output/scene_{i}")
```

### 2. 自定义插值方法

```python
# SLERP (球面线性插值) - 更平滑
config_slerp = TransitionConfig(interpolation_method="slerp")

# Linear (线性插值) - 更快
config_linear = TransitionConfig(interpolation_method="linear")
```

### 3. 进度回调

```python
def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"进度: {current}/{total} ({percent:.1f}%)")

frames = generator.generate_transition(
    prompt_start="...",
    prompt_end="...",
    callback=progress_callback
)
```

---

## 故障排查

### 常见问题

#### 1. CUDA 内存不足 (OOM)

**错误**: `RuntimeError: CUDA out of memory`

**解决方案**:
```python
# 降低分辨率
config.height = 512
config.width = 512

# 减少帧数
config.num_frames = 5

# 启用内存优化
config.enable_vae_slicing = True
config.enable_attention_slicing = True
config.enable_cpu_offload = True

# 清理缓存
import torch
torch.cuda.empty_cache()
```

#### 2. 模型下载失败

**错误**: `OSError: Can't load model...`

**解决方案**:
```bash
# 手动下载模型
huggingface-cli download stabilityai/sdxl-turbo

# 或使用镜像站点
export HF_ENDPOINT=https://hf-mirror.com
```

#### 3. 导入错误

**错误**: `ImportError: cannot import name 'AITransitionGenerator'`

**解决方案**:
```bash
# 确保在项目根目录
cd /home/user/tvbox1/video-ai

# 检查依赖
pip install torch diffusers transformers accelerate

# 验证安装
python -c "import torch; print(torch.__version__)"
python -c "import diffusers; print(diffusers.__version__)"
```

#### 4. GPU 不可用

**症状**: 自动降级到 CPU，速度很慢

**检查**:
```python
import torch
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"设备数量: {torch.cuda.device_count()}")
```

**解决方案**:
- 确保安装了 CUDA 版本的 PyTorch
- 检查 NVIDIA 驱动和 CUDA 工具包

---

## 示例演示

### 运行演示脚本

```bash
# 基础演示
python examples/ai_transition_demo.py --mode basic

# 性能基准测试
python examples/ai_transition_demo.py --mode benchmark

# 插值方法对比
python examples/ai_transition_demo.py --mode comparison

# 视频集成测试
python examples/ai_transition_demo.py --mode integration

# 运行所有演示
python examples/ai_transition_demo.py --mode all --output ./output/demo
```

### 输出示例

演示会生成:
- 单帧 PNG 图像 (`frame_0000.png`, `frame_0001.png`, ...)
- GIF 动画 (`transition.gif`)
- 性能基准报告 (控制台输出)

---

## API 参考

### AITransitionGenerator

```python
class AITransitionGenerator:
    def __init__(
        self,
        config: Optional[TransitionConfig] = None,
        enable_gpu: bool = True,
        verbose: bool = True
    )

    def load_model(self) -> None
        """加载 Stable Diffusion 模型"""

    def generate_transition(
        self,
        prompt_start: str,
        prompt_end: str,
        num_frames: Optional[int] = None,
        callback: Optional[Callable] = None
    ) -> List[Image.Image]
        """生成 AI 过渡帧"""

    def benchmark(self) -> Dict[str, float]
        """性能基准测试"""

    def save_frames(
        self,
        frames: List[Image.Image],
        output_dir: str,
        prefix: str = "frame"
    ) -> None
        """保存帧序列"""

    def cleanup(self) -> None
        """清理资源"""
```

### 便捷函数

```python
def create_ai_transition(
    prompt_start: str,
    prompt_end: str,
    num_frames: int = 10,
    output_dir: Optional[str] = None,
    device: str = "cuda",
    verbose: bool = True
) -> List[Image.Image]
    """快速创建 AI 过渡"""
```

---

## 技术原理

### Latent Blending 算法

1. **文本编码**: 将提示词编码为嵌入向量
2. **嵌入插值**: 在嵌入空间中使用 SLERP 插值
3. **图像生成**: 为每个插值点生成图像
4. **帧序列**: 组合为平滑的过渡序列

### SLERP vs Linear

- **SLERP** (球面线性插值): 保持角速度恒定，更平滑
- **Linear** (线性插值): 更快，但可能不够平滑

### 性能优化技术

- **VAE Slicing**: 减少 VAE 解码器的内存占用
- **Attention Slicing**: 减少注意力机制的内存占用
- **FP16**: 使用半精度浮点数 (GPU)
- **批处理**: 批量处理多个过渡请求

---

## 未来改进

### 计划中的功能

- [ ] 完整的树形分支算法 (递归 latent blending)
- [ ] 自动提示词优化
- [ ] 视频帧参考图像支持
- [ ] 多 GPU 并行处理
- [ ] 实时预览 (低分辨率)
- [ ] 更多插值算法 (cubic, bezier)
- [ ] 风格迁移过渡
- [ ] 音频同步过渡

---

## 参考资源

- **原始项目**: [lunarring/latentblending](https://github.com/lunarring/latentblending)
- **Stable Diffusion XL**: [stabilityai/sdxl](https://huggingface.co/stabilityai/sdxl-turbo)
- **Diffusers 文档**: [huggingface.co/docs/diffusers](https://huggingface.co/docs/diffusers)
- **研究报告**: `docs/LATENT_BLENDING_RESEARCH.md`

---

## 许可证

本项目遵循 MIT 许可证。

使用的模型和库:
- SDXL Turbo: [SDXL Turbo License](https://huggingface.co/stabilityai/sdxl-turbo)
- Diffusers: Apache 2.0
- PyTorch: BSD-style

---

## 贡献

欢迎贡献! 请查看主项目的贡献指南。

**开发重点**:
- 性能优化
- 更多插值算法
- 视频集成改进
- 文档和示例

---

**最后更新**: 2025-11-17
**版本**: 2.0 (阶段二)
**状态**: ✅ MVP 完成
