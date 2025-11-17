"""
视频过渡效果生成器

支持多种过渡效果类型和文字模板，为阶段二 AI 过渡做准备。
阶段二更新: 集成 AI 过渡生成 (latent blending)
"""

from typing import Literal, Optional, Tuple, List

try:
    from moviepy.editor import (
        VideoFileClip, TextClip, ColorClip,
        CompositeVideoClip, concatenate_videoclips,
        ImageClip
    )
    from moviepy.video.fx.fadeout import fadeout
    from moviepy.video.fx.fadein import fadein
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    # 定义虚拟类，当 MOVIEPY_AVAILABLE 为 False 时不会真正使用
    VideoFileClip = None
    TextClip = None
    ColorClip = None
    CompositeVideoClip = None
    ImageClip = None

# AI 过渡生成器 (阶段二)
try:
    from .ai_transition import AITransitionGenerator, TransitionConfig
    AI_TRANSITION_AVAILABLE = True
except ImportError:
    AI_TRANSITION_AVAILABLE = False
    AITransitionGenerator = None
    TransitionConfig = None

# 延迟导入这些依赖
numpy_available = False
scipy_available = False
pil_available = False
colorsys_available = False

try:
    import numpy as np
    numpy_available = True
except ImportError:
    pass

try:
    from scipy import ndimage
    scipy_available = True
except ImportError:
    pass

try:
    from PIL import Image, ImageDraw, ImageFilter
    pil_available = True
except ImportError:
    pass

try:
    import colorsys
    colorsys_available = True
except ImportError:
    pass


class TransitionGenerator:
    """视频过渡效果生成器 (支持 AI 生成)"""

    SUPPORTED_STYLES = ["text", "fade", "blur", "zoom", "gradient", "ai_generated"]
    SUPPORTED_TEMPLATES = ["minimal", "modern", "classic", "colorful", "info_card"]

    def __init__(
        self,
        transition_style: Literal["text", "fade", "blur", "zoom", "gradient", "ai_generated"] = "text",
        duration: float = 2.0,
        enable_ai: bool = True,
        ai_config: Optional[TransitionConfig] = None
    ):
        """
        初始化过渡生成器

        Args:
            transition_style: 过渡风格 ('text', 'fade', 'blur', 'zoom', 'gradient', 'ai_generated')
            duration: 过渡时长（秒）
            enable_ai: 是否启用 AI 过渡 (阶段二功能)
            ai_config: AI 过渡配置 (可选)
        """
        if transition_style not in self.SUPPORTED_STYLES:
            raise ValueError(
                f"不支持的过渡类型: {transition_style}. "
                f"支持的类型: {self.SUPPORTED_STYLES}"
            )

        self.style = transition_style
        self.duration = duration
        self.moviepy_available = MOVIEPY_AVAILABLE

        # AI 过渡生成器 (阶段二)
        self.ai_generator = None
        self.ai_available = False

        if enable_ai and transition_style == "ai_generated":
            self._init_ai_generator(ai_config)

    def _init_ai_generator(self, ai_config: Optional[TransitionConfig] = None):
        """初始化 AI 过渡生成器"""
        if not AI_TRANSITION_AVAILABLE:
            print("警告: AI 过渡不可用 (未安装依赖)")
            print("请安装: pip install torch diffusers transformers accelerate")
            print("降级到简单文字过渡")
            self.style = "text"
            return

        try:
            self.ai_generator = AITransitionGenerator(
                config=ai_config,
                enable_gpu=True,
                verbose=True
            )
            self.ai_available = True
            print("✓ AI 过渡生成器已启用")
        except Exception as e:
            print(f"警告: AI 过渡初始化失败: {e}")
            print("降级到简单文字过渡")
            self.style = "text"
            self.ai_available = False

    def create_transition(
        self,
        text: Optional[str] = None,
        size: Tuple[int, int] = (1920, 1080),
        template: str = "default",
        prompt_start: Optional[str] = None,
        prompt_end: Optional[str] = None,
        **kwargs
    ):
        """
        创建过渡效果

        Args:
            text: 过渡文字（用于文字类过渡）
            size: 视频尺寸 (宽, 高)
            template: 文字模板名称
            prompt_start: AI 过渡起始提示词 (仅用于 ai_generated)
            prompt_end: AI 过渡结束提示词 (仅用于 ai_generated)
            **kwargs: 额外参数

        Returns:
            过渡视频片段
        """
        # AI 过渡 (阶段二)
        if self.style == "ai_generated":
            return self._create_ai_transition(
                prompt_start, prompt_end, size, **kwargs
            )

        # 传统过渡
        if not self.moviepy_available:
            raise ImportError(
                "请安装依赖: pip install moviepy pillow scipy"
            )

        if self.style == "text":
            if not text:
                text = "继续"
            return self._create_text_transition(text, size, template, **kwargs)
        elif self.style == "fade":
            return self._create_fade_transition(size, **kwargs)
        elif self.style == "blur":
            return self._create_blur_transition(size, **kwargs)
        elif self.style == "zoom":
            return self._create_zoom_transition(size, **kwargs)
        elif self.style == "gradient":
            return self._create_gradient_transition(size, **kwargs)
        else:
            raise ValueError(f"不支持的过渡类型: {self.style}")

    def _create_ai_transition(
        self,
        prompt_start: Optional[str],
        prompt_end: Optional[str],
        size: Tuple[int, int],
        **kwargs
    ):
        """创建 AI 生成的过渡 (阶段二)

        使用 latent blending 技术生成平滑的 AI 过渡效果
        """
        if not self.ai_available or self.ai_generator is None:
            print("警告: AI 过渡不可用，降级到淡入淡出")
            return self._create_fade_transition(size)

        # 验证提示词
        if not prompt_start or not prompt_end:
            raise ValueError("AI 过渡需要提供 prompt_start 和 prompt_end")

        try:
            import numpy as np

            # 计算帧数 (基于持续时间和 FPS)
            fps = kwargs.get('fps', 30)
            num_frames = int(self.duration * fps)

            # 生成 AI 过渡帧
            print(f"生成 AI 过渡: {num_frames} 帧...")
            frames = self.ai_generator.generate_transition(
                prompt_start=prompt_start,
                prompt_end=prompt_end,
                num_frames=num_frames
            )

            # 将 PIL 图像转换为 MoviePy ImageClip 序列
            clips = []
            frame_duration = 1.0 / fps

            for i, frame in enumerate(frames):
                # 调整图像大小到目标尺寸
                if frame.size != size:
                    frame = frame.resize(size, Image.LANCZOS)

                # 转换为 numpy 数组
                frame_array = np.array(frame)

                # 创建 ImageClip
                img_clip = ImageClip(frame_array).set_duration(frame_duration)
                clips.append(img_clip)

            # 拼接所有帧
            from moviepy.editor import concatenate_videoclips
            final_clip = concatenate_videoclips(clips, method="compose")

            return final_clip

        except Exception as e:
            print(f"AI 过渡生成失败: {e}")
            print("降级到淡入淡出")
            return self._create_fade_transition(size)

    def _create_text_transition(
        self,
        text: str,
        size: Tuple[int, int],
        template: str = "default",
        **kwargs
    ):
        """
        创建文字过渡

        支持 5 种文字模板：
        - minimal: 简约风格（白底黑字）
        - modern: 现代风格（渐变背景）
        - classic: 经典风格（黑底白字）
        - colorful: 彩色风格（多彩背景）
        - info_card: 信息卡片风格
        """
        if template == "minimal":
            return self._template_minimal(text, size)
        elif template == "modern":
            return self._template_modern(text, size)
        elif template == "classic":
            return self._template_classic(text, size)
        elif template == "colorful":
            return self._template_colorful(text, size)
        elif template == "info_card":
            return self._template_info_card(text, size)
        else:
            # 默认使用现代风格
            return self._template_modern(text, size)

    def _template_minimal(
        self,
        text: str,
        size: Tuple[int, int]
    ):
        """
        简约风格：白色背景 + 黑色文字 + 简单动画

        特点：
        - 纯白背景
        - 黑色文字
        - 居中显示
        - 淡入淡出效果
        """
        width, height = size

        # 创建白色背景
        bg_clip = ColorClip(
            size=size,
            color=(255, 255, 255)
        ).set_duration(self.duration)

        # 创建文字
        txt_clip = TextClip(
            text,
            fontsize=56,
            color='black',
            font='Arial',
            method='caption',
            align='center',
            size=(width - 200, None)
        ).set_duration(self.duration)

        # 居中位置
        txt_clip = txt_clip.set_position('center')

        # 应用淡入淡出
        txt_clip = txt_clip.fadein(0.5).fadeout(0.5)

        # 合并背景和文字
        final = CompositeVideoClip([bg_clip, txt_clip])
        return final

    def _template_modern(
        self,
        text: str,
        size: Tuple[int, int]
    ):
        """
        现代风格：渐变背景 + 白色文字 + 淡入淡出

        特点：
        - 蓝色到紫色渐变背景
        - 白色文字
        - 简洁现代设计
        - 顺畅的淡入淡出
        """
        width, height = size

        # 创建渐变背景
        gradient_img = self._create_gradient_image(
            width, height,
            color1=(41, 128, 185),    # 蓝色
            color2=(155, 89, 182)      # 紫色
        )

        # 处理可能的 None 返回值
        if gradient_img is None:
            bg_clip = ColorClip(
                size=size,
                color=(100, 100, 180)
            ).set_duration(self.duration)
        else:
            bg_clip = ImageClip(gradient_img).set_duration(self.duration)

        # 创建文字
        txt_clip = TextClip(
            text,
            fontsize=60,
            color='white',
            font='Arial-Bold',
            method='caption',
            align='center',
            size=(width - 200, None)
        ).set_duration(self.duration)

        # 居中位置
        txt_clip = txt_clip.set_position('center')

        # 应用淡入淡出
        txt_clip = txt_clip.fadein(0.5).fadeout(0.5)

        # 合并
        final = CompositeVideoClip([bg_clip, txt_clip])
        return final

    def _template_classic(
        self,
        text: str,
        size: Tuple[int, int]
    ):
        """
        经典风格：黑色背景 + 白色文字 + 居中显示

        特点：
        - 纯黑背景
        - 白色文字
        - 经典简洁
        - 无额外装饰
        """
        width, height = size

        # 创建黑色背景
        bg_clip = ColorClip(
            size=size,
            color=(0, 0, 0)
        ).set_duration(self.duration)

        # 创建文字
        txt_clip = TextClip(
            text,
            fontsize=56,
            color='white',
            font='Arial',
            method='caption',
            align='center',
            size=(width - 200, None)
        ).set_duration(self.duration)

        # 居中位置
        txt_clip = txt_clip.set_position('center')

        # 应用淡入淡出
        txt_clip = txt_clip.fadein(0.5).fadeout(0.5)

        # 合并
        final = CompositeVideoClip([bg_clip, txt_clip])
        return final

    def _template_colorful(
        self,
        text: str,
        size: Tuple[int, int]
    ):
        """
        彩色风格：彩色渐变背景 + 动态文字

        特点：
        - 彩虹渐变背景
        - 白色文字带阴影
        - 充满活力
        - 动态效果
        """
        width, height = size

        # 创建彩虹渐变背景
        gradient_img = self._create_rainbow_gradient(width, height)

        # 处理可能的 None 返回值
        if gradient_img is None:
            bg_clip = ColorClip(
                size=size,
                color=(200, 100, 200)
            ).set_duration(self.duration)
        else:
            bg_clip = ImageClip(gradient_img).set_duration(self.duration)

        # 创建文字（带阴影效果）
        txt_clip = TextClip(
            text,
            fontsize=64,
            color='white',
            font='Arial-Bold',
            method='caption',
            align='center',
            size=(width - 200, None),
            stroke_color='black',
            stroke_width=2
        ).set_duration(self.duration)

        # 居中位置
        txt_clip = txt_clip.set_position('center')

        # 应用淡入淡出
        txt_clip = txt_clip.fadein(0.4).fadeout(0.4)

        # 合并
        final = CompositeVideoClip([bg_clip, txt_clip])
        return final

    def _template_info_card(
        self,
        text: str,
        size: Tuple[int, int]
    ):
        """
        信息卡片风格：卡片式布局 + 多层次设计

        特点：
        - 渐变背景
        - 白色卡片
        - 分层文字
        - 专业设计
        """
        width, height = size

        # 创建渐变背景
        gradient_img = self._create_gradient_image(
            width, height,
            color1=(44, 62, 80),      # 深灰蓝
            color2=(52, 73, 94)        # 灰蓝
        )

        # 处理可能的 None 返回值
        if gradient_img is None:
            bg_clip = ColorClip(
                size=size,
                color=(50, 70, 90)
            ).set_duration(self.duration)
        else:
            bg_clip = ImageClip(gradient_img).set_duration(self.duration)

        # 创建卡片背景
        card_img = self._create_card_image(width, height)
        if card_img is None:
            card_clip = ColorClip(
                size=size,
                color=(200, 200, 200)
            ).set_duration(self.duration)
        else:
            card_clip = ImageClip(card_img).set_duration(self.duration)

        # 创建主文字
        title_lines = text.split('：', 1)
        if len(title_lines) == 2:
            title, subtitle = title_lines
        else:
            title = text
            subtitle = None

        # 标题
        title_clip = TextClip(
            title,
            fontsize=48,
            color='white',
            font='Arial-Bold',
            method='caption',
            align='center',
            size=(width - 400, None)
        ).set_duration(self.duration)

        title_clip = title_clip.set_position(('center', height // 2 - 50))

        # 副标题
        if subtitle:
            subtitle_clip = TextClip(
                subtitle,
                fontsize=36,
                color='#B0BEC5',
                font='Arial',
                method='caption',
                align='center',
                size=(width - 400, None)
            ).set_duration(self.duration)
            subtitle_clip = subtitle_clip.set_position(('center', height // 2 + 50))
            clips = [bg_clip, card_clip, title_clip, subtitle_clip]
        else:
            clips = [bg_clip, card_clip, title_clip]

        # 应用淡入淡出
        for i in range(len(clips)):
            if i > 0:  # 不修改背景
                clips[i] = clips[i].fadein(0.5).fadeout(0.5)

        # 合并
        final = CompositeVideoClip(clips)
        return final

    def _create_fade_transition(
        self,
        size: Tuple[int, int],
        **kwargs
    ):
        """
        创建淡入淡出过渡

        特点：
        - 黑屏淡入淡出
        - 简单流畅
        - 适用于大多数场景
        """
        # 创建黑色片段
        transition = ColorClip(
            size=size,
            color=(0, 0, 0)
        ).set_duration(self.duration)

        return transition

    def _create_blur_transition(
        self,
        size: Tuple[int, int],
        **kwargs
    ):
        """
        创建模糊过渡

        特点：
        - 灰色背景
        - 模糊效果
        - 渐变模糊
        """
        if not pil_available:
            # 如果没有 PIL，返回纯灰色背景
            print("  警告: 缺少 PIL，使用纯灰色背景替代")
            transition = ColorClip(
                size=size,
                color=(128, 128, 128)
            ).set_duration(self.duration)
            return transition

        from PIL import Image, ImageFilter

        # 创建灰色背景
        gray_img = Image.new('RGB', size, color=(128, 128, 128))

        # 应用模糊效果
        gray_img = gray_img.filter(ImageFilter.GaussianBlur(radius=30))

        if numpy_available:
            import numpy as np
            transition = ImageClip(np.array(gray_img)).set_duration(self.duration)
        else:
            # 如果没有 numpy，返回颜色片段
            transition = ColorClip(
                size=size,
                color=(128, 128, 128)
            ).set_duration(self.duration)

        return transition

    def _create_zoom_transition(
        self,
        size: Tuple[int, int],
        **kwargs
    ):
        """
        创建缩放过渡

        特点：
        - 黑色背景
        - 缩放动画
        - 从中心点开始
        """
        # 创建黑色背景
        zoom_clip = ColorClip(
            size=size,
            color=(0, 0, 0)
        ).set_duration(self.duration)

        return zoom_clip

    def _create_gradient_transition(
        self,
        size: Tuple[int, int],
        **kwargs
    ):
        """
        创建渐变过渡

        特点：
        - 平滑的颜色渐变
        - 多色过渡
        """
        width, height = size

        # 创建渐变图像
        gradient_img = self._create_gradient_image(
            width, height,
            color1=(0, 0, 0),      # 黑色
            color2=(64, 64, 64)    # 深灰色
        )

        if gradient_img is None:
            transition = ColorClip(
                size=size,
                color=(32, 32, 32)
            ).set_duration(self.duration)
        else:
            transition = ImageClip(gradient_img).set_duration(self.duration)

        return transition

    def apply_to_clips(
        self,
        clips: list,
        topics: Optional[list] = None
    ) -> list:
        """
        为视频片段之间添加过渡

        Args:
            clips: 视频片段列表
            topics: 主题列表（可选）

        Returns:
            添加过渡后的片段列表
        """
        result = []

        for i, clip in enumerate(clips):
            result.append(clip)

            # 在片段之间添加过渡（除了最后一个）
            if i < len(clips) - 1:
                # 确定过渡文字
                if topics and i + 1 < len(topics):
                    topic = topics[i + 1]
                    transition_text = f"第{i+2}部分: {topic}"
                else:
                    transition_text = f"第{i+2}部分"

                # 创建过渡
                try:
                    transition = self.create_transition(
                        text=transition_text,
                        size=clip.size if hasattr(clip, 'size') else (1920, 1080)
                    )
                    result.append(transition)
                except Exception as e:
                    print(f"  警告: 创建过渡失败 ({e})，跳过")
                    continue

        return result

    def _create_gradient_image(
        self,
        width: int,
        height: int,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int]
    ):
        """创建渐变图像"""
        if not numpy_available:
            print("  警告: 缺少 numpy，使用纯色替代")
            # 返回平均颜色
            avg_color = tuple((c1 + c2) // 2 for c1, c2 in zip(color1, color2))
            if pil_available:
                return Image.new('RGB', (width, height), avg_color)
            return None

        import numpy as np

        # 创建渐变
        gradient = np.linspace(0, 1, width)
        gradient = np.tile(gradient, (height, 1))

        # 应用颜色渐变
        img = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(3):  # RGB 三个通道
            img[:, :, i] = (
                color1[i] * (1 - gradient) +
                color2[i] * gradient
            ).astype(np.uint8)

        return img

    def _create_rainbow_gradient(
        self,
        width: int,
        height: int
    ):
        """创建彩虹渐变图像"""
        if not (numpy_available and colorsys_available):
            # 如果没有这些库，返回渐变代替
            print("  警告: 缺少 numpy 或 colorsys，使用简单彩虹渐变替代")
            return self._create_gradient_image(
                width, height,
                color1=(255, 0, 0),      # 红
                color2=(255, 0, 255)     # 紫
            )

        import numpy as np
        import colorsys

        img = np.zeros((height, width, 3), dtype=np.uint8)

        for x in range(width):
            # 色调从 0 到 1（红 -> 黄 -> 绿 -> 青 -> 蓝 -> 紫 -> 红）
            hue = x / width

            for y in range(height):
                # 饱和度和明度根据高度变化
                saturation = 0.8 + 0.2 * (y / height)
                value = 0.8 + 0.2 * (1 - y / height)

                # 转换为 RGB
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
                img[y, x] = [int(r * 255), int(g * 255), int(b * 255)]

        return img

    def _create_card_image(
        self,
        width: int,
        height: int
    ):
        """创建卡片背景图像"""
        if not pil_available:
            print("  警告: 缺少 PIL，使用白色背景替代")
            if numpy_available:
                import numpy as np
                return np.ones((height, width, 3), dtype=np.uint8) * 200
            return None

        from PIL import Image, ImageDraw

        # 使用 PIL 创建卡片
        card_size = (width - 200, height - 300)
        card_x = 100
        card_y = 150

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制白色卡片
        draw.rounded_rectangle(
            [(card_x, card_y), (card_x + card_size[0], card_y + card_size[1])],
            radius=20,
            fill=(255, 255, 255, 200),
            outline=(200, 200, 200, 200),
            width=2
        )

        # 转换为 RGB 数组
        if numpy_available:
            import numpy as np
            return np.array(img.convert('RGB'))
        return img


if __name__ == "__main__":
    print("TransitionGenerator 模块已加载")
