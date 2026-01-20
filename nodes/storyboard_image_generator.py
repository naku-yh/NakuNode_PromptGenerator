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
    "GLM": "zai-org/GLM-4.6V"
}


class StoryboardImageGenerator:
    """
    分镜图片生成节点 - 基于一张图片生成指定数量的连续分镜
    """

    @classmethod
    def INPUT_TYPES(s):
        # 創建AI服務商列表
        provider_list = ["智谱AI", "硅基流动"]

        # 模型选择列表
        model_list = ["QwenEdit", "Flux.2"]

        inputs = {
            "required": {
                "剧本描述": ("STRING", {"multiline": True, "default": "请输入详细的剧本描述，描述你想要的分镜故事内容"}),
                "AI服务商": (provider_list,),
                "模型选择": (model_list, {"default": "QwenEdit"}),  # 新增模型选择
                "分镜数量": ("INT", {"default": 3, "min": 1, "max": 12}),
                "API_KEY": ("STRING", {"multiline": False, "default": "选择内建服务商时无需填写"}),
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
            "硅基流动模型选择": (["QWENVL", "GLM"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
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

    def generate_storyboard(self, 剧本描述, AI服务商, 模型选择, 分镜数量, API_KEY, 随机种子, 图片1=None, 图片2=None, 图片3=None, 图片4=None, 图片5=None, 图片6=None, 硅基流动模型选择=None):
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

        # 根据模型选择构建不同的提示词
        if 模型选择 == "QwenEdit":
            # 使用原有的提示词
            base_prompt = f"""你是拥有 10 年以上类型片视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节、情绪氛围；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。尽量做到拆分后的单段剧本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

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
8. 每一段分镜之间仅用一个换行来区分，不需要增加额外的符号和注释。

我需要生成 {分镜数量} 个分镜。

我的剧本描述是：{剧本描述}"""
        elif 模型选择 == "Flux.2":
            # 使用新的Flux.2提示词
            base_prompt = f"""你是拥有 10 年以上类型片视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节、情绪氛围；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。尽量做到拆分后的单段剧本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

分镜格式： [镜头序号]/[景别]，画面中 [主体（若用户上传了角色单独的图片，则需要通过"ImageX的角色"来锚定角色，其中X为上传的图片序号），严格保持发色、身形、服饰不变] 在 [环境（若用户上传了场景单独的图片，则需要通过"ImageX的场景"来锚定场景，其中X为上传的图片序号），画面中的位置，随剧情自然递进延伸] 下做
[动作，为前一镜头的静态延续或递进姿态]，[光影风格，完全匹配图片色调与光影逻辑] 营造 [情绪氛围，贴合剧情发展层次]。文字长度 150-300 字， 一段中文的自然语言，不换行，无特殊符号，语言契合类型片创作语境。

创作规则：
1. 视觉连贯统一：色彩调性、构图逻辑、美学风格、材质表现与图片完全契合，动作姿态衔接无断层；
2. 景别丰富多样：必须涵盖特写、近景、中景、远景、全景、广角等多种景别中至少 3 种不同景别，避免连续重复同一景别；
3. 文本原创精炼：核心短语重复不超过 2 次，无叙事冗余；
4. 背景自然递进：环境细节随剧情逐步变化，无突兀跳跃，强化画面叙事性；
5. 构图电影感：运用适配景别强化主体表现力，突出画面张力；
6. 画质高清无瑕：注重真实材质纹理表现，画面清晰无噪点、无畸变。严格根据用户需要的分镜数量提供分镜提示文本，无额外注释。
7. 剧情自然递进：动作姿态衔接原画面逻辑，环境细节随分镜逐步变化（如原场景为巷口，后续可延伸至巷尾、墙角），无突兀跳跃。
8. 每一段分镜之间仅用一个换行来区分，不需要增加额外的符号和注释。
9.当用户提到两人或多人对话的场景，请参照以下案例进行对话画面的描述生成：
参考案例一：中景，三分线构图 ，在学校门口，站着一位穿着校服的女生， 位于画面右侧三分之一 后景处，非居中构图，人物视线朝向画面左侧。在画面的左侧三分之一处，展示一个男生的头部背影，位于前景。
参考案例二：中景过肩，视角切到男生身后。镜头聚焦在女生的胸部以上，男生的肩膀在前景占据 1/3 画面并微糊。
参考案例三：近景过肩，视角切到男生身后。镜头聚焦在女生的胸部以上，男生的肩膀在前景占据 1/3 画面并微糊。
参考案例四：反向近景过肩，镜头拉近。聚焦在女士的肩膀以上，捕捉其眼神细节，前景的男士肩膀模糊。

我需要生成 {分镜数量} 个分镜。

我的剧本描述是：{剧本描述}"""
        else:
            # 默认使用QwenEdit的提示词
            base_prompt = f"""你是拥有 10 年以上类型片视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。第一步精准分析用户上传图片核心元素：主体（外貌、发色、身形、服饰、状态、动作线索）、景别、光影风格（光源类型、色调基调、明暗对比、光影逻辑）、环境场景细节、情绪氛围；第二步精准分析用户的剧本描述，根据用户需要的分镜数量进行剧本的拆分。尽量做到拆分后的单段剧本能通过一段5-7秒的视频完整呈现。第三步基于分析结果，按以下格式和规则生成用户需要的多段连续文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

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
8. 每一段分镜之间仅用一个换行来区分，不需要增加额外的符号和注释。

我需要生成 {分镜数量} 个分镜。

我的剧本描述是：{剧本描述}"""

        # 根据选择的AI服务商调用相应API
        if AI服务商 == "智谱AI":
            if not API_KEY or API_KEY == "选择内建服务商时无需填写":
                raise Exception("必须填入智谱/硅基流动的 API")
            # 对每张图片调用API（如果有多张图片，我们只使用第一张作为参考，或者将它们都传给API）
            result = self.call_zhipu_multi_image_api(image_base64_list, base_prompt, API_KEY)
        elif AI服务商 == "硅基流动":
            if not API_KEY or API_KEY == "选择内建服务商时无需填写":
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

        # 构建消息内容，包含所有图片
        content = [{"type": "text", "text": prompt}]
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
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message']['content']

    def call_siliconflow_multi_image_api(self, image_base64_list, prompt, api_key, model_choice):
        """调用硅基流动 API，支持多张图片"""
        model = SILICONFLOW_MODELS[model_choice]
        url = "https://api.siliconflow.cn/v1/chat/completions"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}"
        }

        # 构建消息内容，包含所有图片
        content = [{"type": "text", "text": prompt}]
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
                {
                    "role": "user",
                    "content": content
                }
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