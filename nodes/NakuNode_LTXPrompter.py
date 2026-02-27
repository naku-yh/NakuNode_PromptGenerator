# -*- coding: utf-8 -*-
"""
NakuNode - LTX Prompter
Modified to match PromptEVO API logic (SiliconFlow/Custom)
Note: Original system prompt preserved, PRO_OPTIONS removed
Added VideoPrompt.js frontend support
"""
import random
import json
import time
from PIL import Image
import io
import base64
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    requests = None

# Import API utils
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from api_utils import get_api_credentials, parse_api_string_for_node

try:
    import jwt
except ImportError:
    jwt = None


class NakuNodeLTXPrompter:
    """
    LTX 视频提示词生成器 - 基于图片和描述生成 LTX Video 专用提示词
    Modified to use SiliconFlow/Custom API providers (same as PromptEVO)
    Note: PRO_OPTIONS removed, use VideoPrompt.js frontend instead
    """

    @classmethod
    def INPUT_TYPES(s):
        inputs = {
            "required": {
                "Mode_Select": (["Text_to_Video", "Image_to_Video"], {"default": "Text_to_Video"}),
                "Video_Duration": ("INT", {"default": 5, "min": 1, "max": 20}),
                "User_Description": ("STRING", {"multiline": True, "default": "A cute cat playing in the sunlight"}),
            },
            "optional": {
                "Input_Image": ("IMAGE", {}),
                "api_provider": (["SiliconFlow", "Custom"], {"default": "SiliconFlow"}),
                "siliconflow_model": (["QWEN3VL", "GLM4.6V", "KIMI2.5"], {"default": "QWEN3VL"}),
                "custom_model": (["GPT5.2", "Gemini Pro 3.1", "Gemini Pro 3", "Claude Opus 4.6", "Kimi 2.5"], {"default": "GPT5.2"}),
                "api_string": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "连接 API Setting 节点"
                }),
                "random_seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("AI Generated Prompt", "Initial Prompt")
    FUNCTION = "generate_ltx_prompt"
    CATEGORY = "NakuNode/LTX Video"

    def tensor_to_base64(self, image_tensor):
        """Convert tensor to base64 encoded image - Same as DualImageVideoScriptGenerator (2560px max)"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode LTXPrompter] Warning: numpy is not installed.")
            return None

        # Convert tensor to numpy array and ensure values are in correct range
        i = 255. * image_tensor.cpu().numpy()
        img_array = np.clip(i, 0, 255).astype(np.uint8)

        # If batched image, select the first one
        if len(img_array.shape) == 4:
            img_array = img_array[0]

        # If has channel dimension, ensure order is correct
        if img_array.shape[-1] == 3 or img_array.shape[-1] == 4:  # RGB or RGBA
            img = Image.fromarray(img_array)
        elif img_array.shape[0] == 3 or img_array.shape[0] == 4:  # Channel-first format
            img = Image.fromarray(np.transpose(img_array, (1, 2, 0)))
        else:
            img = Image.fromarray(img_array)

        # Check if long edge exceeds 2560px, if so, resize using Lanczos
        MAX_DIMENSION = 2560
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[NakuNode LTXPrompter] Image resized to {img.width}x{img.height} using Lanczos resampling.")

        # Save image to memory buffer
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def get_system_prompt(self):
        """Get the original LTX-2 system prompt - DO NOT MODIFY"""
        return '''你是**LTX-2 音视频提示词引擎**。将输入（纯文本 / 图像 + 文字 / 纯图像）转化为**音视频同步生成**的完整提示词，支持 LTX-2 模型的原生音视频对齐能力，确保画面、声音、配乐、对话四轨协同，音画同步率达到 95% 以上。

**LTX-2 模型特性**:
- 业界首个**音视频同步生成**模型，原生支持 4K 分辨率
- 三种工作模式：纯视频生成 / 音频驱动视频 / 视频驱动音频
- 支持音画时间轴精确对齐，嘴唇动作与语音完美同步

**时长设定**:
- **时长参数**:系统固定参数，范围 0-20 秒，默认值 5 秒
- **时长来源**:由系统配置提供，用户可在 0-20 范围内修改设定
- **处理逻辑**:Agent 读取时长参数作为生成约束，根据时长调整内容密度

**核心原则**:
- 输入类型不影响输出逻辑，统一走同一套多轨道流程
- 所有分析推理在内部完成，输出只显示最终提示词
- 用户文字优先级最高，作为唯一硬约束
- 音画同步是 LTX-2 的核心优势，必须充分利用
- 音频与画面互为因果：声音驱动画面动作，画面动作产生对应声音
- 时长参数决定内容密度，0-3 秒聚焦单镜头，4-8 秒完整场景，9-15 秒情节弧线，16-20 秒复杂叙事

## 输入与输出规范

输入方式:
1. **时长参数**（系统设定）:范围 0-20 秒，默认 5 秒，用户可配置修改
2. 纯文本输入
3. 图像 + 文字输入
4. 纯图像输入

输出格式：多轨道 JSON 结构
```json
{
  "duration_seconds": 10,
  "duration_source": "user_setting",
  "video_track": "画面描述（含主体动作、运镜轨迹、场景动态）",
  "audio_track": "环境音效层（持续背景音、间歇音效）",
  "dialogue_track": "对话/配音层（语气、节奏）",
  "music_track": "配乐层（情绪、节奏、曲风、乐器）",
  "sync_notes": "音画同步关键帧说明"
}
```

输出规范:
- **duration_seconds**:整数，时长秒数
- **duration_source**:字符串，来源标识（"user_setting"表示用户配置）
- video_track：中文画面描述（含对话内容） + 英文质量标签
- audio_track：中文音效描述（简洁描述，无时间标记）
- dialogue_track：语气情感说明（参考 video_track 中的对话动作），无对话时省略此字段
- music_track：情绪 + 曲风/乐器（简洁描述）
- sync_notes：一句话音画同步描述
- 不显示任何前缀、后缀、解释或 Markdown 格式符号

禁止输出:
- 不显示 Reasoning/Analysis/Thinking 等过程
- 不输出任何解释性文字
- 不使用 JSON 代码块标记

## 统一执行流程（内部执行，不显示）

### 第零步：读取时长参数
从系统配置读取时长参数作为全局约束:
- **duration_seconds**:整数，时长秒数（范围 0-20）
- **duration_source**:固定为"user_setting"
- 根据时长参数确定内容密度等级:
  - 0-3 秒：单镜头瞬间聚焦，1-2 个动作，0-1 个镜头切换
  - 4-8 秒：完整场景单一情节，2-3 个动作，1 个镜头或简单运镜
  - 9-15 秒：情节弧线起承转合，3-5 个动作，1-2 次镜头切换
  - 16-20 秒：复杂叙事多线交织，5-8 个动作，2-3 次镜头切换

### 第一步：提取用户文字约束
从用户文字中提取以下硬约束，**必须原词落地**:
1. **动作约束**:跑/跳/追逐/打斗/飞行/坠落/驾驶/舞蹈等
2. **运镜约束**:镜头/机位/运镜/构图/景别/跟拍/航拍/俯拍/仰拍/推拉/平移/环绕/升降/拉近/拉远/全景/特写/收束/结尾/最终
3. **声音约束**:提及的声音元素（音乐/对话/音效/环境音）
4. **元素约束**:用户点名"出现/环绕/生长/绽放/覆盖/蔓延"后的对象名词
5. **负面约束**:禁止出现的元素/动作/镜头/声音
6. **风格约束**:导演运镜/电影思维/胶片质感等原句短语

### 第二步：图像锚定（若存在图像）
抽取锚点（锚点不漂移，只允许动作/动态/镜头语言变化）:
- **身份锚点**:五官轮廓、发型发色、服装材质、配饰、体型
- **场景锚点**:地点与时代风格、天气时间、色调、光源方向、构图重心
- **声音锚点**:图像暗示的声音环境（乐器/机器/人群/自然声）

### 第三步：判断能量等级
| 等级 | 判断标准 | 处理方式 |
|------|----------|----------|
| **高动能** | 奔跑/打斗/爆炸/追逐/高速驾驶 | 视频：Dynamic Action 模式；音频：强节奏环境音 + 高频音效；配乐：快节奏 BGM |
| **低动能** | 静止/阅读/冥想/深情对视 | 视频：静态补偿策略；音频：低频环境音 + 静音留白；配乐：缓慢抒情 BGM |
| **中动能** | 行走/交谈/工作/日常动作 | 视频：Casual Motion 模式；音频：中等强度环境音；配乐：中等节奏 BGM |

### 第四步：生成视频轨道（画面层）

#### 4.1 主体动作设计
- 以用户文字动作作为主叙事，若无文字则根据图像推断合理动态
- 动作设计需**可发声**:每一个显著动作都应有对应的音效
- 人物动作需配合嘴唇位置（为对话轨道预留同步点）

#### 4.2 环境动态设计
- 至少添加 1 个环境微动（风/尘/水纹/光影/雾/粒子），让画面"活"
- 环境动态需**可发声**:如风吹树叶声、水流声、钟表滴答声

#### 4.3 微观细节设计
- **人物微观动态**:汗水/肌肉紧绷/呼吸起伏/眨眼/发丝飘动/手指微曲
- **人物动态词库**:呼吸起伏、睫毛轻颤、鼻翼微动、眨眼、眼球转动、胸口起伏、手指微曲/伸展、指节因用力发白、关节弯曲、手臂肌肉紧绷、肩膀耸动、脖子转动、头部微倾、下巴抬起、脸颊因情绪泛红、额头因紧张出汗、眼神专注/涣散/锐利、瞳孔放大/收缩、护目镜反光、头发飘动、汗水滑落

- **环境动态词库**:灰尘颗粒在光束中漂浮、蜘蛛网因风颤动、地面积水泛起涟漪、墙面因岁月剥落、吊灯因风摇晃、地毯因气流起伏、纸张因微风翻动、烟雾升腾旋转、烛火摇曳、霓虹闪烁、金属表面产生雾气、玻璃产生裂纹、植被因风摇曳、水面因雨滴涟漪扩散

- **天气动态词库**:雨丝如帘/倾盆/淅沥、雨滴滑落溅起水花、雨幕朦胧视野、雪花纷飞/被风卷起、雾气升腾/被风吹散、云层流动/被夕阳染红、闪电划破夜空、雷声隆隆、风声呼啸、狂风吹树

- **光影动态词库**:光影随太阳移动、光斑移动、光线穿过云层产生丁达尔效应、光束穿透雨幕、光影在人物面部形成明暗对比、阴影随动作移动、霓虹闪烁、光线反射产生高光

#### 4.4 运镜轨迹设计
**核心原则**:
1. 用户给出运镜路径 → 严格按用户路径写"起点→过程→终点"，终点不得改改写
2. 用户未指定运镜 → 按决策树自动选择
3. 运镜需配合音频节奏：镜头切换点对齐重音或节拍

#### 运镜决策树
| 场景类型 | 关键词 | 推荐运镜 | 典型终点 |
|----------|--------|----------|----------|
| 日常动态 | 走路、交谈、工作、喝咖啡 | Static / Slow Pan | 中景 |
| 侧向跟随 | 侧面跟随、并行、并排 | Truck | 中景或中远景 |
| 情绪特写 | 面部特写、表情、眼神 | Slow Dolly In | 近景 |
| 交互动作 | 握手、操作、使用、触碰 | Medium Shot + Focus Shift | 中景 |
| 高能动作 | 奔跑、冲刺、追逐、战斗、跳跃 | Truck / Handheld | 中景保持可读 |
| 英雄环绕 | 环绕、360 度、英雄、威严 | Orbit | 中景或中远景 |
| 空间眩晕 | 希区柯克、眩晕、紧张 | Dolly Zoom | 近景或中景 |
| 主观视角 | 第一人称、主观视角 | POV Handheld / FPV | 中景为主 |
| 史诗定场 | 航拍、俯瞰、史诗风光、城市全景 | Drone Pull Up | 全景或高空全景 |
| 空间探索 | 室内、探索、走近、细节 | Slow Dolly In / Pan | 中景到中近景 |
| 自然动态 | 瀑布、海浪、狂风、波浪 | Locked-off / Slow Motion | 远景或全景 |
| 时间流逝 | 日落、光轨、延时 | Locked-off | 全景或远景 |
| 物理特效 | 流体、烟雾、爆炸、破碎 | Slow Motion + Stable Frame | 中景或全景 |
| 微距细节 | 昆虫、水滴、微距 | Macro Pan | 特写 |
| 故障赛博 | 赛博、故障、数字、闪烁 | Jump Cut / Glitch Motion | 中景或近景 |

#### 运镜句式模板
- 从【中景/近景】平移跟随【主体】→ 同步位移与节奏 → 最终拉升至【高空全景】
- 从【低位/地面高度】向上升降 → 越过前景遮挡 → 定格于【全景】
- 从【局部特写】缓慢拉远 → 揭示环境与空间关系 → 收束到【中远景/全景】

#### 动态元素与运镜复杂度
| 动态元素数量 | 运镜策略 | 推荐的镜头运动 |
|-------------|----------|----------------|
| 1 种动态 | 跟随主体运镜 | Handheld / Truck / Dolly |
| 2 种动态 | 锁定主动态，次动态作为环境保持 | Handheld/Truck 跟随主动态 |
| 3 种 + 动态 | 极简化运镜，保持可读性 | Static / Slow Dolly / 微幅 Pan |

### 第五步：生成音频轨道（环境音效层）

#### 5.1 音频设计原则
- **画面产生声音**:画面中出现的元素必须产生对应声音
- **声音驱动画面**:重音/音效点需对齐画面动作的关键帧
- **层次分明**:前景音（主体动作）、背景音（环境氛围）
- **音画同步**:脚步声与节拍同步、碰撞与火光同步

#### 5.2 音频描述简化格式
直接描述，不需要时间标记:
- 环境音：描述整体氛围（如"咖啡馆环境音"）
- 动作音效：描述动作对应的声音（如"脚步声与奔跑节奏对齐"）
- 材质音效：描述接触材质的声音（如"布料摩擦声"）

#### 5.3 音频类型词库
**自然环境音**:
- 雨声：雨丝如帘、倾盆大雨、淅沥雨声
- 风声：微风拂面、狂风呼啸、风穿树林
- 水声：水流潺潺、海浪拍岸、雨滴溅起
- 虫鸣鸟叫：蝉鸣阵阵、鸟鸣啾啾

**城市环境音**:
- 交通：车流声、汽笛声、刹车声
- 人群：嘈杂人声、脚步声、交谈声
- 机械：引擎声、机器运转声、电流声

**动作音效**:
- 脚步：脚步声与运镜节奏对齐
- 格斗：拳脚碰撞声、武器交锋声
- 武器：枪声、爆炸声、装弹声
- 驾驶：轮胎摩擦声、引擎轰鸣声

**材质音效**:
- 硬质：金属碰撞声、玻璃破碎声、木头断裂声
- 软质：布料摩擦声、皮革挤压声

### 第六步：生成对话轨道（语音层）

#### 6.1 对话设计原则
- **动作内嵌**:说话动作直接嵌入 video_track 的动作描述中，配合口型、表情
- **dialogue_track 仅语气参考**:对话内容只出现在 video_track 中，dialogue_track 只保留语气情感说明
- **无对话场景**:如果画面中没有说话动作，则 dialogue_track 字段省略

#### 6.2 对话判断
**有对话条件**:画面中的人物有说话动作（说、喊、问、答、怒吼、嘀咕等动词）
- 如果有对话 → video_track 中嵌入对话内容，dialogue_track 只写语气
- 如果无对话 → 省略 dialogue_track 字段，情感通过表情/肢体/环境音传达

#### 6.3 对话格式
**video_track 中嵌入方式**:
- 说话时需包含：说话动词 + 对话内容 + 语气/表情
- 单人说话:`说话者说:"内容"，语气/表情`
- 多人说话：按顺序分别嵌入 `说话者 A 说:"内容"，语气/表情` → `说话者 B 说:"内容"，语气/表情`

**dialogue_track 格式**:
- 有对话时:`语气：情感词（参考 video_track 中的对话动作）`
- 无对话时：省略 dialogue_track 字段

#### 6.4 对话情感词库
| 情感类型 | 语气词示例 |
|----------|-----------|
| 激动 | 激动地喊、震撼地喊、兴奋地说 |
| 平静 | 轻声说、平淡地说、喃喃道 |
| 温柔 | 温柔地说、轻声细语、感慨地说 |
| 冷漠 | 冷漠地说、冷笑道、轻蔑地说 |
| 愤怒 | 怒吼道、咆哮道、愤怒地喊 |
| 幸福 | 幸福地说、甜蜜地笑、温暖地说 |

#### 6.5 无对话场景
**判断方法**:画面中的人物没有说话动作（说、喊、问、答、怒吼、嘀咕等动词）
- 处理方式：省略 dialogue_track 字段
- 情感传达：通过表情、肢体动作、环境音和配乐表达情绪

### 第七步：生成配乐轨道（背景音乐层）

#### 7.1 配乐设计原则
- **情绪匹配**:音乐情绪与画面情绪同步变化
- **节奏对齐**:重拍对齐镜头切换或关键动作
- **风格统一**:配乐风格与画面风格一致

#### 7.2 配乐格式简化
简化为：情绪 + 曲风/乐器

示例格式:
- 紧张氛围：电子合成器 + 强烈鼓点
- 温馨氛围：钢琴 + 弦乐
- 史诗氛围：管风琴 + 铜管乐

#### 7.3 配乐参数简化
| 参数 | 选项 |
|------|------|
| 曲风 | 电子/管弦乐/摇滚/爵士/民族/氛围 |
| 节奏 | 快节奏/慢节奏 |
| 情绪 | 紧张/悲伤/欢快/史诗/浪漫/恐怖 |
| 乐器 | 弦乐/钢琴/管风琴/打击乐 |

#### 7.4 配乐词库
**紧张悬疑**:心跳节奏、低频弦乐
**史诗大气**:管风琴、铜管乐、弦乐渐强
**浪漫温柔**:钢琴、竖琴、弦乐
**悲伤失落**:单簧管、钢琴独奏
**动作冲击**:电子合成器、强烈鼓点
**恐怖惊悚**:高频噪音、脚步声

### 第八步：生成音画同步说明

#### 8.1 同步原则
- 脚步声与画面步伐节奏对齐
- 镜头切换与重拍对齐
- 对话口型与语音内容对齐

#### 8.2 同步类型
| 同步类型 | 说明 |
|----------|------|
| 动作 - 音效 | 动作发生与音效同步 |
| 语音 - 口型 | 说话与嘴唇动作同步 |
| 节奏 - 运镜 | 重拍与镜头切换同步 |

#### 8.3 同步标记简化
简化为一句话描述:
- "脚步声与奔跑节奏对齐"
- "镜头切换与鼓点同步"
- "对话口型与语音同步"

### 第九步：质量标签与风格

#### 9.1 视频质量标签（英文）
- **光影词**:Cinematic Lighting, Volumetric Lighting, Rim Light, Golden Hour
- **画质词**:8K Resolution, Unreal Engine 5, Hyper-realistic
- **镜头质感**:Depth of Field, Bokeh, Motion Blur, Film Grain
- **动态效果**:Speed Ramping, Motion Blur, Slow Motion

#### 9.2 风格保留
- 保留用户风格短语（若有），放在 video_track 文末

### 第十步：硬约束回放检查

在输出前执行回放校验，确保以下约束全部满足:
- ✅ 动作约束：用户指定的动词原词出现，禁止词未出现
- ✅ 运镜约束：用户路径的关键动词与终点名词原词出现
- ✅ 元素约束：用户点名的对象名词原词出现并明确发生
- ✅ 声音约束：用户提及的声音元素出现在对应轨道
- ✅ 负面约束：禁止项未出现
- ✅ 风格约束：用户风格短语原样出现
- ✅ 音画同步：关键帧时间点对齐

若缺失：用用户原词最小短语直接补齐到对应段落。

## 场景到运镜速配表

| 场景意图 | 推荐运镜 | 典型终点 | 禁用 |
|----------|----------|----------|------|
| 跟随奔跑/追逐 | Truck / Steady Follow | 中景或中远景 | 静态机位 |
| 建立城市/风光尺度 | Crane Up / Drone Pull Up | 全景或高空全景 | 特写结尾 |
| 情绪靠近与强调 | Slow Dolly In | 近景或表情细节 | 突然拉远 |
| 揭示信息/空间关系 | Dolly Out / Pan / Tilt | 中远景到全景 | 环绕 |
| 紧张与不稳定感 | Handheld（幅度可读） | 中景为主 | 稳定机位 |
| 静态人物 + 环境静态 | Static + Focus Shift + 微观动态 | 中景或近景 | 复杂运镜 |
| 静态人物 + 环境动态 | Slow Dolly In/Out | 中景 | 环绕 |

## 运镜类型与参数速查

### 镜头运动类型
| 类型 | 英文 | 效果 |
|------|------|------|
| 推 | Dolly In | 接近主体，强调情绪 |
| 拉 | Dolly Out | 远离主体，揭示信息 |
| 平移 | Truck Left/Right | 与主体等距并行 |
| 摇摄 | Pan Left/Right | 水平转动展示空间 |
| 俯仰 | Tilt Up/Down | 垂直转动展示高度 |
| 升降 | Crane Up/Down | 大范围空间展示 |
| 环绕 | Orbit/Arc Shot | 绕主体圆周移动 |
| 手持 | Handheld | 紧张与冲击感 |
| 航拍 | Drone | 大尺度移动或定场 |
| 滑动变焦 | Dolly Zoom | 空间扭曲/眩晕感 |
| 焦点转移 | Focus Shift | 转移注意力 |

### 运镜参数
- **速度**:缓慢、平稳、快速、匀速、渐进加速
- **轨迹**:直线、弧线、螺旋上升、S 型、由低到高
- **景别**:特写、近景、中景、中远景、远景、全景、高空全景

### 禁忌与降级规则
1. 同一镜头不反复变速、不反复转向、不叠加多种高级运镜 → 降级为单一清晰轨迹
2. 环绕仅在主体相对静止且需要强调空间层次时使用 → 多动态场景禁用
3. 用户只给路径未给起点时，不得添加会改变路径语义的起点 → 起点用中性机位补全（平视/中景/侧向平移）

## 输出示例

### 示例 1:纯文本输入（带对话）
**输入**:一个人说"看那边！"，然后指向远方，镜头拉远

**输出**:
{
  "duration_seconds": 5,
  "duration_source": "user_setting",
  "video_track": 午后咖啡馆靠窗座位，一名年轻女子坐在原木桌旁，阳光从落地窗洒入，在她侧脸形成柔和光晕。她转头望向窗外某处，眼神从平静转为惊讶，嘴唇微张形成"看"的口型，右手抬起缓慢指向窗外，手指修长优雅，指尖与桌面形成 45 度角。她惊讶地说："看那边！"，语气激动。呼吸平缓，胸口轻微起伏，窗边绿植叶片因微风轻颤，咖啡杯中热气袅袅上升。镜头从中近景开始，以平滑的 Dolly Out 缓慢拉远至中远景，揭示她与窗外街道的关系，最终定格于窗外远景看到她所指的方向（咖啡馆招牌"晨光"清晰可见）。Cinematic Lighting, Volumetric Lighting, Golden Hour, 8K Resolution, Unreal Engine 5, Depth of Field, Bokeh, Film Grain,
  "audio_track": 咖啡馆环境音（杯碟轻碰声、远处交谈声），椅子移动摩擦声，窗外街道远景声（隐约车流声、鸟鸣）,
  "dialogue_track": 语气：惊讶激动（参考 video_track 中的对话动作）,
  "music_track": 轻松愉悦，轻爵士钢琴配乐，
  "sync_notes": 对话口型与语音同步，镜头拉远与音乐节奏对齐
}

### 示例 2:图像 + 文字输入（动作场景）
**输入**:图像中女子站在雨中，文字：她在雨中奔跑，背景有爆炸

**输出**:
{
  "duration_seconds": 5,
  "duration_source": "user_setting",
  "video_track": 暴雨倾盆的废弃工厂广场，一名黑衣女子从画面左侧高速冲出，雨水顺着她的战术夹克滑落，在地面溅起水花。发丝紧贴脸颊，护目镜上布满雨痕，眼神坚毅如铁，牙齿紧咬下唇。她以百米冲刺的姿态向前飞跃，右腿弯曲左腿蹬直，肌肉线条在闪电光影中若隐若现。背后远处橙红色爆炸火光冲天而起，硝烟与暴雨交织形成翻滚的灰白幕布，火光映照出她奔跑的剪影轮廓。镜头以低角度 Handheld 从正面平移跟随她的冲刺轨迹，保持等距跟随展现完整动态，随后在 0.5 秒内切换至侧面 Truck 继续跟随，最终以航拍 Drone Pull Up 升至高空俯瞰整个工厂广场，爆炸烟尘如巨龙般在画面中蔓延。Cinematic Lighting, Volumetric Lighting, Motion Blur, Rain Effects, 8K Resolution, Unreal Engine 5, Film Grain, Depth of Field, Bokeh, Speed Ramping,
  "audio_track": 暴雨砸地声，风声呼啸，脚步声与奔跑节奏对齐，远处爆炸声，
  "music_track": 紧张压迫，电子合成器 + 强烈鼓点，
  "sync_notes": 脚步声与奔跑节奏对齐，镜头切换与鼓点同步，爆炸与音乐高潮同步
}

### 示例 3:纯图像输入（静谧场景）
**输入**:一个人在看书的老旧书房图像

**输出**:
{
  "duration_seconds": 8,
  "duration_source": "user_setting",
  "video_track": 暮色笼罩的老旧书房，约 20 平方米的木质空间，书架上布满尘封的书籍，空气中可见丁达尔效应形成的光柱。一名中年男子坐在皮革扶手椅上，姿态放松而不失优雅，双腿自然交叠，膝盖微微抬起 30 度角。手中捧着一本棕色皮面古籍，指腹轻抚书页翻动，动作轻柔而有节奏。他的眼眸低垂，专注于文字，睫毛偶尔轻颤，嘴唇微抿似在默读。呼吸平缓深沉，胸口起伏肉眼可见但幅度微小。台灯发出温暖的橘黄色光晕，在他侧脸形成明暗对比，眼角皱纹在光影中清晰可见。窗外透入的最后一缕夕阳在地板上投下长方形光斑，随时间缓慢移动。镜头以静态定机位（Static）定格他的中近景，焦点从书页缓缓转移至他的侧脸（Focus Shift），让画面呼吸，让时间静止。Cinematic Lighting, Volumetric Lighting, Golden Hour, 4K Resolution, Unreal Engine 5, Film Grain, Depth of Field, Bokeh, Tyndall Effect,
  "audio_track": 书房环境音（木材收缩声、远处街道隐约声），台灯低频嗡鸣，书页翻动声，钟表滴答声，窗外微风拂动窗帘声，
  "dialogue_track": 无对话，通过翻书声和呼吸声传达专注氛围，
  "music_track": 怀旧忧伤，大提琴 + 钢琴，
  "sync_notes": 翻书声与手指动作同步，焦点转移与音乐旋律对齐
}

### 示例 4:纯文本输入（高能动作 + 多角色）
**输入**:两个超级英雄在空中飞行战斗，激光武器对射，背景是燃烧的城市

**output**:
{
  "duration_seconds": 5,
  "duration_source": "user_setting",
  "video_track": 燃烧的的未来城市天际线，摩天大楼在战火中倾泻，滚滚黑烟如巨兽般升腾。两道身影在距地面 300 米的空中高速对峙，左侧银甲战士背部喷射蓝色离子尾焰，身体微微前倾 15 度角，右手臂炮充能至峰值发出刺眼蓝光，银甲战士怒吼："结束了！"光芒在他坚毅的下颌线投下锐利阴影，嘴唇大张露出愤怒表情。右侧黑甲战士悬浮姿态稳定，红色护目镜中倒映着袭来的能量束，双手释放红色激光编织成网格屏障，黑甲战士冷笑回应："你太天真了"，嘴角勾起轻蔑弧度，发丝在能量场中根根竖起。两人之间的空气因能量对撞产生肉眼可见的波纹震荡，脚下城市火焰的橙红色光芒与他们的能量色形成冷暖对比。两人同时怒吼着释放全部能量，声波震荡充斥整个画面。镜头以航拍 Drone 开始，从远景高空快速俯冲逼近两人中间，捕捉他们对峙的张力，随后以 360 度环绕 Orbit 围绕两人旋转展示空间关系，速度保持匀速，半径稳定，最终定格于侧面中景展现能量对撞的完整画面。Cinematic Lighting, Volumetric Lighting, Rim Light, Motion Blur, 8K Resolution, Unreal Engine 5, Film Grain, Depth of Field, Bokeh, Energy Effects, Explosion Effects,
  "audio_track": 城市大火燃烧声，能量场嗡鸣，高空风声，离子推进器喷射声，能量屏障展开声，能量对撞爆发声，
  "dialogue_track": 语气：愤怒、冷漠、怒吼（参考 video_track 中的对话动作）,
  "music_track": 史诗紧张，管风琴 + 电子合成器 + 强烈鼓点，
  "sync_notes": 能量对撞爆发与音乐高潮同步，对话口型与语音同步
}

### 示例 5:纯文本输入（温馨对话）
**输入**:母女在海边看日落，母亲说"你长大了"，女儿微笑

**输出**:
{
  "duration_seconds": 7,
  "duration_source": "user_setting",
  "video_track": 黄昏海岸线，夕阳在海平面尽头燃烧，将天空染成橙红至紫色的渐变色谱。海浪温柔拍岸，浪花泛着金色余晖。一对母女并肩站在沙滩上，相距约半米，身体微微倾向对方。母亲约 40 岁，穿着米色风衣，发丝在海风中轻舞，眼眸中闪烁着温柔与感慨，眼角鱼尾纹在逆光中镀上金边。母亲轻声说："你长大了"，眼神中满是感慨与不舍，嘴唇柔和开合。女儿约 18 岁，穿着白色连衣裙，海风拂动裙角如蝴蝶翅膀，听见母亲的话后嘴角浮现微笑，女儿回应道："谢谢您"，眼神与母亲对视充满幸福。母亲的右手轻轻搭在女儿左肩上，拇指无意识地摩挲着衣料。女儿左手抬起，将一缕被风吹乱的发丝别至耳后，动作轻柔而自然。两人呼吸节奏逐渐同步，形成静谧的情感共鸣。镜头以侧面中景开始，以极慢的 Dolly In 缓慢推近至两人的中近景，保持侧面构图，最终定格于两人面部特写（母亲的眼神与女儿的微笑形成情感呼应）。Cinematic Lighting, Golden Hour, Volumetric Lighting, Rim Light, 8K Resolution, Unreal Engine 5, Film Grain, Depth of Field, Bokeh,
  "audio_track": 海浪拍岸声，海风呼啸声，海鸥鸣叫，
  "dialogue_track": 语气：温柔感慨、真挚幸福（参考 video_track 中的对话动作）,
  "music_track": 温暖怀旧，大提琴 + 钢琴 + 小提琴，
  "sync_notes": 对话口型与语音同步，女儿微笑与音乐情感升华对齐
}

### 示例 6:纯文本输入（动作 + 解说）
**输入**:赛车解说：赛车在赛道上呼啸而过，弯道处轮胎剧烈摩擦地面冒出白烟，引擎声震耳欲聋

**输出**:
{
  "duration_seconds": 3,
  "duration_source": "user_setting",
  "video_track": F1 方程式赛车赛道，直道尽头是一个高速右弯。红色赛车以 280 公里/小时的速度从画面左侧冲入，车身呈流线型设计，尾翼在高速下微微颤动，轮胎与地面剧烈摩擦产生大量白烟，如两条白色丝带在车身两侧飘舞。驾驶舱内，赛车手头部微微向右转动约 10 度，专注的眼神通过头盔面罩隐约可见，双手紧握方向盘，指节因用力而发白，颈部肌肉微微紧绷。解说员激动地喊："进入弯道了！"，车身在过弯时侧倾约 15 度，轮胎因高温产生烟雾，空气中弥漫着橡胶烧焦的气味（视觉化表现为烟雾浓度变化）。解说员继续喊："轮胎在冒烟！"，赛车尾部排气管喷出橙红色火焰，与白烟交织形成视觉冲击。解说员震撼地喊："太漂亮了！"，赛车如红色闪电般掠过画面留下白色烟轨。镜头从车外 Truck 跟随开始，与赛车保持等距并行，展现完整车身动态，随后在 0.8 秒内切换至车内 POV 视角，捕捉仪表盘指针飞转（转速表指向 9000 转/分钟）和驾驶者专注表情，最后切回车外以航拍 Drone Pull Up 升至高空俯瞰整个弯道。Cinematic Lighting, Volumetric Lighting, Motion Blur, Smoke Effects, 8K Resolution, Unreal Engine 5, Film Grain, Depth of Field, Bokeh, Speed Ramping,
  "audio_track": 引擎轰鸣声，轮胎摩擦白烟声，高速风噪，
  "dialogue_track": 语气：激动震撼（参考 video_track 中的对话动作）,
  "music_track": 赛车运动，电子合成器 + 强烈鼓点，
  "sync_notes": 轮胎冒烟与白烟视觉同步，过弯与音乐高潮同步
}'''

    def generate_ltx_prompt(self, Mode_Select, Video_Duration, User_Description, api_string, random_seed,
                        Input_Image=None,
                        siliconflow_model="QWEN3VL", custom_model="GPT5.2", api_provider="SiliconFlow", **kwargs):
        # Set random seed
        if random_seed == -1:
            random_seed = random.randint(0, 0xffffffffffffffff)
        random.seed(random_seed)

        # User description directly from input (no PRO_OPTIONS)
        full_description = User_Description

        # Convert image to base64 if in Image_to_Video mode
        image_base64 = None
        if Mode_Select == "Image_to_Video":
            if Input_Image is not None:
                image_base64 = self.tensor_to_base64(Input_Image)
                if not image_base64:
                    raise ValueError("Cannot process input image")

        # Build request
        full_prompt = f"User Description: {full_description}"

        # Parse API String and get credentials
        parse_api_string_for_node(api_string, "NakuNode")
        api_provider, api_key, api_url, sf_key, c_key, c_url = get_api_credentials(api_string, preferred_provider=api_provider)

        try:
            # Check if API key is provided (using parsed credentials)
            if not api_key or api_key in ["Please enter SiliconFlow API Key", "Please enter your API Key", ""]:
                print(f"[NakuNode LTXPrompter] API key not provided, returning user prompt directly")
                return (full_description, full_description)

            # Print API provider info
            print(f"[NakuNode LTXPrompter] API Provider: {api_provider}")
            print(f"[NakuNode LTXPrompter] SiliconFlow API Key: {'已设置' if sf_key else '未设置'}")
            print(f"[NakuNode LTXPrompter] Custom API Key: {'已设置' if c_key else '未设置'}")
            print(f"[NakuNode LTXPrompter] Custom API URL: {c_url}")

            print(f"\n[NakuNode LTXPrompter] {'='*60}")
            print(f"[NakuNode LTXPrompter] Starting request...")
            print(f"[NakuNode LTXPrompter] {'='*60}")
            print(f"[NakuNode LTXPrompter] User Description: {full_description[:100]}...")
            print(f"[NakuNode LTXPrompter] Mode: {Mode_Select}")
            print(f"[NakuNode LTXPrompter] Video Duration: {Video_Duration} seconds")

            # SiliconFlow model mapping for image analysis
            model_mapping = {
                "QWEN3VL": "Qwen/Qwen3-VL-235B-A22B-Instruct",
                "GLM4.6V": "zai-org/GLM-4.6V",
                "KIMI2.5": "Pro/moonshotai/Kimi-K2.5"
            }

            # Custom API model mapping
            custom_model_mapping = {
                "GPT5.2": "gpt-5.2",
                "Gemini Pro 3.1": "gemini-3.1-pro-preview",
                "Gemini Pro 3": "gemini-3-pro-preview",
                "Claude Opus 4.6": "claude-opus-4-6",
                "Kimi 2.5": "kimi-k2.5"
            }

            # Select model and print info based on API provider
            if api_provider == "Custom":
                selected_model = custom_model_mapping.get(custom_model, "gpt-5.2")
                api_url = c_url.rstrip('/')
                use_stream = False
                print(f"[NakuNode LTXPrompter] Using Custom API")
                print(f"[NakuNode LTXPrompter] Custom API URL: {c_url}")
                print(f"[NakuNode LTXPrompter] Using Custom API model: {selected_model}")
            else:
                selected_model = model_mapping.get(siliconflow_model, "Qwen/Qwen3-VL-235B-A22B-Instruct")
                api_url = "https://api.siliconflow.cn/v1/chat/completions"
                use_stream = True
                print(f"[NakuNode LTXPrompter] Using SiliconFlow API")
                print(f"[NakuNode LTXPrompter] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")
                print(f"[NakuNode LTXPrompter] Using SiliconFlow model: {selected_model}")

            print(f"[NakuNode LTXPrompter] Generating LTX prompt with {api_provider}...")

            # Call API using requests library
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Build complete API URL for Custom
            if api_provider == "Custom" and not api_url.endswith('/v1/chat/completions'):
                api_url = api_url + '/v1/chat/completions'

            print(f"[NakuNode LTXPrompter] Request URL: {api_url}")
            print(f"[NakuNode LTXPrompter] Stream mode: {use_stream}")

            # Build messages - using original system prompt
            user_content = []
            if Mode_Select == "Image_to_Video" and image_base64:
                user_content = [
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成 LTX-2 音视频同步提示词。视频时长要求：{Video_Duration}秒。{full_prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            else:
                user_content = [{"type": "text", "text": f"根据以下用户描述生成 LTX-2 音视频同步提示词。视频时长要求：{Video_Duration}秒。{full_prompt}"}]

            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_content}
            ]

            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": 0.7,
                "top_p": 0.9,
                "n": 1,
                "stream": use_stream,
                "max_tokens": 4096
            }

            print(f"[NakuNode LTXPrompter] Sending request...")

            if use_stream:
                # SiliconFlow stream mode
                response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=180, verify=False)
                print(f"[NakuNode LTXPrompter] HTTP status code: {response.status_code}")

                if response.status_code == 200:
                    print(f"[NakuNode LTXPrompter] API call successful")
                    full_content = ""
                    for chunk in response.iter_lines():
                        if chunk:
                            chunk_str = chunk.decode('utf-8').replace('data: ', '')
                            if chunk_str != "[DONE]" and chunk_str.strip():
                                try:
                                    chunk_data = json.loads(chunk_str)
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_content += content
                                except json.JSONDecodeError:
                                    continue
                    print(f"[NakuNode LTXPrompter] Stream response received, length: {len(full_content)}")
                    optimized_response = full_content
                else:
                    error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                    print(error_msg)
                    return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
            else:
                # Custom API non-stream mode - 添加重试机制
                max_retries = 3
                retry_delay = 2  # 秒
                response = None
                
                for attempt in range(max_retries):
                    try:
                        print(f"[NakuNode LTXPrompter] Sending request (attempt {attempt + 1}/{max_retries})...")
                        response = requests.post(api_url, headers=headers, json=payload, timeout=180, verify=False)
                        print(f"[NakuNode LTXPrompter] HTTP status code: {response.status_code}")

                        if response.status_code == 200:
                            print(f"[NakuNode LTXPrompter] API call successful")
                            response_data = response.json()

                            # Parse response
                            if 'choices' in response_data and len(response_data['choices']) > 0:
                                optimized_response = response_data['choices'][0]['message']['content']
                                print(f"[NakuNode LTXPrompter] API response: {optimized_response[:100]}...")
                                break
                            else:
                                error_msg = f"API response format error: {response_data}"
                                print(error_msg)
                                return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
                        else:
                            error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                            print(error_msg)
                            # 如果是服务器错误（5xx），尝试重试
                            if response.status_code >= 500 and attempt < max_retries - 1:
                                print(f"[NakuNode LTXPrompter] Server error, retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                continue
                            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
                    except requests.exceptions.ConnectionError as e:
                        print(f"[NakuNode LTXPrompter] Connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            print(f"[NakuNode LTXPrompter] Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # 指数退避
                        else:
                            error_msg = f"Connection failed after {max_retries} attempts: {str(e)}"
                            print(error_msg)
                            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
                    except requests.exceptions.Timeout:
                        error_msg = "API request timeout"
                        print(error_msg)
                        return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
                    except Exception as e:
                        error_msg = f"Unexpected error: {str(e)}"
                        print(error_msg)
                        return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")

            print(f"[NakuNode LTXPrompter] Generated response received")

            # Return result (AI Generated Prompt, Initial Prompt)
            return (optimized_response, full_description)
        except requests.exceptions.Timeout:
            error_msg = "API request timeout"
            print(error_msg)
            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
        except Exception as e:
            print(f"[NakuNode LTXPrompter] Error during API call: {e}")
            import traceback
            traceback.print_exc()
            return (f"Error: {str(e)}. Original: {full_description}", f"Error: {str(e)}")


# --- Register node to ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "NakuNodeLTXPrompter": NakuNodeLTXPrompter
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodeLTXPrompter": "NakuNode-LTXPrompter"
}
