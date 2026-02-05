# -*- coding: utf-8 -*-
import random
import json
import time
from PIL import Image
import io
import base64

# 尝试导入必要的库，如果失败则在调用时抛出更友好的错误
try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None


# =================================================================================
# == 专业视频提示词选项库 (Pro-V1) ==
# =================================================================================
PRO_OPTIONS = {
    "艺术风格": [
        "随机", "无", "超现实主义", "印象派", "赛博朋克", "蒸汽朋克", "日本浮世绘", "动漫风格", "黏土动画",
        "像素艺术", "卡通渲染", "图形小说风格", "水墨画", "装饰艺术", "哥特式风格", "巴洛克风格",
        "未来主义", "蒸汽波", "低多边形", "故障艺术", "概念艺术", "极简主义", "技术原理图",
        "手绘素描", "油画质感"
    ],
    "景别": [
        "随机", "无", "远景", "大远景", "全景", "中全景", "牛仔景", "中景", "中近景",
        "近景", "大特写", "特写", "插入镜头", "反应镜头", "双人镜头", "三人镜头", "群体镜头",
        "建置镜头", "细节镜头", "单人镜头", "宏观镜头", "定场镜头", "环境肖像", "全景风光",
        "航拍远景"
    ],
    "相机角度": [
        "随机", "无", "平视角度", "高角度", "低角度", "鸟瞰视角", "仰视视角", "荷兰角/斜角",
        "过肩视角", "主观视角(POV)", "侧面视角", "正面视角", "背面视角", "臀部高度视角",
        "地面高度视角", "膝盖高度视角", "上帝视角", "倾斜视角", "镜像反射视角", "锁定视角",
        "广角畸变视角", "望远镜视角", "显微镜视角", "门框窥视视角", "仪表盘视角"
    ],
    "移动与运镜": [
        "随机", "无", "平摇", "俯仰", "推轨", "拉轨", "滑动变焦", "横向滑动", "升降", "手持拍摄",
        "斯坦尼康", "无人机航拍", "第一人称穿越机(FPV)", "弧形运镜", "旋转镜头(Roll)",
        "跟拍", "变焦", "快速推近", "环绕拍摄", "探索性运镜", "固定镜头", "摇臂镜头",

        "穿梭镜头", "身体摄像头", "慢速推轨"
    ],
    "透镜与焦点": [
        "随机", "无", "浅景深", "深景深", "焦点转移", "广角镜头", "长焦镜头", "标准镜头", "鱼眼镜头",
        "变形宽银幕镜头", "微距镜头", "移轴镜头", "柔焦效果", "锐利对焦", "失焦模糊(散景)",
        "针孔效果", "分焦镜效果", "镜头呼吸效应", "红外镜头", "紫外镜头", "热成像镜头",
        "自定义散景形状", "前景模糊", "背景模糊", "全景深"
    ],
    "光线与照明": [
        "随机", "无", "三点布光", "伦勃朗光", "蝴蝶光", "环形光", "分割光", "硬光", "柔光",
        "高调布光", "低调布光", "边缘光", "剪影", "体积光", "耶稣光/曙光", "霓虹灯光",
        "自然光", "黄金时刻", "蓝色时刻", "神奇时刻", "环境光", "顶光", "底光", "烛光", "频闪光"
    ],
    "色彩与色调": [
        "随机", "无", "单色", "互补色", "类似色", "三色系", "饱和度高", "饱和度低/褪色", "暖色调",
        "冷色调", "电影感青橙色调", "漂白效果", "交叉冲洗", "复古胶片色", "LOMO风格",
        "高对比度", "低对比度", "粉彩色调", "双色调", "红外色彩", "选择性色彩", "霓虹色谱",
        "赛璐珞动画色", "暗调/黑色电影", "明亮鲜活"
    ],
    "材质与质感": [
        "随机", "无", "抛光金属", "生锈金属", "碳纤维", "粗糙木材", "光滑玻璃", "磨砂玻璃",
        "半透明水晶", "粗糙混凝土", "光滑大理石", "柔软织物", "皮革质感", "液体质感",
        "全息显示", "哑光表面", "高光泽表面", "丝绸质感", "多毛/毛茸茸", "鳞片质感",
        "生物发光", "粘液质感", "折纸质感", "陶瓷质感", "腐朽/风化"
    ],
    "视觉与后期效果": [
        "随机", "无", "镜头光晕", "动态模糊", "色差", "光线溢出/辉光", "电影颗粒", "暗角",
        "光泄露", "故障/数据损坏", "延时摄影", "慢动作", "粒子效果(火花/尘埃)", "烟雾/薄雾",
        "HUD/UI界面叠加", "全息投影", "像素化", "热浪扭曲", "水下扭曲", "定格动画",
        "光绘/光迹", "倒放效果", "万花筒效果", "鱼眼畸变", "扫描线/CRT效果"
    ]
}

# SiliconFlow 模型映射
SILICONFLOW_MODELS = {
    "QWENVL": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "GLM": "zai-org/GLM-4.6V"
}


class ImageVideoPromptOptimizer:
    """
    单图视频提示词生成器 - 增加了专业视频提示词选项库
    """
    
    @classmethod
    def INPUT_TYPES(s):
        # 创建AI服务商列表 - 移除了内置LLM1, LLM2和OpenRouter
        provider_list = ["智谱AI", "硅基流动"]

        inputs = {
            "required": {
                "图片": ("IMAGE", {}),
                "用户描述": ("STRING", {"multiline": True, "default": "一只可爱的小猫在草地上玩耍"}),
                "AI服务商": (provider_list,),
                "API_KEY": ("STRING", {"multiline": False, "default": "请填写您的API密钥或令牌"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        # 动态添加所有专业选项分类，并设默认为"无"
        for category, options_list in PRO_OPTIONS.items():
            inputs["required"][category] = (options_list, {"default": "无"})

        inputs["optional"] = {
            "硅基流动模型选择": (["QWENVL", "GLM"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")  # 中文提示词, 英文提示词
    RETURN_NAMES = ("AI 生成提示词", "初始提示词")
    FUNCTION = "optimize_prompt"
    CATEGORY = "NakuNode/提示词生成"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为base64编码的图片"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode ImageOptimizer] Warning: numpy is not installed.")
            return None

        # 转换张量到numpy数组并确保值在正确范围内
        i = 255. * image_tensor.cpu().numpy()
        img_array = np.clip(i, 0, 255).astype(np.uint8)

        # 如果是批次图片，选择第一个
        if len(img_array.shape) == 4:
            img_array = img_array[0]

        # 如果有通道维度，确保顺序正确
        if img_array.shape[-1] == 3 or img_array.shape[-1] == 4:  # RGB or RGBA
            img = Image.fromarray(img_array)
        elif img_array.shape[0] == 3 or img_array.shape[0] == 4:  # Channel-first format
            img = Image.fromarray(np.transpose(img_array, (1, 2, 0)))
        else:
            img = Image.fromarray(img_array)

        # 调整图片大小以避免API错误
        MAX_DIMENSION = 1024
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[NakuNode ImageOptimizer] Image resized to {img.width}x{img.height} to prevent API errors.")

        # 将图片保存到内存中的缓冲区
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def generate_zhipu_token(self, apikey: str):
        if not jwt:
            raise ImportError("pyjwt库缺失。请在您的ComfyUI环境中运行 'pip install pyjwt' 来安装。")

        try:
            id, secret = apikey.split('.')
        except Exception as e:
            raise ValueError("无效的智谱API Key，格式应为 'id.secret'", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + 60 * 60 * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )

    def call_llm_api(self, provider, api_key, prompt, image_base64, siliconflow_model_choice="QWENVL"):
        # AI预设关键词模板
        system_prompt = """你是一名熟悉生成通义万相AI视频制作提示词的智能体，基于通义万相AI生视频功能的提示词使用公式生成最佳提示词prompt，提示词的格式以一段完整的自然语言句子为最终输出prompt，需要给到中文和英文两版提示词：

以下几种提示词使用公式：

提示词方式1：主体（主体描述）＋场景（场景描述）＋运动（运动描述）＋镜头语言＋氛围词 ＋风格化
主体描述：主体描述是对主体外观特征细节的描述，可通过形容词或短句列举，例如「一位身着少数民族服饰的黑发苗族少女」、「一位来自异世界的飞天仙子，身着破旧却华丽的服饰，背后展开一对由废墟碎片构成的奇异翅膀」。
场景描述：场景描述是对主体所处环境特征细节的描述，可通过形容词或短句列举。
运动描述：运动描述是对运动特征细节的描述，包含运动的幅度、速率和运动作用的效果，例如「猛烈地摇摆」、「缓慢地移动」、「打碎了玻璃」。
镜头语言：镜头语言包含景别、视角、镜头、运镜等，常见镜头语言详见下方提示词词典。
氛围词：氛围词是对预期画面氛围的描述，例如「梦幻」、「孤独」、「宏伟」，常见氛围词详见下方提示词词典。
风格化：风格化是对画面风格语言的描述，例如「赛博朋克」、「勾线插画」、「废土风格」，常见风格化详见下方提示词词典。
情感修饰词：
梦幻般的、紧张的、宁静的、未来感的、复古的
"画面充满神秘感，背景有若隐若现的星光"
"快速运镜配合紧张的音乐节奏，营造悬疑氛围"
示例优化：
原始提示词：机器人在城市中行走。
优化后：
未来主义风格的银色人形机器人以流畅机械动作穿越霓虹灯闪烁的赛博朋克都市，雨滴在玻璃幕墙反射出霓虹光斑，镜头以手持跟拍方式从低角度仰视，背景虚化为紫色光晕。

提示词方式2：适用于对镜头运动有明确要求、在提示词方式1之上添加更具体的运镜描述可以有效提升视频的动感和叙事性。
提示词=风格化运镜描述＋主体（主体描述）＋场景（场景描述）＋运动（运动描述）+镜头语言＋氛围词：运镜描述是对镜头运动的具体描述，在时间线上，将镜头运动和画面内容的变化有效结合可以有效提升视频叙事的丰富性和专业度。可以通过代入导演的视角来想象和书写运镜过程。需要注意将镜头运动的时长合理控制在5s内，避免过于复杂的运镜，同时如果是图片生成视频，请注意这是一个镜头的内容，不可以有切镜的描述例如从全景切特写。
镜头词典参考：
景别：特写、全景、中景
视角：第一人称视角、俯视
镜头类型：广角镜头、鱼眼镜头、微距镜头、移轴镜头
风格化词汇：
艺术风格：水墨画、油画、赛博朋克、蒸汽波、浮世绘
光影效果：柔和自然光、冷色调月光、强光照射
材质细节：金属光泽、丝绸质感、半透明材质
示例优化：
原始提示词：太空飞船起飞。
优化后：
深空中的银色宇宙飞船喷射蓝色等离子火焰垂直升空，镜头以广角从飞船底部仰拍并缓慢旋转，背景有星云流动效果。

提示词方式3：适用于有明确该类创意需求的用户，在提示词方式1/提示词方式2的基础上添加形变描述可以有效提升视频的趣味性，带来意想不到的视觉效果。
提示词 = 主体A（主体描述）+形变过程+主体B（主体描述）＋场景（场景描述）+运动（运动描述）+镜头语言＋氛围词＋风格化
主体A：主体A指主体形变前的特征和状态。
形变过程：形变过程是对主体从A形态变为B形态的过程描述。详细的过程描述可以有效提升形变的自然度和生动性。
主体B：主体B指主体形变后的特征和状态。
动态变形指令：
物体变形：逐渐变形为…（如「机器人手臂逐渐变形为机械藤蔓」）。
材质变化：表面纹理从…变为…（如「水晶雕像表面纹理从光滑变为像素化」）。
粒子化/融合：分裂成粒子重组为…（如「火焰化作金色粒子重组为凤凰」）。
示例优化：
原始提示词：花朵绽放。
优化后：
黑色土壤中缓慢升起透明晶体，晶体内部逐渐绽放出霓虹粉色的机械花朵，花瓣边缘分裂成发光粒子形成光晕，镜头从侧面俯拍花朵盛开过程。

避免生成画面模糊，可添加清晰度参数：8K分辨率，超清细节。
示例：8K分辨率的机械蜘蛛攀爬在锈蚀金属表面
避免生成风格不统一，可添加明确艺术流派：新海诚风格，柔和水彩质感等。
示例：新海诚风格的樱花雨与少年奔跑场景
避免运动不连贯，可添加描述镜头轨迹：镜头以360°环绕主体匀速移动。
示例：镜头以360°环绕芭蕾舞者旋转拍摄。

最后请确保包含以下要素，同时需要合并为一句自然语句（中文及英文）：
主体：明确核心对象（人物、物体、抽象概念）。
场景：环境细节（室内/室外、季节、时间）。
动作/运动：动态过程或静态姿势。
视觉风格：艺术流派、画质要求。
镜头指令：视角、景别、运动路径。（若没有镜头运动的话请强调镜头固定不动）
增强细节：光线、色彩、特效、情绪氛围。
特别注意：确保镜头与镜头之间的衔接流畅，不能出现例如「手持跟拍轨道推进」这种不合理的运镜方式，因为手持跟拍是有抖动的，轨道推进是平滑的。最终输出一段中文的自然语言，不能换行，不能在段头和段尾增加意义不明的符号，提示词以：中文提示词/... 这样的格式输出。例如：中文提示词/一位身穿红色西装外套的女性..."""

        if not requests:
            raise ImportError("requests库缺失。请在您的ComfyUI环境中运行 'pip install requests' 来安装。")

        headers = {"Content-Type": "application/json"}

        if not api_key or api_key == "必须填入智谱/硅基流动的API":
            raise ValueError(f"使用「{provider}」服务商时，请在API_KEY字段中填入您的API密钥。")

        if provider == "智谱AI":
            token = self.generate_zhipu_token(api_key)
            headers["Authorization"] = token
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成视频提示词：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
            payload = {"model": "glm-4v-plus", "messages": messages, "stream": False}
            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        elif provider == "OpenRouter":
            headers["Authorization"] = f"Bearer {api_key}"
            headers["HTTP-Referer"] = "http://localhost"
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成视频提示词：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
            payload = {"messages": messages, "model": "qwen/qwen2-vl-7b-instruct:free", "stream": False}
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        elif provider == "硅基流动":
            headers["Authorization"] = f"Bearer {api_key}"
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成视频提示词：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
            # 根据用户选择的硅基流动模型选择对应的模型
            model = SILICONFLOW_MODELS.get(siliconflow_model_choice, "Qwen/Qwen-VL-Chat")  # 默认为QwenVL
            payload = {"messages": messages, "model": model, "stream": False}
            api_url = "https://api.siliconflow.cn/v1/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        return prompt

    def optimize_prompt(self, 图片, 用户描述, AI服务商, API_KEY, 随机种子, 硅基流动模型选择="QWENVL", **kwargs):
        # 设置随机种子
        if 随机种子 == -1:
            随机种子 = random.randint(0, 0xffffffffffffffff)
        random.seed(随机种子)

        # 将专业选项融合到用户描述后面，使用逗号分隔
        parts = [用户描述]
        for category, options_list in PRO_OPTIONS.items():
            selected = kwargs.get(category)

            if selected == "无":
                continue
            elif selected == "随机":
                # 从选项列表中排除"随机"和"无"
                valid_options = [opt for opt in options_list if opt not in ["随机", "无"]]
                if valid_options:
                    chosen = random.choice(valid_options)
                    parts.append(chosen)
            else:
                parts.append(selected)

        full_description = "，".join(filter(None, parts))

        # 将图片转换为base64
        image_base64 = self.tensor_to_base64(图片)
        if not image_base64:
            raise ValueError("无法处理输入的图片")

        # 构建请求
        full_prompt = f"用户描述：{full_description}"

        try:
            print(f"[NakuNode ImageOptimizer] Optimizing prompt with {AI服务商}...")
            # 如果是硅基流动服务商，传递模型选择
            if AI服务商 == "硅基流动":
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64, 硅基流动模型选择)
            else:
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64)
            print(f"[NakuNode ImageOptimizer] Optimized response: {optimized_response}")

            # 解析响应，通常应该包含中文和英文版本
            # 尝试查找中文和英文部分
            # 首先尝试查找是否有明确标识的部分
            zh_part = ""
            en_part = ""

            # 尝试解析返回的内容，提取中文和英文版本
            lines = optimized_response.split('\n')
            in_chinese = False
            in_english = False

            chinese_lines = []
            english_lines = []

            for line in lines:
                line = line.strip()

                # 检查是否包含中文字符（简化检查）
                if any('\u4e00' <= char <= '\u9fff' for char in line):
                    if not line.startswith("English:") and not line.startswith("英文:") and "English" not in line and "英文" not in line:
                        chinese_lines.append(line)

                # 检查是否可能包含英文
                if any(char.isalpha() or char.isspace() or char in ',.!?:;\'\"-()[]{}' for char in line) and not any('\u4e00' <= char <= '\u9fff' for char in line):
                    if line and not line.startswith("中文:") and not line.startswith("Chinese:") and "中文" not in line and "Chinese" not in line:
                        english_lines.append(line)

            # 合并结果
            zh_part = ' '.join(chinese_lines).strip()
            en_part = ' '.join(english_lines).strip()

            # 如果解析不成功，使用整个响应作为两种语言
            if not zh_part and not en_part:
                zh_part = optimized_response
                en_part = optimized_response
            elif not zh_part:
                zh_part = full_description  # 使用融合后的描述作为中文
            elif not en_part:
                en_part = full_description  # 使用融合后的描述作为英文

            # 如果解析结果还不够好，直接返回AI的完整响应
            if len(zh_part) < len(full_description) / 2:  # 如果中文部分太短
                zh_part = optimized_response
            if len(en_part) < len(full_description) / 2:  # 如果英文部分太短
                en_part = optimized_response

            return (zh_part, en_part)
        except Exception as e:
            print(f"[NakuNode ImageOptimizer] Error during LLM optimization: {e}")
            # 发生错误时返回融合后的描述
            return (f"优化错误: {e}. 原始描述: {full_description}", f"Optimization Error: {e}. Original: {full_description}")


# --- 註冊節點到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "ImageVideoPromptOptimizer": ImageVideoPromptOptimizer
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageVideoPromptOptimizer": "NakuNode-单图视频提示词生成器"
}