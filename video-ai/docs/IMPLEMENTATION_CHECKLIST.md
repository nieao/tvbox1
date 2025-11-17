# Latent Blending 集成实现清单

## Phase 1：MVP 关键快速检查表

### 周期 1-2：核心集成（第 1-2 周）

- [ ] **依赖安装**
  - [ ] 创建 `requirements_transitions.txt`
  ```
  latentblending @ git+https://github.com/lunarring/latentblending
  diffusers>=0.21.0
  transformers>=4.30.0
  torch>=2.0.0
  torchvision>=0.15.0
  LPIPS @ git+https://github.com/richzhang/PerceptualSimilarity.git#egg=LPIPS
  ```
  - [ ] 安装并测试导入

- [ ] **项目结构调整**
  ```
  video_ai_system/
  ├── modules/
  │   ├── transitions/          # 新建
  │   │   ├── __init__.py
  │   │   ├── generator.py      # 核心生成类
  │   │   ├── config.py         # 参数配置
  │   │   └── utils.py          # 辅助函数
  │   ├── video_processing/
  │   ├── llm/
  │   └── ...
  ├── configs/
  │   └── transitions.yaml      # 转场配置
  └── tests/
      └── test_transitions.py
  ```

- [ ] **创建核心生成器类**
  ```python
  # modules/transitions/generator.py
  
  class LatentBlendingTransitionGenerator:
      """Latent Blending 过渡生成器包装"""
      
      def __init__(self, config_path: str):
          self.config = self._load_config(config_path)
          self.pipe = None
          self.engine = None
          self._initialize()
      
      def _initialize(self):
          """初始化 Latent Blending 引擎"""
          from latentblending.diffusers_holder import DiffusersHolder
          from latentblending.blending_engine import BlendingEngine
          
          self.pipe = DiffusersHolder(
              model_id=self.config['model_id'],
              device=self.config['device']
          )
          self.engine = BlendingEngine(self.pipe)
          self._apply_optimizations()
      
      def _apply_optimizations(self):
          """应用性能优化"""
          self.pipe.vae.enable_slicing()
          self.pipe.unet.enable_attention_slicing()
      
      def generate(
          self,
          prompt_from: str,
          prompt_to: str,
          num_frames: int = 10,
          preset: str = 'balanced'
      ) -> List[PIL.Image]:
          """生成过渡帧"""
          config = self.config['presets'][preset]
          self.engine.set_prompt1(prompt_from)
          self.engine.set_prompt2(prompt_to)
          self.engine.set_branching(
              depth=config['depth'],
              nmb_trans_images=num_frames
          )
          return self.engine.run_transition()
  ```

- [ ] **配置文件创建**
  ```yaml
  # configs/transitions.yaml
  model_id: stabilityai/sdxl-turbo
  device: cuda
  
  presets:
    mvp:
      num_inference_steps: 20
      guidance_scale: 5.0
      guidance_scale_mid_damper: 0.7
      branch1_crossfeed_power: 0.4
      depth: 0
      nmb_trans_images: 5
      estimated_time: 15  # 秒
    
    balanced:
      num_inference_steps: 30
      guidance_scale: 4.5
      guidance_scale_mid_damper: 0.6
      branch1_crossfeed_power: 0.3
      depth: 1
      nmb_trans_images: 10
      estimated_time: 45
    
    high:
      num_inference_steps: 40
      guidance_scale: 3.5
      guidance_scale_mid_damper: 0.5
      branch1_crossfeed_power: 0.25
      depth: 2
      nmb_trans_images: 20
      estimated_time: 120
  
  optimizations:
    enable_vae_tiling: true
    enable_attention_slicing: true
    use_fp16: true
    cache_embeddings: true
  ```

- [ ] **基础单元测试**
  ```python
  # tests/test_transitions.py
  
  import unittest
  from modules.transitions.generator import LatentBlendingTransitionGenerator
  
  class TestTransitionGenerator(unittest.TestCase):
      @classmethod
      def setUpClass(cls):
          cls.gen = LatentBlendingTransitionGenerator(
              'configs/transitions.yaml'
          )
      
      def test_simple_transition(self):
          frames = self.gen.generate(
              "blue sky",
              "sunset",
              num_frames=5,
              preset='mvp'
          )
          self.assertEqual(len(frames), 5)
          self.assertIsNotNone(frames[0])
      
      def test_quality_presets(self):
          for preset in ['mvp', 'balanced', 'high']:
              frames = self.gen.generate(
                  "test1",
                  "test2",
                  preset=preset
              )
              self.assertGreater(len(frames), 0)
  ```

---

### 周期 3：视频集成（第 2-3 周）

- [ ] **视频帧提取模块**
  ```python
  # modules/transitions/video_processor.py
  
  class VideoProcessor:
      @staticmethod
      def extract_frame(video_path: str, frame_idx: int) -> PIL.Image:
          """提取指定帧"""
          import cv2
          cap = cv2.VideoCapture(video_path)
          cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
          ret, frame = cap.read()
          cap.release()
          
          if not ret:
              raise ValueError(f"Cannot extract frame {frame_idx}")
          
          # BGR to RGB
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          return PIL.Image.fromarray(frame)
      
      @staticmethod
      def get_frame_count(video_path: str) -> int:
          """获取视频帧数"""
          import cv2
          cap = cv2.VideoCapture(video_path)
          count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
          cap.release()
          return count
      
      @staticmethod
      def get_fps(video_path: str) -> float:
          """获取视频帧率"""
          import cv2
          cap = cv2.VideoCapture(video_path)
          fps = cap.get(cv2.CAP_PROP_FPS)
          cap.release()
          return fps
  ```

- [ ] **视频片段管理**
  ```python
  # modules/transitions/video_segment.py
  
  class VideoSegment:
      def __init__(self, video_path: str, start: float, end: float):
          self.video_path = video_path
          self.start_sec = start  # 秒
          self.end_sec = end
          self.prompt = None
      
      def set_prompt(self, prompt: str):
          self.prompt = prompt
      
      def get_last_frame(self) -> PIL.Image:
          """获取片段最后一帧"""
          fps = VideoProcessor.get_fps(self.video_path)
          frame_idx = int(self.end_sec * fps) - 1
          return VideoProcessor.extract_frame(self.video_path, frame_idx)
      
      def get_first_frame(self) -> PIL.Image:
          """获取片段第一帧"""
          fps = VideoProcessor.get_fps(self.video_path)
          frame_idx = int(self.start_sec * fps)
          return VideoProcessor.extract_frame(self.video_path, frame_idx)
  ```

- [ ] **过渡序列管理**
  ```python
  # modules/transitions/sequence.py
  
  class TransitionSequence:
      def __init__(self, transition_generator):
          self.gen = transition_generator
          self.segments = []
          self.transitions = []
      
      def add_segment(self, segment: VideoSegment):
          self.segments.append(segment)
      
      def generate_all_transitions(
          self,
          preset: str = 'balanced'
      ) -> List[str]:
          """为所有相邻片段生成过渡"""
          for i in range(len(self.segments) - 1):
              current = self.segments[i]
              next_seg = self.segments[i + 1]
              
              frames = self.gen.generate(
                  current.prompt,
                  next_seg.prompt,
                  preset=preset
              )
              
              transition_path = self._save_transition(frames, i)
              self.transitions.append(transition_path)
          
          return self.transitions
      
      @staticmethod
      def _save_transition(
          frames: List[PIL.Image],
          index: int
      ) -> str:
          """保存过渡为视频"""
          import cv2
          
          path = f"./output/transition_{index:03d}.mp4"
          
          frame_array = [cv2.cvtColor(
              np.array(f),
              cv2.COLOR_RGB2BGR
          ) for f in frames]
          
          h, w = frame_array[0].shape[:2]
          out = cv2.VideoWriter(
              path,
              cv2.VideoWriter_fourcc(*'mp4v'),
              30,  # fps
              (w, h)
          )
          
          for frame in frame_array:
              out.write(frame)
          out.release()
          
          return path
  ```

- [ ] **与现有系统集成**
  ```python
  # 在现有的视频编辑系统中添加过渡支持
  
  from modules.transitions.generator import LatentBlendingTransitionGenerator
  from modules.transitions.sequence import TransitionSequence, VideoSegment
  
  class VideoAISystemWithTransitions:
      def __init__(self):
          self.transition_gen = LatentBlendingTransitionGenerator(
              'configs/transitions.yaml'
          )
      
      def create_video_with_transitions(
          self,
          clips_config: List[Dict],  # [{video, start, end, prompt}]
          output_path: str
      ):
          """创建带过渡的视频"""
          
          # 创建片段序列
          seq = TransitionSequence(self.transition_gen)
          
          for clip_cfg in clips_config:
              segment = VideoSegment(
                  clip_cfg['video'],
                  clip_cfg['start'],
                  clip_cfg['end']
              )
              segment.set_prompt(clip_cfg['prompt'])
              seq.add_segment(segment)
          
          # 生成所有过渡
          transitions = seq.generate_all_transitions(preset='balanced')
          
          # 使用 ffmpeg 合并
          self._concatenate_with_transitions(
              clips_config,
              transitions,
              output_path
          )
      
      @staticmethod
      def _concatenate_with_transitions(
          clips: List[Dict],
          transitions: List[str],
          output: str
      ):
          """使用 ffmpeg 合并片段和过渡"""
          import subprocess
          
          concat_file = '/tmp/concat_list.txt'
          with open(concat_file, 'w') as f:
              for i, clip in enumerate(clips):
                  # 添加原始片段
                  f.write(f"file '{clip['video']}'\n")
                  
                  # 添加过渡（除了最后一个片段）
                  if i < len(transitions):
                      f.write(f"file '{transitions[i]}'\n")
          
          # 运行 ffmpeg
          subprocess.run([
              'ffmpeg',
              '-f', 'concat',
              '-safe', '0',
              '-i', concat_file,
              '-c', 'copy',
              output
          ])
  ```

---

### 周期 4：优化与监控（第 3-4 周）

- [ ] **性能监控**
  ```python
  # modules/transitions/monitor.py
  
  import time
  import torch
  from typing import Dict, List
  
  class PerformanceMonitor:
      def __init__(self):
          self.stats = []
      
      def measure_generation(
          self,
          gen_func,
          *args,
          **kwargs
      ) -> tuple:
          """测量过渡生成的性能"""
          
          # 内存重置
          torch.cuda.reset_peak_memory_stats()
          
          # 计时
          start_time = time.time()
          result = gen_func(*args, **kwargs)
          elapsed_time = time.time() - start_time
          
          # 内存使用
          peak_memory = torch.cuda.max_memory_allocated() / 1e9
          
          stat = {
              'time': elapsed_time,
              'memory': peak_memory,
              'frames': len(result),
              'preset': kwargs.get('preset', 'unknown')
          }
          
          self.stats.append(stat)
          return result, stat
      
      def print_stats(self):
          """打印统计信息"""
          print("Performance Statistics")
          print("=" * 60)
          for i, stat in enumerate(self.stats):
              print(f"Transition {i}:")
              print(f"  Time:     {stat['time']:.2f}s")
              print(f"  Memory:   {stat['memory']:.2f}GB")
              print(f"  Frames:   {stat['frames']}")
              print(f"  Preset:   {stat['preset']}")
          print("=" * 60)
      
      def export_stats(self, path: str):
          """导出为 CSV"""
          import csv
          with open(path, 'w') as f:
              writer = csv.DictWriter(
                  f,
                  fieldnames=['time', 'memory', 'frames', 'preset']
              )
              writer.writeheader()
              writer.writerows(self.stats)
  ```

- [ ] **缓存与预计算**
  ```python
  # modules/transitions/cache.py
  
  import pickle
  from pathlib import Path
  
  class EmbeddingCache:
      def __init__(self, cache_dir: str = './cache'):
          self.cache_dir = Path(cache_dir)
          self.cache_dir.mkdir(exist_ok=True)
      
      def _get_cache_path(self, prompt: str) -> Path:
          import hashlib
          hash_val = hashlib.md5(prompt.encode()).hexdigest()
          return self.cache_dir / f"embedding_{hash_val}.pkl"
      
      def get(self, prompt: str):
          """获取缓存的嵌入"""
          path = self._get_cache_path(prompt)
          if path.exists():
              with open(path, 'rb') as f:
                  return pickle.load(f)
          return None
      
      def set(self, prompt: str, embedding):
          """保存嵌入缓存"""
          path = self._get_cache_path(prompt)
          with open(path, 'wb') as f:
              pickle.dump(embedding, f)
      
      def clear(self):
          """清空缓存"""
          for f in self.cache_dir.glob("embedding_*.pkl"):
              f.unlink()
  ```

- [ ] **日志与错误处理**
  ```python
  # modules/transitions/logger.py
  
  import logging
  from datetime import datetime
  
  class TransitionLogger:
      def __init__(self, log_dir: str = './logs'):
          self.log_dir = Path(log_dir)
          self.log_dir.mkdir(exist_ok=True)
          
          # 创建文件处理器
          log_file = self.log_dir / f"transitions_{datetime.now().isoformat()}.log"
          
          handler = logging.FileHandler(log_file)
          handler.setLevel(logging.DEBUG)
          
          formatter = logging.Formatter(
              '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
          )
          handler.setFormatter(formatter)
          
          self.logger = logging.getLogger('transitions')
          self.logger.addHandler(handler)
      
      def info(self, msg: str):
          self.logger.info(msg)
      
      def error(self, msg: str, exc_info=False):
          self.logger.error(msg, exc_info=exc_info)
      
      def warning(self, msg: str):
          self.logger.warning(msg)
  ```

---

## Phase 2：功能验收标准

### 成功标准

- [ ] **功能验收**
  - [ ] 能够生成 5 帧过渡（MVP 配置）< 20 秒
  - [ ] 生成 10 帧过渡（平衡配置）< 60 秒
  - [ ] 在 12GB+ GPU 上运行无内存溢出
  - [ ] 输出质量主观评价 ≥ 3/5 分

- [ ] **集成验收**
  - [ ] 可以集成到现有视频编辑系统
  - [ ] 支持批量生成（多个过渡）
  - [ ] 配置文件完整可修改
  - [ ] 日志记录完整

- [ ] **文档验收**
  - [ ] API 文档完整
  - [ ] 使用示例清晰
  - [ ] 参数说明详细
  - [ ] 常见问题解答完整

---

## 快速诊断清单

### 如果过渡质量差

1. [ ] 检查 `guidance_scale` 是否过高（应该 < 5.0）
2. [ ] 增加 `num_inference_steps`（尝试 30-40）
3. [ ] 增加 `depth`（尝试 1-2）
4. [ ] 检查提示词是否清晰有意义
5. [ ] 尝试高质量预设而不是 MVP

### 如果速度太慢

1. [ ] 检查 `depth` 是否过高（降低到 0-1）
2. [ ] 减少 `num_inference_steps`（可降到 20）
3. [ ] 启用所有内存优化
4. [ ] 使用 SDXL Turbo 而非完整 SDXL
5. [ ] 减少 `nmb_trans_images`

### 如果内存溢出

1. [ ] 启用 VAE slicing：`pipe.vae.enable_slicing()`
2. [ ] 启用注意力 slicing：`pipe.unet.enable_attention_slicing()`
3. [ ] 减少 `nmb_trans_images` 到 5-8
4. [ ] 使用 fp16 精度
5. [ ] 如果仍然不行，使用 SDXL Turbo

---

## 关键里程碑检查

| 周 | 目标 | 验收标准 |
|----|------|---------|
| 1 | 依赖和基础集成 | 能导入库，运行简单示例 |
| 2 | 核心生成器实现 | 能生成过渡，质量基本可用 |
| 3 | 视频集成 | 能为多个片段生成过渡 |
| 4 | 优化与监控 | 性能稳定，日志完整 |

---

## 部署前检查清单

- [ ] 所有单元测试通过
- [ ] 性能监控数据收集完整
- [ ] 文档已更新
- [ ] 错误处理完善
- [ ] 日志记录正确
- [ ] 缓存机制有效
- [ ] 内存使用在预期范围内
- [ ] API 与现有系统兼容
- [ ] 配置文件已验证
- [ ] 已收集参数优化建议

---

**创建时间**: 2025-11-17 | **状态**: 就绪实现
