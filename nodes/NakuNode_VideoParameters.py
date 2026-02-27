import random

# --------------------------------------------------------------------------------
# 辅助函数：用于处理随机选项
# --------------------------------------------------------------------------------
def get_random_value(data_dict, exclude_keys):
    """从字典中随机选择一个值，排除指定的键"""
    valid_keys = [k for k in data_dict.keys() if k not in exclude_keys]
    if not valid_keys:
        return ""
    random_key = random.choice(valid_keys)
    return data_dict[random_key]


# --------------------------------------------------------------------------------
# 预设数据 (来自@227/预设字典.txt 视频制作部分)
# --------------------------------------------------------------------------------

# --- 运镜方式数据 ---
CAMERA_MOVEMENTS = {
    "-- 无 --": "",
    "随机": "",
    "向前推进": "push in, camera moving forward",
    "快速推进": "crash zoom, rapid push in",
    "向后拉远": "pull back, camera moving backward",
    "缓慢拉远": "slow zoom out, gradual pull back",
    "轨道左移": "truck left, tracking shot left",
    "轨道右移": "truck right, tracking shot right",
    "水平摇摄": "pan right, horizontal pan",
    "垂直摇摄": "tilt up, vertical tilt",
    "弧形运镜": "arc shot, curved camera movement",
    "环绕运镜": "orbit shot, circling around subject",
    "摇臂升高": "crane up, rising camera movement",
    "摇臂下降": "crane down, lowering camera movement",
    "手持推进": "handheld push in, shaky cam moving forward",
    "手持跟随": "handheld tracking, following shot",
    "斯坦尼康稳定": "steadicam shot, smooth camera movement",
    "快速甩镜": "whip pan, swish pan",
    "希区柯克变焦": "dolly zoom, vertigo effect",
    "低角度仰拍": "low angle shot, looking up",
    "高角度俯拍": "high angle shot, looking down",
    "上帝视角": "top-down view, birds eye view",
    "无人机航拍": "drone shot, aerial view",
    "第一人称视角": "first person view, fpv shot",
    "过肩镜头": "over the shoulder shot, ots",
    "旋转运镜": "camera roll, rotating camera",
    "变焦推进": "zoom in, optical zoom",
    "变焦拉远": "zoom out, reverse zoom",
    "跟焦切换": "rack focus, focus pull",
    "荷兰角倾斜": "dutch angle, tilted frame",
    "侧面跟拍": "side tracking shot, profile follow",
    "固定长镜头": "static shot, locked camera",
    "子弹时间": "bullet time, frozen time effect",
    "FPV 极速穿越": "fpv drone shot, high speed fly through",
    "穿越镜头": "fly through, passing through object",
    "极速冲镜": "speed ramping, hyper speed push in",
    "揭幕拉出": "reveal shot, dolly out from behind object",
    "英雄镜头": "hero shot, low angle rising up",
    "垂直俯冲": "top down crash, drone diving shot",
    "甩尾运镜": "drift shot, sliding camera turn",
    "失重悬浮": "weightless camera, floating movement",
    "眼球特写推进": "extreme close up zoom, macro eye zoom",
    "混乱震颤": "intense shake, chaotic handheld",
    "螺旋升天": "spiral rise, ascending corkscrew shot",
    "瞬移变焦": "crash zoom in out, snap zoom",
    "倒放拉远": "reverse dolly, moving away from chaos",
    "地面滑行": "ground level slide, low tracking shot",
}

# --- 光线描述数据 ---
LIGHTING_DESCRIPTIONS = {
    "-- 无 --": "",
    "随机": "",
    "柔和顶光": "soft overhead light",
    "聚光灯效果": "spotlight effect, dramatic spotlight",
    "侧逆光": "rim light, side backlighting",
    "柔和环境光": "soft ambient light",
    "蓝紫色赛博朋克霓虹灯光": "blue and purple cyberpunk neon light",
    "青蓝与红色的赛博朋克霓虹灯光": "cyan and red cyberpunk neon light",
    "白织灯光": "incandescent lighting, warm bulb glow",
    "钨丝灯光": "tungsten lighting",
    "3200k 暖光": "3200k warm light",
    "5600k 自然光": "5600k natural daylight",
    "伦勃朗光": "rembrandt lighting",
    "蝴蝶光": "butterfly lighting, paramount lighting",
    "丁达尔效应": "tyndall effect, god rays, volumetric light beams",
    "黄金时刻": "golden hour lighting, warm sunset glow",
    "蓝调时刻": "blue hour lighting, twilight",
    "阴天漫射光": "overcast diffused light, soft cloudy sky",
    "高调照明": "high key lighting, bright and even illumination",
    "低调照明": "low key lighting, dark moody shadows",
    "分割布光": "split lighting, half face illuminated",
    "环形闪光灯": "ring flash lighting, circular catchlight",
    "柔光箱照明": "softbox lighting, studio soft light",
    "荧光灯管": "fluorescent lighting, green tint flicker",
    "烛光照明": "candlelight, flickering warm flame",
    "篝火光源": "campfire light, warm orange glow",
    "屏幕反光": "screen reflection light, monitor glow",
    "汽车前灯": "car headlights, dramatic forward lighting",
    "体积光": "volumetric lighting, foggy light scattering",
    "边缘轮廓光": "edge lighting, strong rim light",
    "正面平光": "flat front lighting, even illumination",
    "硬质直射光": "hard direct light, strong shadows",
    "月光冷调": "moonlight, cold blue night light",
    "窗户自然光": "natural window light, soft directional",
    "电影感橙青光": "cinematic teal and orange lighting",
    "双色调布光": "two-tone lighting, bicolor mood light",
    "极简留白光": "minimal bright lighting, white background light",
    "戏剧性阴影": "dramatic shadows, chiaroscuro",
    "穿透烟雾光": "light beams in smoke, atmospheric haze",
    "频闪闪光": "strobe light, flashing club light",
    "霓虹招牌光": "neon sign glow, vibrant sign reflections",
    "舞台追光": "stage follow spot, isolated subject light",
    "剪影逆光": "silhouette backlighting, strong back light",
    "地面反射光": "bounce light from ground, under lighting",
    "潮湿反射光": "wet surface reflections, rain reflections",
    "生物荧光": "bioluminescence, organic glow",
    "熔岩火光": "lava glow, intense fire heat",
    "医院冷白光": "hospital cold white light, sterile lighting",
    "复古胶片暖光": "vintage film warm tones, nostalgic lighting",
    "梦幻柔焦光": "dreamy soft focus light, ethereal glow",
    "强对比裂光": "harsh contrast lighting, stark shadows",
    "发丝轮廓光": "hair rim light, glowing hair outline",
}

# --- 视觉与后期效果数据 ---
VISUAL_EFFECTS = {
    "-- 无 --": "",
    "随机": "",
    "镜头光晕": "lens flare, anamorphic flare",
    "暗角效果": "vignette, dark edges",
    "HUD 界面": "HUD interface, heads up display overlay",
    "粒子飘散": "floating particles, dust motes",
    "延时摄影": "time lapse, hyperlapse",
    "流光轨迹": "light trails",
    "定格动画": "stop motion animation",
    "爆炸冲击波": "explosion effect, shockwave blast",
    "烟雾缭绕": "swirling smoke, atmospheric fog",
    "胶片颗粒": "film grain, vintage noise texture",
    "景深虚化": "depth of field, bokeh blur background",
    "色差故障": "chromatic aberration, RGB split",
    "数字故障": "glitch effect, digital distortion",
    "扫描线": "scanlines, CRT monitor effect",
    "运动模糊": "motion blur, dynamic blur",
    "双重曝光": "double exposure, layered imagery",
    "鱼眼畸变": "fisheye lens, barrel distortion",
    "热浪扭曲": "heat distortion, heat haze ripple",
    "全息投影": "holographic effect, hologram projection",
    "夜视效果": "night vision, green monochrome",
    "热成像仪": "thermal imaging, infrared heatmap",
    "移轴微缩": "tilt shift, miniature effect",
    "像素化风格": "pixelation, 8-bit style",
    "水波涟漪": "water ripple effect, surface distortion",
    "闪电电弧": "lightning effect, electric arc",
    "火焰燃烧": "fire effect, flames and sparks",
    "能量脉冲": "energy pulse, power wave",
    "魔法光尘": "magical particles, sparkle dust",
    "雨滴滑落": "rain drops on lens, wet glass effect",
    "雪片飘落": "falling snow, winter atmosphere",
    "墨水扩散": "ink bleed, watercolor spread",
    "玻璃破碎": "glass shatter, broken mirror effect",
    "电磁干扰": "static noise, signal interference",
    "数据流瀑布": "matrix code rain, digital stream",
    "星空浩瀚": "starfield, cosmic background",
    "极光漂浮": "aurora effect, northern lights",
    "霓虹闪烁": "neon flicker, pulsing glow",
    "高对比黑白": "high contrast black and white, noir style",
    "复古褪色": "vintage fade, desaturated nostalgia",
    "赛博故障": "cyberpunk glitch, digital artifacts",
    "老胶片划痕": "film scratches, damaged vintage film",
    "镜头污渍": "dirty lens, smudge marks",
    "眩光耀斑": "sun glare, bright burst",
    "电影黑边": "cinematic letterbox, film aspect ratio",
    "径向模糊": "radial blur, zoom blur",
    "时光倒流": "reverse motion, backwards effect",
    "悬浮物体": "floating objects, gravity defying",
    "冲击碎屑": "debris flying, impact fragments",
    "冰霜覆盖": "frost effect, ice crystals",
    "岩浆流动": "magma flow, lava texture",
}


# --------------------------------------------------------------------------------
# 节点：NakuNode 视频参数
# --------------------------------------------------------------------------------
class NakuNodeVideoParameters:
    """
    视频参数设计节点
    用于生成视频制作的提示词参数，包含运镜方式、光线描述、视觉与后期效果
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "运镜方式": (list(CAMERA_MOVEMENTS.keys()), {"default": "-- 无 --"}),
                "光线描述": (list(LIGHTING_DESCRIPTIONS.keys()), {"default": "-- 无 --"}),
                "视觉与后期效果": (list(VISUAL_EFFECTS.keys()), {"default": "-- 无 --"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("视频参数",)
    FUNCTION = "generate_params"
    CATEGORY = "NakuNode_Design_Prompt"

    def generate_params(self, camera_movement, lighting, visual_effects):
        params = []

        # 处理运镜方式
        if camera_movement == "随机":
            value = get_random_value(CAMERA_MOVEMENTS, ["-- 无 --", "随机"])
            if value:
                params.append(value)
        elif camera_movement != "-- 无 --":
            value = CAMERA_MOVEMENTS.get(camera_movement, "")
            if value:
                params.append(value)

        # 处理光线描述
        if lighting == "随机":
            value = get_random_value(LIGHTING_DESCRIPTIONS, ["-- 无 --", "随机"])
            if value:
                params.append(value)
        elif lighting != "-- 无 --":
            value = LIGHTING_DESCRIPTIONS.get(lighting, "")
            if value:
                params.append(value)

        # 处理视觉与后期效果
        if visual_effects == "随机":
            value = get_random_value(VISUAL_EFFECTS, ["-- 无 --", "随机"])
            if value:
                params.append(value)
        elif visual_effects != "-- 无 --":
            value = VISUAL_EFFECTS.get(visual_effects, "")
            if value:
                params.append(value)

        return (", ".join(filter(None, params)),)


# --------------------------------------------------------------------------------
# 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "NakuNode_VideoParameters": NakuNodeVideoParameters
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNode_VideoParameters": "NakuNode_视频参数"
}
