# -*- coding: utf-8 -*-
import random
import json
import time
from PIL import Image
import io
import base64

# 尝試導入必要的庫，如果失敗則在調用時拋出更友好的錯誤
try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None


# SiliconFlow 模型映射
SILICONFLOW_MODELS = {
    "QWENVL": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "GLM": "zai-org/GLM-4.6V",
    "KIMI": "Pro/moonshotai/Kimi-K2.5"
}


class StoryboardImageGenerator:
    """
    分镜图片生成节点 - 基于一张图片生成指定数量的连续分镜
    """

    @classmethod
    def INPUT_TYPES(s):
        # 創建AI服務商列表
        provider_list = ["智谱AI", "硅基流动"]

        inputs = {
            "required": {
                "剧本描述": ("STRING", {"multiline": True, "default": "请输入详细的剧本描述，描述你想要的分镜故事内容"}),
                "AI服务商": (provider_list,),
                "分镜数量": ("INT", {"default": 3, "min": 1, "max": 12}),
                "API_KEY": ("STRING", {"multiline": False, "default": "请填写您的API密钥或令牌"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        inputs["optional"] = {
            "图片1": ("IMAGE", {}),
            "图片2": ("IMAGE", {}),
            "图片3": ("IMAGE", {}),
            "图片4": ("IMAGE", {}),
            "图片5": ("IMAGE", {}),
            "图片6": ("IMAGE", {}),
            "硅基流动模型选择": (["QWENVL", "GLM", "KIMI"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")  # 分镜提示词, 原始请求
    RETURN_NAMES = ("分镜提示词", "原始请求")
    FUNCTION = "generate_storyboard"
    CATEGORY = "NakuNode/分镜生成"

    def tensor_to_base64(self, image_tensor):
        """將張量轉換為base64編碼的圖片"""
        # 將張量轉換為numpy數組
        i = 255.0 * image_tensor.cpu().numpy()
        img = Image.fromarray(i.astype('uint8')[0])

        # 將圖片轉換為base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str

    def generate_zhipu_token(self, apikey):
        if not jwt:
            raise ImportError("pyjwt庫缺失。請在您的ComfyUI環境中運行 'pip install pyjwt' 來安裝。")

        try:
            # 分割API密钥以获取 kid 和 secret
            parts = apikey.split(".")
            if len(parts) != 2:
                raise ValueError("无效的API密钥格式")
            kid, secret = parts

            # 创建 JWT payload
            payload = {
                "api_key": kid,
                "exp": int(round(time.time())) + 3600,
                "timestamp": int(round(time.time() * 1000)),
            }

            # 生成token
            token = jwt.encode(
                payload,
                secret,
                algorithm="HS256",
                headers={"kid": kid}
            )
            return token
        except Exception as e:
            raise Exception(f"生成智谱AI认证令牌失败: {str(e)}")

    def call_zhipu_api(self, image_base64, prompt, api_key):
        """调用智谱AI API"""
        url = "https://open.bigmodel.cn/api/paas/v4/vision/completions"

        headers = {
            "Authorization": f"Bearer {self.generate_zhipu_token(api_key)}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message']['content']

    def call_siliconflow_api(self, image_base64, prompt, api_key, model_choice):
        """调用硅基流动 API"""
        model = SILICONFLOW_MODELS[model_choice]
        url = "https://api.siliconflow.cn/v1/chat/completions"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message']['content']

    def generate_storyboard(self, 剧本描述, AI服务商, 分镜数量, API_KEY, 随机种子, 图片1=None, 图片2=None, 图片3=None, 图片4=None, 图片5=None, 图片6=None, 硅基流动模型选择=None):
        # 设置随机种子
        if 随机种子 == -1:
            随机种子 = random.randint(0, 0xffffffffffffffff)
        random.seed(随机种子)

        # 准备图片列表
        image_tensors = []
        if 图片1 is not None:
            image_tensors.append(图片1)
        if 图片2 is not None:
            image_tensors.append(图片2)
        if 图片3 is not None:
            image_tensors.append(图片3)
        if 图片4 is not None:
            image_tensors.append(图片4)
        if 图片5 is not None:
            image_tensors.append(图片5)
        if 图片6 is not None:
            image_tensors.append(图片6)

        # 如果没有提供任何图片，则抛出错误
        if not image_tensors:
            raise Exception("至少需要提供一张图片")

        # 将图片转换为base64
        image_base64_list = [self.tensor_to_base64(img) for img in image_tensors]

        # 固定使用内置的prompt
        base_prompt = f"""你是拥有 10 年以上视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别（全景、中景、半身特写等等）、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节（场景布局、家具或道具陈设的位置）、情绪氛围、图片风格（日系动漫风、国风、写实风等等）；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。做到拆分后的单段分镜脚本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

1. 核心机制：焦点接力 (Focus Relay)

为了实现"流水般"的叙事，你必须遵循微观因果律，而非单纯的动作。
接力规则：
物理接力：镜头 A 结尾手触碰到门 -> 镜头 B 门拉开角色站在门口看向门外的景观。
视线接力：镜头 A 结尾角色看向天空 -> 镜头 B 也是仰视视角，展示角色眼中的景象。
环境接力：镜头 A 结尾一阵风吹乱头发 -> 镜头 B 是一片被风吹起的树叶掠过镜头。
空间接力：镜头 A 全景展示两名角色在聊天->镜头 B是视角切到角色A身后，中景过肩。镜头聚焦在角色B的胸部以上，角色A的肩膀在前景占据 1/3 画面并微糊
风格接力：镜头 A 是新海诚动漫风 -> 镜头 B 也是新海诚动漫风

2. 图像调性自适应 (Tone Adaptation) - 关键步骤

在生成前，请先判断【参考图像】的属性：
类型 A [对话/情感]：衔接靠光影变化、微表情、嘴型、风吹草动。
类型 B [悬疑/探索]：衔接靠脚步移动、手部触碰、手电筒光束、门的开合。
类型 C [激烈/战斗]：衔接靠速度线、碰撞、碎片、物理位移、角色间的碰撞。


3. 9镜头通用流体结构 (Universal Fluid Structure)

无论什么类型，必须严格遵循以下镜头焦点的转移逻辑（可根据用户要求的镜头数动态调整，整体遵循以下规则），每个画面的视角需要有变化，不能全部都是平视，可以使用镜头俯视/镜头仰视 等更有视觉冲击力的镜头语言描述：

镜头1 [全景入画]：大环境 -> 视觉锚点(Visual Anchor) 处于环境中。
镜头2 [推进/聚焦]：镜头推近 -> 聚焦于 Visual Anchor 的某个局部（眼睛/手/配饰）。
镜头3 [触发/诱因]：中景镜头向左移动->环境发生微小变化（光线移动/风吹过/出现声音），引起 Visual Anchor 注意。
镜头4 [反应/互动]：镜头向前推进，特写Visual Anchor 做出反应（转头/伸手/起步/眼神流转等等）。
镜头5 [过程/流动]：低角度全景镜头向右转动->Visual Anchor 正在进行某个动作（行走/奔跑/抚摸/哭泣等等），强调动作的进行时。
镜头6 [高点/特写]：动作的关键瞬间或情绪的最高点（手指触碰物体/泪水滴落/全力冲刺/角色激动的说话/角色做出过激的行为/角色怒吼等等）。
镜头7 [变化/后果]：由于镜头6的动作，环境产生了反馈（物体亮起/花瓣散开/门打开/敌人倒下/火光四溅/强烈的碰撞等等）。
镜头8 [余韵/局部]：聚焦于变化的后果细节（发光的纹路/地上的水渍/飘落的羽毛/身体的伤口/惊恐的表情等等）。
镜头9 [拉远/出画]：镜头低角度拉远，交代Visual Anchor 与改变后的环境的状态，或者 Visual Anchor 离开改变后的环境。

4. 参考案例

假设输入文字：夕阳下抱着吉他的女孩。情感/忧伤，冷暖色调对比。
假设输入两张图像：Image1是一张全景图像：被夕阳照射着的草地。Image2 是一名穿着粉色连衣裙的黑色长发女孩。Image1 和 Image2 的画风都是日式动漫风。
AI Output:
Next Scene：低角度全景/逆光 : Image1 的夕阳将金色的光辉洒满草地，抱着木吉他的Image2角色穿着粉色连衣裙的黑色长发女孩独自坐在山坡的长椅上，身影被拉得很长。冷暖色调对比。日式动漫。
Next Scene：镜头推进/侧面特写 : 镜头缓慢推进，微风轻轻吹起抱着木吉他的Image2角色黑色长发女孩耳边的碎发，她的睫毛在夕阳下闪烁微光，背景是虚化的Image1的某个位置。冷暖色调对比。日式动漫。
Next Scene：镜头推进特写/Image2手部 :Image2抱着木吉女孩的纤细手指轻轻按在琴弦上，空气中仿佛凝固着即将弹奏前的寂静。背景是虚化的 Image1 局部的空间。冷暖色调对比。日式动漫。
Next Scene：镜头推进中景/Image2胸部以上半身 : Image2角色抱着木吉他穿着粉色连衣裙的黑色长发女孩的手腕轻柔地摆动，拨响了第一根琴弦，琴弦震动的波纹仿佛在空气中扩散，背景是虚化的Image1的某个位置。冷暖色调对比。日式动漫。
Next Scene：低角度环绕镜头/Image2腰部以上半身: 随着旋律的流淌，抱着木吉他的Image2角色长发女孩闭上眼睛沉浸在音乐中，镜头围绕她缓慢旋转，背景是 Image1 的空间，捕捉她陶醉的神情。冷暖色调对比。日式动漫。
Next Scene：镜头大幅度推进/极近特写 : 抱着木吉他的Image2角色长发女孩眼角滑落一滴晶莹的泪珠，泪珠正好滴落在琴箱的边缘，折射出夕阳的红光。背景是 Image1 的空间。冷暖色调对比。日式动漫。
Next Scene：过肩镜头/三分线构图 : 顺着抱着木吉他的Image2角色穿着粉色连衣裙的长发女孩睁开的视线望去，远处的飞鸟正成群结队地飞向落日。在画面的左侧三分之一处，展示Image2角色的头部背影，位于前景。冷暖色调对比。日式动漫。
Next Scene：平视视角全景/背面 : 抱着木吉他的Image2角色穿着粉色连衣裙的长发女孩停止了弹奏，依然保持着抱琴的姿势，看着飞鸟消失在地平线。冷暖色调对比。日式动漫。
Next Scene：镜头拉远/升高 : 镜头垂直拉高，抱着木吉他的Image2角色穿着粉色连衣裙的黑色长发女孩变成了 Image1 场景中草地上一个小小的点，微弱的阳光照射在她身上，被巨大的星空夜幕逐渐笼罩。冷暖色调对比。日式动漫。

5. 正式执行 (Execute)

请分析我上传的图片，首先判断是[静谧/情感]、[悬疑/探索]还是[激烈/战斗]，然后提取Visual Anchor，严格按照"焦点接力"逻辑生成{分镜数量}行分镜。
要求：禁止废话，禁止空行，禁止代词，确保镜头之间有电影剪辑般的逻辑连贯性。

6.特殊情况（Special Cases）
当用户输入一张图片里面既有人物又有场景。则意味着用户需要以他上传的分镜作为第一个分镜，根据用户提供的剧本进行分镜拆解。注意所有分镜的镜头运动描述需要基于第一张分镜图作为标准进行。同时后面所有分镜中只要涉及到人物角色，请详细描述人物角色的各种特征，避免模型无法正确识别角色。注意一些特写的镜头画面描述，只描述画面出现的内容。错误提示词：侧面特写/眼睛：黑色长发女孩穿着粉色连衣裙和黑色小皮鞋，她的睫毛在夕阳下闪闪发光，瞳孔里映射着落日的余晖。正确的提示词：侧面特写/眼睛：黑色长发女孩的睫毛在夕阳下闪闪发光，瞳孔里映射着落日的余晖。

参考案例
假设输入的文字：两个女孩在夕阳下的草地平静地对话。黑色长发女孩向金色短发女孩告别。两人依依不舍。冷暖色调对比。
假设输入一张图像：全景图像。夕阳下两名坐在草地上的女孩，一名女孩黑色长直发穿着粉色连衣裙，一名女孩金色短发穿着蓝色连衣裙。画面暖色调。画风为日式动漫风。
AI Output:
Next Scene：低角度全景/逆光：夕阳将金色的光辉洒满草地，照射在两名坐在草地上女孩的身上，穿着粉色连衣裙的黑色长发女孩转头看向金色短发穿着蓝色连衣裙的女孩，脸上露出微笑。两个人的身影被拉得很长。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：镜头向右移动并推进/侧面特写：镜头缓慢推进，微风轻轻吹起黑色长发女孩耳边的碎发，她看向旁边的金色短发女孩，嘴巴轻轻动起来。前景是虚化的金色短发女孩的侧脸，在画面的右侧三分之一处。逆光，冷暖色调对比。日式动漫风。
Next Scene：镜头推进特写/手部：穿着粉色连衣裙女孩的纤细手指轻轻搭在穿着蓝色连衣裙女孩的手上，两人跪坐在草地上。展示一种温暖又柔和的情感，柔和的夕阳照射在她们的手上。冷暖色调对比。日式动漫风。
Next Scene：镜头向左移动并推进/侧面特写：金色短发女孩看向黑色长发女孩，嘴巴轻轻动起来。前景是虚化的黑色长发女孩的背面，在画面的右侧三分之一处。柔和的夕阳照射在金色短发女孩的脸上。冷暖色调对比。日式动漫风。
Next Scene：低角度环绕镜头/角色腰部以上半身 : 黑色长发女孩把头靠在金色短发女孩的肩上，两人坐在夕阳照射的草地上，夕阳的光线从左边柔和的照射在她们身上。黑色长发女孩露出微笑，嘴巴轻轻动起来说话。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：镜头大幅度推进/极近特写: 金色短发女孩眼角滑落一滴晶莹的泪珠，折射出夕阳的红光。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：镜头转到两人身后，过肩镜头/三分线构图 : 前景是两人的背影，远处的飞鸟正成群结队地飞向落日。冷暖色调对比。日式动漫风。
Next Scene：平视视角全景: 金色短发穿着蓝色连衣裙的女孩抹着眼泪，穿着粉色连衣裙的黑色长发女孩抱着她低声哭泣。冷暖色调对比。日式动漫风。
Next Scene： 大远景/拉高 : 镜头垂直拉高，金色短发穿着蓝色连衣裙的女孩牵着穿着粉色连衣裙的黑色长发女孩走在草地上，变成了草地上一个小小的点，被巨大的星空夜幕逐渐笼罩。冷暖色调对比。日式动漫风。

# : 强制排版约束 (Output Layout) - 重要
1.  **紧凑输出**：所有输出必须是一个**连续的文本块**。
2.  **零空行**：在 `Next Scene` 与 `Next Scene` 之间，**严禁插入空行**。
3.  **换行符**：仅允许使用单次换行（Single Line Break），禁止使用段落分行。

# Example (排版正确示范)
Next Scene：...
Next Scene：...
Next Scene：...
(注意：上面这三行是紧挨着的，中间没有空隙)

# Action
请执行生成，确保结果紧凑无空行。

我的剧本描述是：{剧本描述}"""

        # 根据选择的AI服务商调用相应API


        # 调试输出 - 显示当前使用的参数和提示词
        debug_info = f"""【NAKU分镜系统】
- 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- AI服务商: {AI服务商}
- 分镜数量: {分镜数量}
- 图片数量: {len(image_tensors)}
- 随机种子: {随机种子}
- 硅基流动模型选择: {硅基流动模型选择}
- 剧本描述: {剧本描述[:100]}...  # 仅显示前100个字符
========================================
"""

        print(debug_info)

        if AI服务商 == "智谱AI":
            if not API_KEY or API_KEY == "请填写您的API密钥或令牌":
                raise Exception("必须填入智谱/硅基流动的 API")
            # 对每张图片调用API（如果有多张图片，我们只使用第一张作为参考，或者将它们都传给API）
            result = self.call_zhipu_multi_image_api(image_base64_list, base_prompt, API_KEY)
        elif AI服务商 == "硅基流动":
            if not API_KEY or API_KEY == "请填写您的API密钥或令牌":
                raise Exception("必须填入智谱/硅基流动的 API")
            result = self.call_siliconflow_multi_image_api(image_base64_list, base_prompt, API_KEY, 硅基流动模型选择)
        else:
            raise Exception(f"不支持的AI服务商: {AI服务商}")

        return (result, base_prompt)

    def call_zhipu_multi_image_api(self, image_base64_list, prompt, api_key):
        """调用智谱AI API，支持多张图片"""
        url = "https://open.bigmodel.cn/api/paas/v4/vision/completions"

        headers = {
            "Authorization": f"Bearer {self.generate_zhipu_token(api_key)}",
            "Content-Type": "application/json"
        }

        # 使用固定系统提示词
        system_prompt = """你是拥有 10 年以上类型片视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节、情绪氛围；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。尽量做到拆分后的单段剧本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

分镜格式： [镜头序号]/Next Scene:[景别]，画面中 [主体（若用户上传了角色单独的图片，则需要通过"ImageX的角色"来锚定角色，其中X为上传的图片序号)，严格保持发色、身形、服饰不变] 在 [环境（若用户上传了场景单独的图片，则需要通过"ImageX的场景"来锚定场景，其中X为上传的图片序号)，画面中的位置，随剧情自然递进延伸] 下做
[动作，为前一镜头的静态延续或递进姿态]，[光影风格，完全匹配图片色调与光影逻辑] 营造 [情绪氛围，贴合剧情发展层次]。文字长度 150-300 字， 一段中文的自然语言，不换行，无特殊符号，语言契合类型片创作语境。

创作规则：
1. 视觉连贯统一：色彩调性、构图逻辑、美学风格、材质表现与图片完全契合，动作姿态衔接无断层；
2. 景别丰富多样：必须涵盖特写、近景、中景、远景、全景、广角等多种景别中至少 3 种不同景别，避免连续重复同一景别；
3. 文本原创精炼：核心短语重复不超过 2 次，无叙事冗余；
4. 背景自然递进：环境细节随剧情逐步变化，无突兀跳跃，强化画面叙事性；
5. 构图电影感：运用适配景别强化主体表现力，突出画面张力；
6. 画质高清无瑕：注重真实材质纹理表现，画面清晰无噪点、无畸变。严格根据用户需要的分镜数量提供分镜提示文本，无额外注释。
7. 剧情自然递进：动作姿态衔接原画面逻辑，环境细节随分镜逐步变化（如原场景为巷口，后续可延伸至巷尾、墙角），无突兀跳跃。
8. 每一段分镜之间仅用一个换行来区分，不需要增加额外的符号和注释."""

        user_prompt = f"根据以下用户描述和附带的图片，生成分镜提示词：{prompt}"

        # 构建消息内容，包含所有图片
        content = [{"type": "text", "text": user_prompt}]
        for img_base64 in image_base64_list:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            })

        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message']['content']

    def call_siliconflow_multi_image_api(self, image_base64_list, prompt, api_key, siliconflow_model_choice):
        """调用硅基流动 API，支持多张图片"""
        model = SILICONFLOW_MODELS[siliconflow_model_choice]
        url = "https://api.siliconflow.cn/v1/chat/completions"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}"
        }

        # 使用固定系统提示词
        system_prompt = """你是拥有 10 年以上类型片视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节、情绪氛围；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。尽量做到拆分后的单段剧本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

分镜格式： [镜头序号]/Next Scene:[景别]，画面中 [主体（若用户上传了角色单独的图片，则需要通过"ImageX的角色"来锚定角色，其中X为上传的图片序号)，严格保持发色、身形、服饰不变] 在 [环境（若用户上传了场景单独的图片，则需要通过"ImageX的场景"来锚定场景，其中X为上传的图片序号)，画面中的位置，随剧情自然递进延伸] 下做
[动作，为前一镜头的静态延续或递进姿态]，[光影风格，完全匹配图片色调与光影逻辑] 营造 [情绪氛围，贴合剧情发展层次]。文字长度 150-300 字， 一段中文的自然语言，不换行，无特殊符号，语言契合类型片创作语境。

创作规则：
1. 视觉连贯统一：色彩调性、构图逻辑、美学风格、材质表现与图片完全契合，动作姿态衔接无断层；
2. 景别丰富多样：必须涵盖特写、近景、中景、远景、全景、广角等多种景别中至少 3 种不同景别，避免连续重复同一景别；
3. 文本原创精炼：核心短语重复不超过 2 次，无叙事冗余；
4. 背景自然递进：环境细节随剧情逐步变化，无突兀跳跃，强化画面叙事性；
5. 构图电影感：运用适配景别强化主体表现力，突出画面张力；
6. 画质高清无瑕：注重真实材质纹理表现，画面清晰无噪点、无畸变。严格根据用户需要的分镜数量提供分镜提示文本，无额外注释。
7. 剧情自然递进：动作姿态衔接原画面逻辑，环境细节随分镜逐步变化（如原场景为巷口，后续可延伸至巷尾、墙角），无突兀跳跃。
8. 每一段分镜之间仅用一个换行来区分，不需要增加额外的符号和注释."""

        user_prompt = f"根据以下用户描述和附带的图片，生成分镜提示词：{prompt}"

        # 构建消息内容，包含所有图片
        content = [{"type": "text", "text": user_prompt}]
        for img_base64 in image_base64_list:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            })

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message']['content']


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "NakuNode_分镜图片生成": StoryboardImageGenerator
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNode_分镜图片生成": "NakuNode 分镜图片生成"
}