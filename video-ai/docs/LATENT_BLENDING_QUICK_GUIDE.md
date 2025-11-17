# Latent Blending 快速实现指南

## 快速开始（5分钟）

### 安装
```bash
pip install git+https://github.com/lunarring/latentblending
pip install diffusers transformers torch torchvision
```

### 最简单的例子
```python
from latentblending.blending_engine import BlendingEngine
from latentblending.diffusers_holder import DiffusersHolder

# 1. 加载模型
pipe = DiffusersHolder(model_id="stabilityai/sdxl-turbo")

# 2. 初始化混合引擎
be = BlendingEngine(pipe)

# 3. 设置提示
be.set_prompt1("underwater scene with fish")
be.set_prompt2("alien landscape with crystals")

# 4. 配置质量
be.set_branching(depth=1, nmb_trans_images=10)

# 5. 生成过渡
transition_images = be.run_transition()

# 6. 保存
be.write_movie_transition('output.mp4', duration_transition=10)
```

---

## 核心概念速记

### 三个关键对象

| 对象 | 作用 | 关键方法 |
|------|------|---------|
| **DiffusersHolder** | 管理 SDXL 模型 | get_text_embedding(), latent2image(), run_diffusion_sd_xl() |
| **BlendingEngine** | 混合控制 | set_prompt1/2(), set_branching(), run_transition() |
| **utils** | 辅助工具 | interpolate_spherical(), add_frames_linear_interp() |

### 参数快记

```python
# MVP 配置（快速，15秒/过渡）
config = {
    'guidance_scale': 5.0,           # 文本引导（推荐 3-5）
    'num_inference_steps': 20,       # 去噪步骤（快=20, 好=40）
    'guidance_scale_mid_damper': 0.7,# 中点衰减（避免生硬）
    'branch1_crossfeed_power': 0.4,  # 结构保留（0-1）
    'depth': 1,                       # 分支深度（快=1, 好=3）
    'nmb_trans_images': 5,            # 输出帧数
}
```

---

## 常用操作模式

### 模式 1：简单关键帧过渡

```python
# 场景：两个不同的概念之间过渡
prompts = [
    "a serene lake at sunrise",
    "a busy cityscape at night"
]

be = BlendingEngine(DiffusersHolder())
be.set_prompt1(prompts[0])
be.set_prompt2(prompts[1])
be.set_branching(depth=1, nmb_trans_images=8)

frames = be.run_transition()
```

### 模式 2：视频片段间的连贯过渡

```python
import cv2

class VideoTransitioner:
    def __init__(self, model_id="stabilityai/sdxl-turbo"):
        self.pipe = DiffusersHolder(model_id)
        self.be = BlendingEngine(self.pipe)
    
    def transition_between_videos(self, video1, video2, fps=30):
        # 提取末尾帧和开头帧
        last_frame1 = self._get_last_frame(video1)
        first_frame2 = self._get_first_frame(video2)
        
        # 配置引擎
        self.be.set_branching(depth=1, nmb_trans_images=fps)
        
        # 生成过渡
        # 提示可以从视频分析得出
        self.be.set_prompt1("scene from first video")
        self.be.set_prompt2("scene from second video")
        
        return self.be.run_transition()
    
    @staticmethod
    def _get_last_frame(video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            last_frame = frame
        cap.release()
        return last_frame
    
    @staticmethod
    def _get_first_frame(video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        return frame
```

### 模式 3：参数动态调整

```python
quality_presets = {
    'draft': {
        'num_inference_steps': 15,
        'guidance_scale': 6.0,
        'depth': 0,
        'nmb_trans_images': 4,
    },
    'preview': {
        'num_inference_steps': 25,
        'guidance_scale': 4.5,
        'depth': 1,
        'nmb_trans_images': 8,
    },
    'final': {
        'num_inference_steps': 40,
        'guidance_scale': 3.5,
        'depth': 2,
        'nmb_trans_images': 20,
    },
}

def generate_with_preset(prompt1, prompt2, preset='preview'):
    config = quality_presets[preset]
    
    pipe = DiffusersHolder(
        num_inference_steps=config['num_inference_steps'],
        guidance_scale=config['guidance_scale']
    )
    be = BlendingEngine(pipe)
    be.set_prompt1(prompt1)
    be.set_prompt2(prompt2)
    be.set_branching(
        depth=config['depth'],
        nmb_trans_images=config['nmb_trans_images']
    )
    
    return be.run_transition()
```

---

## 性能优化速查

### 快速优化清单

```python
# 1. 启用内存优化
pipe.vae.enable_slicing()           # ↓50% VAE 内存
pipe.unet.enable_attention_slicing() # ↓30-50% 注意力内存

# 2. 使用 fp16 精度
pipe.pipe = pipe.pipe.to(torch.float16)

# 3. 禁用梯度
torch.set_grad_enabled(False)

# 4. 缓存嵌入
embedding_cache = {}
cache_key = hash(prompt)
if cache_key not in embedding_cache:
    embedding_cache[cache_key] = pipe.get_text_embedding(prompt)

# 5. 批处理
batch_size = 2
for i in range(0, len(prompts), batch_size):
    batch_prompts = prompts[i:i+batch_size]
    # 批量处理...
```

### 内存诊断

```python
import torch

# 监控内存使用
torch.cuda.reset_peak_memory_stats()
transition_images = be.run_transition()
peak_memory = torch.cuda.max_memory_allocated() / 1e9
print(f"Peak memory: {peak_memory:.2f} GB")

# 如果超过 GPU 内存，尝试：
# 1. 减少 nmb_trans_images
# 2. 减少 num_inference_steps
# 3. 启用更多内存优化
# 4. 使用更小的模型（SDXL Turbo）
```

---

## 参数调优指南

### 问题排查表

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| 过渡有"闪烁" | 分支不足或引导太强 | ↑depth, ↓guidance_scale |
| 内存溢出 | 计算太复杂 | ↓nmb_trans_images, ↓depth, 启用slicing |
| 过渡太生硬 | 中点没有平滑 | ↑guidance_scale_mid_damper |
| 结构失真 | 跨馈送过弱 | ↑branch1_crossfeed_power |
| 计算太慢 | 质量设置过高 | ↓num_inference_steps, ↓depth |
| 输出质量差 | 设置太快 | ↑num_inference_steps, ↑depth |

### 实时参数调整示例

```python
class AdaptiveTransitioner:
    """根据内存和时间预算自动调整参数"""
    
    def generate_transition(
        self,
        prompt1: str,
        prompt2: str,
        max_time: int = 30,  # 秒
        max_memory: float = 10e9,  # GB
    ):
        """自动调整参数以满足约束"""
        
        # 估计所需时间
        estimated_time = self._estimate_time(max_memory)
        
        if estimated_time > max_time:
            # 降低质量
            config = self._get_mvp_config()
        else:
            config = self._get_balanced_config()
        
        pipe = DiffusersHolder(**config['pipe_args'])
        be = BlendingEngine(pipe)
        be.set_prompt1(prompt1)
        be.set_prompt2(prompt2)
        be.set_branching(**config['branching_args'])
        
        return be.run_transition()
    
    @staticmethod
    def _estimate_time(memory_available):
        # 粗略估计：每 1GB 内存约 1-2 秒计算
        return memory_available / 1e9 * 1.5
    
    @staticmethod
    def _get_mvp_config():
        return {
            'pipe_args': {
                'num_inference_steps': 20,
                'guidance_scale': 5.0,
            },
            'branching_args': {
                'depth': 0,
                'nmb_trans_images': 5,
            }
        }
    
    @staticmethod
    def _get_balanced_config():
        return {
            'pipe_args': {
                'num_inference_steps': 30,
                'guidance_scale': 4.0,
            },
            'branching_args': {
                'depth': 1,
                'nmb_trans_images': 10,
            }
        }
```

---

## 与视频编辑系统集成

### 集成到现有视频 AI 系统

```python
from latentblending.blending_engine import BlendingEngine

class VideoAISystemWithTransitions:
    """扩展现有的视频 AI 系统支持平滑过渡"""
    
    def __init__(self, existing_system):
        self.video_ai = existing_system
        self.transition_gen = BlendingEngine(
            DiffusersHolder("stabilityai/sdxl-turbo")
        )
    
    def edit_video_with_smart_transitions(
        self,
        clips: list,  # [{'video': path, 'prompt': str}]
        output_path: str,
    ):
        """为视频片段自动添加智能过渡"""
        
        final_segments = []
        
        for i, clip in enumerate(clips):
            # 添加原始片段
            final_segments.append({
                'type': 'video',
                'path': clip['video']
            })
            
            # 如果有下一个片段，生成过渡
            if i < len(clips) - 1:
                transition = self.transition_gen.run_transition()
                final_segments.append({
                    'type': 'transition',
                    'frames': transition
                })
        
        # 使用现有系统合并
        return self.video_ai.concatenate_segments(
            final_segments,
            output_path
        )
```

### 与提示词系统集成

```python
# 如果已有提示词生成系统
class PromptBasedTransitioner:
    """使用 AI 生成的提示词创建过渡"""
    
    def __init__(self, prompt_generator, transition_engine):
        self.prompt_gen = prompt_generator
        self.transition = transition_engine
    
    def create_transition_from_frames(
        self,
        frame1_path: str,
        frame2_path: str,
    ):
        """为两个帧自动生成过渡"""
        
        # 使用提示词生成器分析帧
        prompt1 = self.prompt_gen.describe_image(frame1_path)
        prompt2 = self.prompt_gen.describe_image(frame2_path)
        
        # 生成中间提示词
        intermediate = self.prompt_gen.interpolate_prompts(
            prompt1,
            prompt2,
            steps=3
        )
        
        # 生成过渡
        self.transition.set_prompt1(prompt1)
        self.transition.set_prompt2(prompt2)
        
        return self.transition.run_transition()
```

---

## 部署与 API 设计

### 简单的 REST API

```python
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI()

class TransitionRequest(BaseModel):
    prompt_from: str
    prompt_to: str
    num_frames: int = 10
    quality: str = "balanced"  # mvp, balanced, high

# 全局引擎（避免重复加载模型）
transition_engine = None

@app.on_event("startup")
async def startup():
    global transition_engine
    transition_engine = BlendingEngine(
        DiffusersHolder("stabilityai/sdxl-turbo")
    )

@app.post("/generate_transition")
async def generate_transition(req: TransitionRequest):
    """生成过渡视频"""
    
    # 根据质量设置参数
    quality_config = {
        'mvp': {'depth': 0, 'num_steps': 20},
        'balanced': {'depth': 1, 'num_steps': 30},
        'high': {'depth': 2, 'num_steps': 40},
    }
    
    config = quality_config[req.quality]
    
    transition_engine.set_prompt1(req.prompt_from)
    transition_engine.set_prompt2(req.prompt_to)
    transition_engine.set_branching(
        depth=config['depth'],
        nmb_trans_images=req.num_frames
    )
    
    frames = transition_engine.run_transition()
    
    # 返回视频或帧列表
    return {
        'status': 'success',
        'frame_count': len(frames),
    }
```

### Docker 部署

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app

# 安装依赖
RUN pip install -r requirements.txt

COPY . .

# 预加载模型
RUN python -c "from latentblending.blending_engine import BlendingEngine; \
               from latentblending.diffusers_holder import DiffusersHolder; \
               DiffusersHolder('stabilityai/sdxl-turbo')"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 常见问题解答

### Q: 为什么我的过渡看起来有"幽灵"图像？
A: 这是跨馈送强度过高的表现。降低 `branch1_crossfeed_power` 到 0.2-0.3。

### Q: 内存溢出怎么办？
A: 按优先级尝试：
1. 启用 VAE slicing: `pipe.vae.enable_slicing()`
2. 减少 `nmb_trans_images`
3. 减少 `num_inference_steps`
4. 使用 SDXL Turbo 而非完整 SDXL

### Q: 如何加快速度？
A: 
- 使用 `guidance_scale=5.0` 而非 7.5
- 设置 `depth=0`（无递归分支）
- 减少 `num_inference_steps` 到 20
- 使用 SDXL Turbo

### Q: 过渡与输入帧的关系如何？
A: 输入帧仅作为"指引"，过渡是从噪声重新生成的，使用提示词和跨馈送控制一致性。

### Q: 可以用于实时视频吗？
A: 可以（预处理），不能用于实时流。建议离线生成过渡。

---

## 下一步

1. **集成到项目**：复制上述代码到 `/modules/transition/` 
2. **测试优化**：在目标 GPU 上测试性能
3. **UI 集成**：为用户提供参数预设选择
4. **监控日志**：记录生成时间和内存使用
5. **用户反馈**：收集最喜欢的参数组合

---

**最后更新**: 2025-11-17 | **对应项目**: lunarring/latentblending
