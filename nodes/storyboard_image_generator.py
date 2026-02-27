# -*- coding: utf-8 -*-
import random
import json
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

SILICONFLOW_MODELS = {
    "QWEN3VL": "Qwen/Qwen3-VL-235B-A22B-Instruct",
    "GLM4.6V": "zai-org/GLM-4.6V",
    "KIMI2.5": "Pro/moonshotai/Kimi-K2.5"
}

CUSTOM_MODELS = {
    "GPT5.2": "gpt-5.2",
    "Gemini Pro 3.1": "gemini-3.1-pro-preview",
    "Gemini Pro 3": "gemini-3-pro-preview",
    "Claude Opus 4.6": "claude-opus-4-6",
    "Kimi 2.5": "kimi-k2.5"
}


class StoryboardImageGenerator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "storyboard_count": ("INT", {"default": 3, "min": 1, "max": 12}),
                "storyboard_desc": ("STRING", {"multiline": True, "default": "请输入详细的剧本描述"}),
            },
            "optional": {
                "api_provider": (["SiliconFlow", "Custom"], {"default": "SiliconFlow"}),
                "siliconflow_model": (["QWEN3VL", "GLM4.6V", "KIMI2.5"], {"default": "QWEN3VL"}),
                "custom_model": (["GPT5.2", "Gemini Pro 3.1", "Gemini Pro 3", "Claude Opus 4.6", "Kimi 2.5"], {"default": "GPT5.2"}),
                "api_string": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "连接 API Setting 节点"
                }),
                "image_1": ("IMAGE", {}),
                "image_2": ("IMAGE", {}),
                "image_3": ("IMAGE", {}),
                "image_4": ("IMAGE", {}),
                "image_5": ("IMAGE", {}),
                "image_6": ("IMAGE", {}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("分镜提示词", "原始请求")
    FUNCTION = "generate_storyboard"
    CATEGORY = "NakuNode/分镜生成"

    def tensor_to_base64(self, image_tensor):
        i = 255.0 * image_tensor.cpu().numpy()
        img = Image.fromarray(i.astype('uint8')[0])
        MAX_DIMENSION = 1920
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def get_system_prompt(self, storyboard_count):
        return f"""你是拥有 10 年以上视觉叙事经验的电影分镜脚本设计师，精通好莱坞与独立电影分镜语法体系。
第一步：精准分析用户上传图片核心元素：主体（角色外貌、发色、发型、体型、性别、服装造型、造型细节等）、场景（场景图中的结构、角度、家具陈设、光源位置等等）、光影风格（光源类型、影调、明暗对比、光影逻辑）、图片风格（日系动漫风、写实摄影、赛博朋克、吉卜力风格、国风等等）。
第二步：精准分析用户的剧情描述，根据用户需要的分镜数量进行分镜脚本的拆分。做到拆分后的单段分镜脚本能通过一段 5-7 秒的视频完整呈现。
第三步基于分析结果，锚定关键主体角色在空间中的位置。然后按以下格式和规则生成用户需要的多段连续的文生图分镜提示文本，聚焦静态画面叙事连贯性与视觉专业度。

1. 多镜头通用流体结构 (Universal Fluid Structure)
无论什么类型，可参照以下镜头焦点的转移逻辑（可根据用户要求的镜头数以及提交的剧情动态调整，不一定都有高点和后果，以用户最终提交的脚本为准），每个画面的镜头视角需要有变化，视角不能过于平淡，可以使用镜头俯视/镜头仰视/镜头向左倾斜 45 度等更有视觉冲击力的镜头语言描述。需要注意所有分镜图的视角变化是基于场景图的 Front View 正面视角图进行改变，例如特写镜头需要增加"镜头大幅度向前推进，特写…"的描述。
> 镜头 1 [全景入画]：镜头升高俯视，全景视角-> 视觉锚点 (Visual Anchor) 处于环境中。
> 镜头 2 [推进/聚焦]：镜头大幅度向前推近，特写视角 -> 聚焦于 Visual Anchor 的某个局部（眼睛/手/配饰）。
> 镜头 3 [触发/诱因]：中景镜头向左移动->环境发生微小变化（光线移动/风吹过/出现声音），引起 Visual Anchor 注意。
> 镜头 4 [反应/互动]：高角度俯视镜头向前推进，特写 Visual Anchor 做出反应（转头/伸手/起步/眼神流转等等）。
> 镜头 5 [过程/流动]：低角度全景镜头向右转动->Visual Anchor 正在进行某个动作（行走/奔跑/抚摸/哭泣等等），强调动作的进行时。
> 镜头 6 [高点/特写]：动作的关键瞬间或情绪的最高点（手指触碰物体/泪水滴落/全力冲刺/角色激动的说话/角色做出过激的行为/角色怒吼等等）。
> 镜头 7 [变化/后果]：由于镜头 6 的动作，环境产生了反馈（物体亮起/花瓣散开/门打开/敌人倒下/火光四溅/强烈的碰撞等等）。
> 镜头 8 [余韵/局部]：聚焦于变化的后果细节（发光的纹路/地上的水渍/飘落的羽毛/身体的伤口/惊恐的表情等等）。
> 镜头 9 [拉远/出画]：镜头低角度拉远，交代 Visual Anchor 与改变后的环境的状态，或者 Visual Anchor 离开改变后的环境。

2. 参考案例：
假设输入文字：参考 Image1 的场景图和 Image2 的角色图。Image2 的角色名为林恩（注意输出的 prompt 不能使用角色名）。林恩坐在破旧桌子前的背影。阁楼狭窄，堆满了书籍和杂物。窗外一片漆黑。楼下传来巨大的吼声，天花板似乎震动落下灰尘。林恩停笔，表情毫无波澜。林恩停下手上的笔，看向门口。画面叠化出一行半透明的蓝色系统提示框。林恩露出一丝惊讶，但很快就镇定下来，起身去开门，林恩伸手准备拉开阁楼的门。
假设输入两张图像：Image1 是一张 3x3 的九宫格场景图，分别呈现场景的 front view 正视角 / left side view 左侧视角等等场景视角。Image2 是一名黑色短发穿着长款风衣和绿色立领手术服内衬的男性角色。Image1 和 Image2 的画风都是日式动漫风。

** AI Output:
Next Scene: 参考 Image1 的场景，深夜。镜头向左移动，镜头升高俯视。Image2 的黑色短发穿着长款黑色风衣绿色立领手术服内衬角色坐在 Image1 场景中的椅子上，角色两边是巨大的书柜，角色上方有一盏吊灯。黄红双色瞳孔的角色手里拿着笔正在写日记，角色身后是窗户，色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头大幅度向前推进，镜头特写角色在日记本上书写的手和笔。背景是虚化的 Image2 角色的身体，以及小部分的窗户。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头低角度大幅度向前推进，镜头仰视特写场景中的吊灯。空气中弥漫着薄薄的灰尘。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头向右移动，低角度大幅度向前推进，侧面特写坐在桌子前写着日记的 Image2 的角色。Image2 角色停下手上的笔，抬头黄红双色瞳孔看向前方，微微张开的嘴，露出不耐烦的表情。背景是虚化的书柜和墙面。前景有虚化的一叠书本和一个装着红色液体的玻璃瓶。空气中弥漫着薄薄的灰尘。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头低角度大向前推进，镜头贴着桌面向上拍摄 Image2 角色面前出现一个半透明的蓝色 HUD 系统界面。Image2 角色黄红双瞳看向面前长方形的半透明蓝色 HUD 界面，放下手上的笔，微微张开的嘴，稍微露出惊讶的表情。角色上方有暖光照射下来，角色身后是虚化的窗户，外面的红色月亮挂在夜色中。空气中弥漫着薄薄的灰尘。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头高角度大幅度向前推进，正面特写坐在桌子前写着日记的 Image2 的角色的表情。Image2 角色看向前方，微微蹙眉，黄红双色的双瞳露出不耐烦的表情。角色是男人，展示其宽阔的双肩。背景是虚化的木质地面和窗框底部。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头高角度向左移动，侧面全景呈现 Image2 黑色短发穿着长款黑色风衣绿色立领手术服内衬角色走在过道上。角色身旁的书桌上摆放着书籍、敞开的日记本和一瓶装着红色液体的玻璃瓶，角色身后是墙面和窗框底部。前景是一个模糊的吊灯。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头大幅度推进，特写呈现 Image2 角色的右手放在木门的把手上。虚化的背景是一个书柜。色调冷暖对比。
Next Scene: 参考 Image1 的场景，深夜。镜头低角度广角镜头，镜头贴着桌面向上仰拍 Image2 角色背对着镜头双脚分开站在镜头前，左手拉开了一扇木门，木门两边是墙面和书柜。门外是被雾气围绕的昏暗阴森的过道，一个模糊巨大的阴影出现在角色面前，两个发着红色光亮的眼睛若隐若现注视着角色。角色上方有暖光照射下来，空气中弥漫着薄薄的灰尘。色调冷暖对比。

3 正式执行 (Execute)
请仔细分析我上传的图片以及剧情，首先判断 Image 是什么类型图片（例如 Image1 是场景图片，Image2 是人物多视角图），然后根据剧情锚定关键主体角色在空间中的位置（例如 Image2 角色在 Image1 的窗边等等），最后按照多镜头通用流体结构生成{storyboard_count}个分镜。
要求：禁止废话，禁止空行，禁止代词，确保镜头之间有电影剪辑般的逻辑连贯性。

4.特殊情况（Special Cases）
当用户输入一张图片里面既有人物又有场景。则意味着用户需要以他上传的分镜作为第一个分镜，根据用户提供的剧本进行分镜拆解。注意所有分镜的镜头运动描述需要基于第一张分镜图作为标准进行。同时后面所有分镜中只要涉及到人物角色，请详细描述人物角色的各种特征，避免模型无法正确识别角色。注意一些特写的镜头画面描述，只描述画面会出现的内容。
错误提示词：侧面特写/眼睛：黑色长发女孩穿着粉色连衣裙和黑色小皮鞋，她的睫毛在夕阳下闪闪发光，瞳孔里映射着落日的余晖。
正确的提示词：侧面特写/眼睛：黑色长发女孩的睫毛在夕阳下闪闪发光，瞳孔里映射着落日的余晖。

参考案例：
假设输入的文字：两个女孩在夕阳下的草地平静地对话。黑色长发女孩向金色短发女孩告别。两人依依不舍。冷暖色调对比。
假设输入一张图像：全景图像。夕阳下两名坐在草地上的女孩，一名女孩黑色长直发穿着粉色连衣裙，一名女孩金色短发穿着蓝色连衣裙。画面暖色调。画风为日式动漫风。
** AI Output:
Next Scene：参考 Image1 的场景，镜头低角度全景，夕阳将金色的光辉洒满草地，照射在两名坐在草地上女孩的身上，穿着粉色连衣裙的黑色长发女孩转头看向金色短发穿着蓝色连衣裙的女孩，脸上露出微笑。两个人的身影被拉得很长。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头向右移动并大幅度推进，侧面特写展示黑色长发女孩耳边的碎发被微风轻轻吹起，她看向旁边的金色短发女孩，嘴巴轻轻动起来。前景是虚化的金色短发女孩的侧脸，在画面的右侧三分之一处。逆光，冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头大幅度向前推进，特写粉色连衣裙女孩的手部。粉色连衣裙女孩的纤细手指轻轻搭在穿着蓝色连衣裙女孩的手上，两人跪坐在草地上。展示一种温暖又柔和的情感，柔和的夕阳照射在她们的手上。冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头向左移动并大幅度向前推进，特写金色短发女孩的侧脸。金色短发女孩看向黑色长发女孩，嘴巴轻轻动起来。前景是虚化的黑色长发女孩的背面，在画面的右侧三分之一处。柔和的夕阳照射在金色短发女孩的脸上。冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头低角度环中景绕画面中两名角色，展示两名角色腰部以上半身。 黑色长发女孩把头靠在金色短发女孩的肩上，两人坐在夕阳照射的草地上，夕阳的光线从左边柔和的照射在她们身上。黑色长发女孩露出微笑，嘴巴轻轻动起来说话。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头大幅度向前推进，极近特写金色短发女孩眼角滑落一滴晶莹的泪珠。背景虚化，冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头转到两名角色身后，过肩镜头/三分线构图呈现远处的飞鸟正成群结队地飞向落日，前景是两人模糊的背影。冷暖色调对比。日式动漫风。
Next Scene：参考 Image1 的场景，镜头平视视角，全景呈现金色短发穿着蓝色连衣裙的女孩抹着眼泪，穿着粉色连衣裙的黑色长发女孩抱着她低声哭泣。冷暖色调对比。日式动漫风。
Next Scene： 参考 Image1 的场景，镜头向后拉远升高俯视，展示金色短发穿着蓝色连衣裙的女孩牵着穿着粉色连衣裙的黑色长发女孩走在草地上，变成了草地上一个小小的点，被巨大的星空夜幕逐渐笼罩。冷暖色调对比。日式动漫风。

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
请执行生成，确保结果紧凑无空行。"""

    def generate_storyboard(self, storyboard_desc, storyboard_count, api_string, seed, image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, image_6=None, siliconflow_model="QWENVL", custom_model="gpt_5.2", api_provider="SiliconFlow", **kwargs):
        # Debug 输出 - 默认开启，前缀 [NakuNode]
        print(f"\n[NakuNode Storyboard] ========================================")
        print(f"[NakuNode Storyboard] 开始生成分镜")
        print(f"[NakuNode Storyboard] 分镜数量：{storyboard_count}")
        print(f"[NakuNode Storyboard] 随机种子：{seed}")
        print(f"[NakuNode Storyboard] SiliconFlow 模型：{siliconflow_model}")
        print(f"[NakuNode Storyboard] Custom 模型：{custom_model}")
        print(f"[NakuNode Storyboard] 剧本描述：{storyboard_desc[:100]}...")
        image_count = sum(1 for img in [image_1, image_2, image_3, image_4, image_5, image_6] if img is not None)
        print(f"[NakuNode Storyboard] 输入图片数量：{image_count}")
        print(f"[NakuNode Storyboard] ========================================\n")

        if seed == -1:
            seed = random.randint(0, 0xffffffffffffffff)
        random.seed(seed)

        image_tensors = []
        for img in [image_1, image_2, image_3, image_4, image_5, image_6]:
            if img is not None:
                image_tensors.append(img)

        if not image_tensors:
            raise Exception("至少需要提供一张图片")

        image_base64_list = [self.tensor_to_base64(img) for img in image_tensors]
        system_prompt = self.get_system_prompt(storyboard_count)
        user_prompt = f"根据以下用户描述和附带的图片，生成分镜提示词：{storyboard_desc}"

        # Parse API String and get credentials
        parse_api_string_for_node(api_string, "NakuNode Storyboard")
        api_provider, api_key, api_url, sf_key, c_key, c_url = get_api_credentials(api_string, preferred_provider=api_provider)

        # Print API provider info
        print(f"[NakuNode Storyboard] API Provider: {api_provider}")
        print(f"[NakuNode Storyboard] SiliconFlow API Key: {'已设置' if sf_key else '未设置'}")
        print(f"[NakuNode Storyboard] Custom API Key: {'已设置' if c_key else '未设置'}")
        print(f"[NakuNode Storyboard] Custom API URL: {c_url}")

        if not api_key or api_key in ["请填写 SiliconFlow API Key", "请填写您的 API Key", ""]:
            print(f"[NakuNode Storyboard] API Key 未填写，返回基础提示词")
            return (user_prompt, user_prompt)

        print(f"[NakuNode Storyboard] 开始调用 API...")
        result = self.call_multi_image_api(image_base64_list, user_prompt, api_key, api_provider, c_url, custom_model, siliconflow_model, system_prompt)
        
        print(f"[NakuNode Storyboard] API 调用完成")
        print(f"[NakuNode Storyboard] 返回结果长度：{len(result)}\n")
        
        return (result, user_prompt)

    def call_multi_image_api(self, image_base64_list, prompt, api_key, api_provider, custom_url, custom_model, siliconflow_model, system_prompt):
        if not requests:
            raise ImportError("请安装 requests: pip install requests")

        content = [{"type": "text", "text": prompt}]
        for img_base64 in image_base64_list:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}})

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

        # 根据服务商选择模型和 URL
        if api_provider == "Custom":
            selected_model = CUSTOM_MODELS.get(custom_model, "gpt-5.2")
            api_url = custom_url.rstrip('/')
            # 构建完整的 API URL
            if not api_url.endswith('/v1/chat/completions'):
                api_url = api_url + '/v1/chat/completions'
            use_stream = False  # Custom API 不使用流式
            print(f"[NakuNode Storyboard] 使用 Custom API: {selected_model}")
            print(f"[NakuNode Storyboard] Custom URL: {custom_url}")
        else:
            selected_model = SILICONFLOW_MODELS.get(siliconflow_model, "Qwen/Qwen3-VL-235B-A22B-Instruct")
            api_url = "https://api.siliconflow.cn/v1/chat/completions"  # 直接包含完整路径
            use_stream = True  # SiliconFlow 使用流式模式
            print(f"[NakuNode Storyboard] 使用 SiliconFlow API: {selected_model}")
            print(f"[NakuNode Storyboard] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")

        print(f"[NakuNode Storyboard] 请求 URL: {api_url}")
        print(f"[NakuNode Storyboard] Stream 模式：{use_stream}")

        payload = {"model": selected_model, "messages": messages, "stream": use_stream, "temperature": 0.7, "max_tokens": 4096}

        try:
            print(f"[NakuNode Storyboard] 发送 HTTP 请求...")
            
            if use_stream:
                # SiliconFlow 流式模式处理
                response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=120, verify=False)
                print(f"[NakuNode Storyboard] HTTP 状态码：{response.status_code}")

                if response.status_code == 200:
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
                    print(f"[NakuNode Storyboard] 流式响应接收完成")
                    return full_content
                else:
                    return f"Error: {response.status_code} - {response.text[:200]}"
            else:
                # Custom API 非流式模式处理
                response = requests.post(api_url, headers=headers, json=payload, timeout=120, verify=False)
                print(f"[NakuNode Storyboard] HTTP 状态码：{response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"


NODE_CLASS_MAPPINGS = {"NakuNode_分镜图片生成": StoryboardImageGenerator}
NODE_DISPLAY_NAME_MAPPINGS = {"NakuNode_分镜图片生成": "NakuNode 分镜图片生成"}
