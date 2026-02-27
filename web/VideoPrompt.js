// NakuNode VideoPrompt Builder 前端实现
// 用于 NakuNode-单图视频提示词生成器 节点

import { app } from "/scripts/app.js";

// 预设数据 - 摄影参数（与 PromptEVO 保持一致）
const PHOTOGRAPHY_PRESET_DATA = {
    style: {
        label: "画面风格",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "赛璐璐风格", value: "anime style, cel shading" },
            { label: "厚涂风格", value: "impasto painting, thick painting" },
            { label: "伪厚涂风格", value: "semi-thick painting, soft blending" },
            { label: "写实照片", value: "photorealistic, realistic photography" },
            { label: "水彩插画", value: "watercolor illustration" },
            { label: "油画风格", value: "classic oil painting" },
            { label: "水墨画/国风", value: "traditional Chinese ink wash painting" },
            { label: "吉卜力动画风", value: "Studio Ghibli style" },
            { label: "新海诚动画风", value: "Makoto Shinkai style, anime background" },
            { label: "赛博朋克", value: "cyberpunk style, neon lights" },
            { label: "蒸汽朋克", value: "steampunk style, mechanical gears" },
            { label: "3D 高清渲染", value: "3D rendering, Octane Render, Unreal Engine 5" },
            { label: "黏土定格风", value: "claymation, 3D clay render" },
            { label: "剪纸/折纸艺术", value: "paper cutout art, layered paper illustration" },
            { label: "像素艺术", value: "pixel art, 16-bit" },
            { label: "美式漫画风", value: "American comic book style, graphic novel" },
            { label: "黑白线稿", value: "monochrome line art" },
            { label: "扁平矢量插画", value: "vector graphic illustration, flat colors" },
            { label: "日本浮世绘", value: "ukiyo-e, traditional Japanese woodblock print" },
            { label: "穆夏/塔罗牌风", value: "Art Nouveau, Alphonse Mucha style, tarot card" },
            { label: "哥特暗黑风", value: "gothic dark fantasy art" },
            { label: "波普艺术", value: "pop art, Andy Warhol style" },
            { label: "极简主义", value: "minimalism art" },
            { label: "低多边形 (Low Poly)", value: "low poly art, isometric 3D" },
            { label: "史诗原画/概念艺术", value: "epic concept art, gorgeous digital painting" }
        ]
    },
    angle: {
        label: "相机视角",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "正面视角", value: "front view" },
            { label: "侧面视角", value: "side view" },
            { label: "背面视角", value: "back view, from behind" },
            { label: "主观视角 POV", value: "POV, first-person view" },
            { label: "第三人称视角", value: "third-person view, from behind" },
            { label: "越肩视角", value: "over-the-shoulder shot" },
            { label: "荷兰角/倾斜", value: "Dutch angle, tilted frame" },
            { label: "监控/CCTV 视角", value: "CCTV security camera footage" },
            { label: "上帝视角/正俯视", value: "bird's-eye view, top-down view" },
            { label: "高机位俯拍", value: "high angle shot, looking down" },
            { label: "低机位仰拍", value: "low angle shot, looking up" },
            { label: "虫瞳视角/极低仰视", value: "worm's-eye view" },
            { label: "无人机航拍视角", value: "drone perspective, aerial view" },
            { label: "鱼眼镜头视角", value: "fisheye lens" },
            { label: "等距视角/2.5D", value: "isometric view" },
            { label: "环境大远景", value: "extreme long shot, establishing shot" },
            { label: "广角全景镜头", value: "wide-angle shot, panoramic" },
            { label: "全身镜头", value: "full body shot" },
            { label: "半身镜头", value: "medium shot, cowboy shot" },
            { label: "面部特写", value: "close-up shot, face focus" },
            { label: "眼孔/门缝窥视", value: "peeking through a keyhole, voyeuristic view" },
            { label: "镜面反射视角", value: "mirror reflection shot" },
            { label: "贴地视角", value: "ground-level shot" },
            { label: "微距视角", value: "macro photography, extreme close-up" },
            { label: "动态透视", value: "dynamic angle, extreme foreshortening" }
        ]
    },
    lens: {
        label: "镜头选择",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "超广角镜头", value: "ultra-wide angle lens" },
            { label: "广角镜头", value: "wide-angle lens" },
            { label: "标准定焦镜头", value: "standard prime lens" },
            { label: "中长焦镜头", value: "medium telephoto lens" },
            { label: "长焦镜头", value: "telephoto lens" },
            { label: "微距镜头", value: "macro lens" },
            { label: "鱼眼镜头", value: "fisheye lens" },
            { label: "移轴镜头", value: "tilt-shift lens" },
            { label: "8mm 镜头", value: "8mm lens" },
            { label: "14mm 镜头", value: "14mm lens" },
            { label: "16mm 镜头", value: "16mm lens" },
            { label: "24mm 镜头", value: "24mm lens" },
            { label: "35mm 镜头", value: "35mm lens" },
            { label: "50mm 镜头", value: "50mm lens" },
            { label: "85mm 镜头", value: "85mm lens" },
            { label: "135mm 镜头", value: "135mm lens" },
            { label: "200mm 镜头", value: "200mm lens" },
            { label: "24mm 探针镜头", value: "24mm Probe Lens" },
            { label: "16mm 探针镜头", value: "16mm Probe Lens" },
            { label: "35mm 1.33x 变形宽荧幕镜头", value: "35mm 1.33x anamorphic lens" },
            { label: "50mm 1.33x 变形宽荧幕镜头", value: "50mm 1.33x anamorphic lens" },
            { label: "50mm 1.5x 变形宽荧幕镜头", value: "50mm 1.5x anamorphic lens" },
            { label: "85mm 1.5x 变形宽荧幕镜头", value: "85mm 1.5x anamorphic lens" },
            { label: "Helios-44-2 镜头", value: "Helios-44-2 lens, swirly bokeh" },
            { label: "徕卡 Summilux 35mm 镜头", value: "Leica Summilux 35mm lens" },
            { label: "蔡司 Planar 50mm 镜头", value: "Carl Zeiss Planar 50mm lens" },
            { label: "佳能 50mm f/0.95 梦幻镜头", value: "Canon 50mm f/0.95 Dream Lens" },
            { label: "匹兹伐老式镜头", value: "Petzval lens" },
            { label: "库克 S4/i 电影镜头", value: "Cooke S4/i cine lens, Cooke look" },
            { label: "阿莱 Signature Prime 电影镜头", value: "ARRI Signature Prime lens" },
            { label: "潘那维申 Primo 电影镜头", value: "Panavision Primo lens" }
        ]
    },
    aperture: {
        label: "光圈选择",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "F0.95 极限大光圈", value: "F0.95 aperture, extreme large aperture" },
            { label: "F1.0 大光圈", value: "F1.0 aperture" },
            { label: "F1.4 大光圈", value: "F1.4 aperture, fast lens" },
            { label: "F2.8 中大光圈", value: "F2.8 aperture" },
            { label: "F4.0 光圈", value: "F4.0 aperture" },
            { label: "F5.6 中等光圈", value: "F5.6 aperture, moderate depth of field" },
            { label: "F7.1 小光圈", value: "F7.1 aperture" },
            { label: "F11 小光圈 (深景深)", value: "F11 aperture, deep depth of field" },
            { label: "F22 极小光圈", value: "F22 aperture, infinite focus" },
            { label: "浅景深", value: "shallow depth of field" },
            { label: "极浅景深", value: "extreme shallow depth of field" },
            { label: "深景深 (全景深)", value: "deep depth of field, deep focus, sharp completely" },
            { label: "背景虚化", value: "background blur, blurred background" },
            { label: "前景虚化", value: "foreground blur, out-of-focus foreground" },
            { label: "微距景深", value: "macro depth of field" },
            { label: "移轴微缩景深", value: "tilt-shift depth of field, miniature effect" },
            { label: "奶油般柔和散景", value: "creamy bokeh, smooth bokeh" },
            { label: "漩涡光斑", value: "swirly bokeh" },
            { label: "甜甜圈光斑", value: "donut bokeh, reflex lens bokeh" },
            { label: "电影感椭圆散景", value: "cinematic bokeh, anamorphic bokeh, oval bokeh" },
            { label: "心形光斑", value: "heart-shaped bokeh" },
            { label: "六角形/多边形光斑", value: "hexagonal bokeh, polygonal bokeh" },
            { label: "大光斑/光晕", value: "large bokeh circles, lens flare halo" },
            { label: "星芒效果", value: "starburst effect, sunstar" },
            { label: "柔焦景深", value: "soft focus, dreamy glow" }
        ]
    },
    composition: {
        label: "构图方式",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "三分法构图", value: "rule of thirds" },
            { label: "中心构图", value: "centered composition, centered subject" },
            { label: "对称构图", value: "symmetrical composition, perfect symmetry" },
            { label: "对角线构图", value: "diagonal composition" },
            { label: "框架构图/画中画", value: "frame within a frame, natural framing" },
            { label: "引导线构图", value: "leading lines" },
            { label: "消失点/单点透视", value: "vanishing point, 1-point perspective" },
            { label: "黄金螺旋/斐波那契", value: "golden ratio, Fibonacci spiral composition" },
            { label: "黄金三角构图", value: "golden triangle composition" },
            { label: "三角形稳定构图", value: "triangle composition" },
            { label: "S 型曲线构图", value: "S-curve composition" },
            { label: "负空间/大面积留白", value: "negative space, ample empty space" },
            { label: "填充框架/饱满构图", value: "fill the frame, cropped tightly" },
            { label: "图案与重复构图", value: "pattern and repetition composition" },
            { label: "极简主义构图", value: "minimalist composition" },
            { label: "奇数法则构图", value: "rule of odds" },
            { label: "视觉平衡/不对称平衡", value: "asymmetrical balance, visual balance" },
            { label: "前景层叠构图 (增加深度)", value: "foreground framing, multi-layered depth" },
            { label: "并列/对比构图", value: "juxtaposition composition" },
            { label: "放射线构图", value: "radiating lines composition, radial symmetry" },
            { label: "倒影平衡构图", value: "reflection composition" },
            { label: "低水平线 (强调天空)", value: "low horizon line" },
            { label: "高水平线 (强调地面)", value: "high horizon line" },
            { label: "棋盘格/网格构图", value: "grid composition, checkerboard layout" },
            { label: "破格/开放式构图", value: "breaking the frame, open composition, dynamic cropping" }
        ]
    },
    film: {
        label: "胶片风格",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "柯达 Portra 400", value: "Kodak Portra 400" },
            { label: "富士 Pro 400H", value: "Fujifilm Pro 400H" },
            { label: "柯达 金 200", value: "Kodak Gold 200" },
            { label: "柯达 ColorPlus 200", value: "Kodak ColorPlus 200" },
            { label: "柯达 Ektar 100", value: "Kodak Ektar 100" },
            { label: "富士 Velvia 50", value: "Fujifilm Velvia 50" },
            { label: "富士 Provia 100F", value: "Fujifilm Provia 100F" },
            { label: "CineStill 800T", value: "CineStill 800T" },
            { label: "CineStill 50D", value: "CineStill 50D" },
            { label: "柯达 Vision3 500T", value: "Kodak Vision3 500T" },
            { label: "柯达 Kodachrome", value: "Kodak Kodachrome" },
            { label: "富士 Superia 400", value: "Fujifilm Superia X-TRA 400" },
            { label: "富士 Natura 1600", value: "Fujifilm Natura 1600" },
            { label: "宝丽来 SX-70", value: "Polaroid SX-70" },
            { label: "柯达 Aerochrome", value: "Kodak Aerochrome" }
        ]
    }
};

// 视频参数预设数据（来自预设字典.txt - 视频制作部分）
const VIDEO_PRESET_DATA = {
    cameraMovement: {
        label: "运镜方式",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "向前推进", value: "push in, camera moving forward" },
            { label: "快速推进", value: "crash zoom, rapid push in" },
            { label: "向后拉远", value: "pull back, camera moving backward" },
            { label: "缓慢拉远", value: "slow zoom out, gradual pull back" },
            { label: "轨道左移", value: "truck left, tracking shot left" },
            { label: "轨道右移", value: "truck right, tracking shot right" },
            { label: "水平摇摄", value: "pan right, horizontal pan" },
            { label: "垂直摇摄", value: "tilt up, vertical tilt" },
            { label: "弧形运镜", value: "arc shot, curved camera movement" },
            { label: "环绕运镜", value: "orbit shot, circling around subject" },
            { label: "摇臂升高", value: "crane up, rising camera movement" },
            { label: "摇臂下降", value: "crane down, lowering camera movement" },
            { label: "手持推进", value: "handheld push in, shaky cam moving forward" },
            { label: "手持跟随", value: "handheld tracking, following shot" },
            { label: "斯坦尼康稳定", value: "steadicam shot, smooth camera movement" },
            { label: "快速甩镜", value: "whip pan, swish pan" },
            { label: "希区柯克变焦", value: "dolly zoom, vertigo effect" },
            { label: "低角度仰拍", value: "low angle shot, looking up" },
            { label: "高角度俯拍", value: "high angle shot, looking down" },
            { label: "上帝视角", value: "top-down view, birds eye view" },
            { label: "无人机航拍", value: "drone shot, aerial view" },
            { label: "第一人称视角", value: "first person view, fpv shot" },
            { label: "过肩镜头", value: "over the shoulder shot, ots" },
            { label: "旋转运镜", value: "camera roll, rotating camera" },
            { label: "变焦推进", value: "zoom in, optical zoom" },
            { label: "变焦拉远", value: "zoom out, reverse zoom" },
            { label: "跟焦切换", value: "rack focus, focus pull" },
            { label: "荷兰角倾斜", value: "dutch angle, tilted frame" },
            { label: "侧面跟拍", value: "side tracking shot, profile follow" },
            { label: "固定长镜头", value: "static shot, locked camera" },
            { label: "子弹时间", value: "bullet time, frozen time effect" },
            { label: "FPV 极速穿越", value: "fpv drone shot, high speed fly through" },
            { label: "穿越镜头", value: "fly through, passing through object" },
            { label: "极速冲镜", value: "speed ramping, hyper speed push in" },
            { label: "揭幕拉出", value: "reveal shot, dolly out from behind object" },
            { label: "英雄镜头", value: "hero shot, low angle rising up" },
            { label: "垂直俯冲", value: "top down crash, drone diving shot" },
            { label: "甩尾运镜", value: "drift shot, sliding camera turn" },
            { label: "失重悬浮", value: "weightless camera, floating movement" },
            { label: "眼球特写推进", value: "extreme close up zoom, macro eye zoom" },
            { label: "混乱震颤", value: "intense shake, chaotic handheld" },
            { label: "螺旋升天", value: "spiral rise, ascending corkscrew shot" },
            { label: "瞬移变焦", value: "crash zoom in out, snap zoom" },
            { label: "倒放拉远", value: "reverse dolly, moving away from chaos" },
            { label: "地面滑行", value: "ground level slide, low tracking shot" }
        ]
    },
    lighting: {
        label: "光线描述",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "柔和顶光", value: "soft overhead light" },
            { label: "聚光灯效果", value: "spotlight effect, dramatic spotlight" },
            { label: "侧逆光", value: "rim light, side backlighting" },
            { label: "柔和环境光", value: "soft ambient light" },
            { label: "蓝紫色赛博朋克霓虹灯光", value: "blue and purple cyberpunk neon light" },
            { label: "青蓝与红色的赛博朋克霓虹灯光", value: "cyan and red cyberpunk neon light" },
            { label: "白织灯光", value: "incandescent lighting, warm bulb glow" },
            { label: "钨丝灯光", value: "tungsten lighting" },
            { label: "3200k 暖光", value: "3200k warm light" },
            { label: "5600k 自然光", value: "5600k natural daylight" },
            { label: "伦勃朗光", value: "rembrandt lighting" },
            { label: "蝴蝶光", value: "butterfly lighting, paramount lighting" },
            { label: "丁达尔效应", value: "tyndall effect, god rays, volumetric light beams" },
            { label: "黄金时刻", value: "golden hour lighting, warm sunset glow" },
            { label: "蓝调时刻", value: "blue hour lighting, twilight" },
            { label: "阴天漫射光", value: "overcast diffused light, soft cloudy sky" },
            { label: "高调照明", value: "high key lighting, bright and even illumination" },
            { label: "低调照明", value: "low key lighting, dark moody shadows" },
            { label: "分割布光", value: "split lighting, half face illuminated" },
            { label: "环形闪光灯", value: "ring flash lighting, circular catchlight" },
            { label: "柔光箱照明", value: "softbox lighting, studio soft light" },
            { label: "荧光灯管", value: "fluorescent lighting, green tint flicker" },
            { label: "烛光照明", value: "candlelight, flickering warm flame" },
            { label: "篝火光源", value: "campfire light, warm orange glow" },
            { label: "屏幕反光", value: "screen reflection light, monitor glow" },
            { label: "汽车前灯", value: "car headlights, dramatic forward lighting" },
            { label: "体积光", value: "volumetric lighting, foggy light scattering" },
            { label: "边缘轮廓光", value: "edge lighting, strong rim light" },
            { label: "正面平光", value: "flat front lighting, even illumination" },
            { label: "硬质直射光", value: "hard direct light, strong shadows" },
            { label: "月光冷调", value: "moonlight, cold blue night light" },
            { label: "窗户自然光", value: "natural window light, soft directional" },
            { label: "电影感橙青光", value: "cinematic teal and orange lighting" },
            { label: "双色调布光", value: "two-tone lighting, bicolor mood light" },
            { label: "极简留白光", value: "minimal bright lighting, white background light" },
            { label: "戏剧性阴影", value: "dramatic shadows, chiaroscuro" },
            { label: "穿透烟雾光", value: "light beams in smoke, atmospheric haze" },
            { label: "频闪闪光", value: "strobe light, flashing club light" },
            { label: "霓虹招牌光", value: "neon sign glow, vibrant sign reflections" },
            { label: "舞台追光", value: "stage follow spot, isolated subject light" },
            { label: "剪影逆光", value: "silhouette backlighting, strong back light" },
            { label: "地面反射光", value: "bounce light from ground, under lighting" },
            { label: "潮湿反射光", value: "wet surface reflections, rain reflections" },
            { label: "生物荧光", value: "bioluminescence, organic glow" },
            { label: "熔岩火光", value: "lava glow, intense fire heat" },
            { label: "医院冷白光", value: "hospital cold white light, sterile lighting" },
            { label: "复古胶片暖光", value: "vintage film warm tones, nostalgic lighting" },
            { label: "梦幻柔焦光", value: "dreamy soft focus light, ethereal glow" },
            { label: "强对比裂光", value: "harsh contrast lighting, stark shadows" },
            { label: "发丝轮廓光", value: "hair rim light, glowing hair outline" }
        ]
    },
    visualEffects: {
        label: "视觉与后期效果",
        options: [
            { label: "无", value: "none" },
            { label: "随机", value: "random" },
            { label: "镜头光晕", value: "lens flare, anamorphic flare" },
            { label: "暗角效果", value: "vignette, dark edges" },
            { label: "HUD 界面", value: "HUD interface, heads up display overlay" },
            { label: "粒子飘散", value: "floating particles, dust motes" },
            { label: "延时摄影", value: "time lapse, hyperlapse" },
            { label: "流光轨迹", value: "light trails" },
            { label: "定格动画", value: "stop motion animation" },
            { label: "爆炸冲击波", value: "explosion effect, shockwave blast" },
            { label: "烟雾缭绕", value: "swirling smoke, atmospheric fog" },
            { label: "胶片颗粒", value: "film grain, vintage noise texture" },
            { label: "景深虚化", value: "depth of field, bokeh blur background" },
            { label: "色差故障", value: "chromatic aberration, RGB split" },
            { label: "数字故障", value: "glitch effect, digital distortion" },
            { label: "扫描线", value: "scanlines, CRT monitor effect" },
            { label: "运动模糊", value: "motion blur, dynamic blur" },
            { label: "双重曝光", value: "double exposure, layered imagery" },
            { label: "鱼眼畸变", value: "fisheye lens, barrel distortion" },
            { label: "热浪扭曲", value: "heat distortion, heat haze ripple" },
            { label: "全息投影", value: "holographic effect, hologram projection" },
            { label: "夜视效果", value: "night vision, green monochrome" },
            { label: "热成像仪", value: "thermal imaging, infrared heatmap" },
            { label: "移轴微缩", value: "tilt shift, miniature effect" },
            { label: "像素化风格", value: "pixelation, 8-bit style" },
            { label: "水波涟漪", value: "water ripple effect, surface distortion" },
            { label: "闪电电弧", value: "lightning effect, electric arc" },
            { label: "火焰燃烧", value: "fire effect, flames and sparks" },
            { label: "能量脉冲", value: "energy pulse, power wave" },
            { label: "魔法光尘", value: "magical particles, sparkle dust" },
            { label: "雨滴滑落", value: "rain drops on lens, wet glass effect" },
            { label: "雪片飘落", value: "falling snow, winter atmosphere" },
            { label: "墨水扩散", value: "ink bleed, watercolor spread" },
            { label: "玻璃破碎", value: "glass shatter, broken mirror effect" },
            { label: "电磁干扰", value: "static noise, signal interference" },
            { label: "数据流瀑布", value: "matrix code rain, digital stream" },
            { label: "星空浩瀚", value: "starfield, cosmic background" },
            { label: "极光漂浮", value: "aurora effect, northern lights" },
            { label: "霓虹闪烁", value: "neon flicker, pulsing glow" },
            { label: "高对比黑白", value: "high contrast black and white, noir style" },
            { label: "复古褪色", value: "vintage fade, desaturated nostalgia" },
            { label: "赛博故障", value: "cyberpunk glitch, digital artifacts" },
            { label: "老胶片划痕", value: "film scratches, damaged vintage film" },
            { label: "镜头污渍", value: "dirty lens, smudge marks" },
            { label: "眩光耀斑", value: "sun glare, bright burst" },
            { label: "电影黑边", value: "cinematic letterbox, film aspect ratio" },
            { label: "径向模糊", value: "radial blur, zoom blur" },
            { label: "时光倒流", value: "reverse motion, backwards effect" },
            { label: "悬浮物体", value: "floating objects, gravity defying" },
            { label: "冲击碎屑", value: "debris flying, impact fragments" },
            { label: "冰霜覆盖", value: "frost effect, ice crystals" },
            { label: "岩浆流动", value: "magma flow, lava texture" }
        ]
    }
};

// 随机选择函数
function getRandomValue(options) {
    const validOptions = options.filter(opt => opt.value !== "none" && opt.value !== "random");
    if (validOptions.length === 0) return "";
    const randomIndex = Math.floor(Math.random() * validOptions.length);
    return validOptions[randomIndex].value;
}

// 创建下拉选择器
function createSelectWidget(category, subcategory, presetData, onChange) {
    const container = document.createElement('div');
    container.style.marginBottom = '10px';

    const label = document.createElement('label');
    label.textContent = presetData.label;
    label.style.display = 'block';
    label.style.marginBottom = '5px';
    label.style.fontSize = '13px';
    label.style.color = '#AAAAAA';

    const select = document.createElement('select');
    select.style.width = '100%';
    select.style.padding = '8px';
    select.style.border = '1px solid #40444B';
    select.style.borderRadius = '4px';
    select.style.backgroundColor = '#2F3136';
    select.style.color = 'white';
    select.style.fontSize = '14px';
    select.style.cursor = 'pointer';

    presetData.options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.label;
        select.appendChild(option);
    });

    select.addEventListener('change', () => {
        onChange(category, subcategory, select.value);
    });

    container.appendChild(label);
    container.appendChild(select);
    return container;
}

// 创建分类标题
function createCategoryTitle(title) {
    const titleEl = document.createElement('div');
    titleEl.textContent = title;
    titleEl.style.fontSize = '16px';
    titleEl.style.fontWeight = 'bold';
    titleEl.style.marginTop = '20px';
    titleEl.style.marginBottom = '10px';
    titleEl.style.paddingBottom = '5px';
    titleEl.style.borderBottom = '2px solid #43B581';
    titleEl.style.color = '#43B581';
    return titleEl;
}

// 注册扩展
app.registerExtension({
    name: "NakuNode.VideoPromptBuilder",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Support ImageVideoPromptOptimizer, DualImageVideoScriptGenerator, NakuNode_LTX_FTE_Prompter, NakuNodeLTXPrompter, and ProfessionalVideoPromptGenerator nodes
        if (nodeData.name === "ImageVideoPromptOptimizer" || nodeData.name === "DualImageVideoScriptGenerator" || nodeData.name === "NakuNode_LTX_FTE_Prompter" || nodeData.name === "NakuNodeLTXPrompter" || nodeData.name === "ProfessionalVideoPromptGenerator") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                // 添加 "Create it!" 按钮
                this.addWidget("button", "Create it!", null, this.openPromptBuilder.bind(this));

                return result;
            };

            // 打开提示词构建器
            nodeType.prototype.openPromptBuilder = function() {
                this.createPromptBuilderPopup();
            };

            // 创建提示词构建器弹窗
            nodeType.prototype.createPromptBuilderPopup = function() {
                const self = this;
                const isDualImageNode = nodeData.name === "DualImageVideoScriptGenerator" || nodeData.name === "NakuNode_LTX_FTE_Prompter";
                const isLTXPrompterNode = nodeData.name === "NakuNodeLTXPrompter";
                const isProfessionalVideoNode = nodeData.name === "ProfessionalVideoPromptGenerator";

                // 创建遮罩层
                const overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '100%';
                overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
                overlay.style.zIndex = '9999';
                overlay.style.display = 'flex';
                overlay.style.justifyContent = 'center';
                overlay.style.alignItems = 'center';
                overlay.style.overflow = 'auto';

                // 创建主容器
                const mainContainer = document.createElement('div');
                mainContainer.style.width = '95%';
                mainContainer.style.maxWidth = '1200px';
                mainContainer.style.maxHeight = '90vh';
                mainContainer.style.backgroundColor = '#36393F';
                mainContainer.style.borderRadius = '8px';
                mainContainer.style.padding = '20px';
                mainContainer.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
                mainContainer.style.display = 'flex';
                mainContainer.style.flexDirection = 'column';
                mainContainer.style.color = 'white';
                mainContainer.style.overflow = 'auto';

                // 创建标题
                const title = document.createElement('div');
                title.textContent = isDualImageNode ? 'NakuNode Dual Image Video Prompt Builder' : 'NakuNode Video Prompt Builder';
                title.style.fontSize = '20px';
                title.style.fontWeight = 'bold';
                title.style.marginBottom = '15px';
                title.style.textAlign = 'center';
                title.style.color = '#43B581';

                // 创建内容区域（可滚动）
                const contentArea = document.createElement('div');
                contentArea.style.flex = '1';
                contentArea.style.overflow = 'auto';
                contentArea.style.padding = '10px';

                // 存储用户选择
                const selections = {
                    photography: {},
                    video: {}
                };

                // 初始化 selections
                Object.keys(PHOTOGRAPHY_PRESET_DATA).forEach(key => {
                    selections.photography[key] = 'none';
                });
                Object.keys(VIDEO_PRESET_DATA).forEach(key => {
                    selections.video[key] = 'none';
                });

                // 创建摄影参数区域
                contentArea.appendChild(createCategoryTitle('📷 摄影参数'));
                Object.keys(PHOTOGRAPHY_PRESET_DATA).forEach(key => {
                    contentArea.appendChild(createSelectWidget('photography', key, PHOTOGRAPHY_PRESET_DATA[key], (cat, subcat, value) => {
                        selections[cat][subcat] = value;
                    }));
                });

                // 创建视频参数区域
                contentArea.appendChild(createCategoryTitle('🎬 视频参数'));
                Object.keys(VIDEO_PRESET_DATA).forEach(key => {
                    contentArea.appendChild(createSelectWidget('video', key, VIDEO_PRESET_DATA[key], (cat, subcat, value) => {
                        selections[cat][subcat] = value;
                    }));
                });

                // 创建按钮容器
                const buttonContainer = document.createElement('div');
                buttonContainer.style.display = 'flex';
                buttonContainer.style.gap = '10px';
                buttonContainer.style.justifyContent = 'center';
                buttonContainer.style.marginTop = '20px';
                buttonContainer.style.paddingTop = '15px';
                buttonContainer.style.borderTop = '1px solid #40444B';

                // 取消按钮
                const cancelButton = document.createElement('button');
                cancelButton.textContent = '取消';
                cancelButton.style.height = '35px';
                cancelButton.style.padding = '0 30px';
                cancelButton.style.border = '1px solid #40444B';
                cancelButton.style.borderRadius = '4px';
                cancelButton.style.backgroundColor = '#4F545C';
                cancelButton.style.color = 'white';
                cancelButton.style.cursor = 'pointer';
                cancelButton.style.fontSize = '14px';
                cancelButton.onmouseover = () => cancelButton.style.backgroundColor = '#5E6269';
                cancelButton.onmouseout = () => cancelButton.style.backgroundColor = '#4F545C';
                cancelButton.onclick = () => {
                    document.body.removeChild(overlay);
                };

                // 确认按钮
                const confirmButton = document.createElement('button');
                confirmButton.textContent = '确认';
                confirmButton.style.height = '35px';
                confirmButton.style.padding = '0 30px';
                confirmButton.style.border = '1px solid #40444B';
                confirmButton.style.borderRadius = '4px';
                confirmButton.style.backgroundColor = '#43B581';
                confirmButton.style.color = 'white';
                confirmButton.style.cursor = 'pointer';
                confirmButton.style.fontSize = '14px';
                confirmButton.onmouseover = () => confirmButton.style.backgroundColor = '#3CA374';
                confirmButton.onmouseout = () => confirmButton.style.backgroundColor = '#43B581';
                confirmButton.onclick = async () => {
                    // 处理用户选择，生成提示词
                    const promptParts = processSelections(selections);
                    const generatedPrompt = promptParts.join('.');

                    console.log("\n[NakuNode-VideoPrompt] ╔════════════════════════════════════════════════════════╗");
                    console.log("[NakuNode-VideoPrompt] ║     Video Prompt Builder - Generated Parameters        ║");
                    console.log("[NakuNode-VideoPrompt] ╚════════════════════════════════════════════════════════╝");
                    console.log(`[NakuNode-VideoPrompt] Full prompt string: ${generatedPrompt}`);

                    // 解析并显示每个分类的参数
                    if (promptParts.length >= 1 && promptParts[0]) {
                        console.log("\n[NakuNode-VideoPrompt] 📷 Photography Parameters:");
                        promptParts[0].split(',').forEach((item, i) => console.log(`  ${i+1}. ${item}`));
                    }

                    if (promptParts.length >= 2 && promptParts[1]) {
                        console.log("\n[NakuNode-VideoPrompt] 🎬 Video Parameters:");
                        promptParts[1].split(',').forEach((item, i) => console.log(`  ${i+1}. ${item}`));
                    }

                    // 更新节点的输入字段
                    if (self.widgets) {
                        for (let i = 0; i < self.widgets.length; i++) {
                            const widget = self.widgets[i];
                            // For ImageVideoPromptOptimizer, update user_prompt
                            // For DualImageVideoScriptGenerator, update 用户描述
                            // For NakuNode_LTX_FTE_Prompter, NakuNodeLTXPrompter, and ProfessionalVideoPromptGenerator, update User_Description
                            if (widget.name === "user_prompt" || widget.name === "用户描述" || widget.name === "User_Description") {
                                // 将生成的提示词追加到现有内容后面
                                const currentValue = widget.value || "";
                                const newValue = currentValue ? `${currentValue}.${generatedPrompt}` : generatedPrompt;
                                widget.value = newValue;
                                console.log(`\n[NakuNode-VideoPrompt] ✅ Saved to ${widget.name} field`);
                                break;
                            }
                        }
                    }

                    // 移除弹窗
                    document.body.removeChild(overlay);

                    // 标记画布为脏，强制刷新
                    app.graph.setDirtyCanvas(true, true);

                    console.log("\n[NakuNode-VideoPrompt] 🎉 Video prompt generated and saved. Please manually execute the workflow.");
                };

                // 添加按钮到容器
                buttonContainer.appendChild(cancelButton);
                buttonContainer.appendChild(confirmButton);

                // 组装界面
                mainContainer.appendChild(title);
                mainContainer.appendChild(contentArea);
                mainContainer.appendChild(buttonContainer);
                overlay.appendChild(mainContainer);

                // 添加到页面
                document.body.appendChild(overlay);
            };
        }
    }
});

// 处理用户选择，生成提示词
function processSelections(selections) {
    const result = [];

    // 处理摄影参数
    const photographyParts = [];
    Object.keys(selections.photography).forEach(key => {
        const value = selections.photography[key];
        if (value === 'random') {
            const randomValue = getRandomValue(PHOTOGRAPHY_PRESET_DATA[key].options);
            if (randomValue) {
                photographyParts.push(randomValue);
            }
        } else if (value !== 'none' && value !== 'random') {
            // 找到对应的输出值
            const option = PHOTOGRAPHY_PRESET_DATA[key].options.find(opt => opt.value === value);
            if (option && option.value !== 'none') {
                photographyParts.push(option.value);
            }
        }
    });
    if (photographyParts.length > 0) {
        result.push(photographyParts.join(','));
    }

    // 处理视频参数
    const videoParts = [];
    Object.keys(selections.video).forEach(key => {
        const value = selections.video[key];
        if (value === 'random') {
            const randomValue = getRandomValue(VIDEO_PRESET_DATA[key].options);
            if (randomValue) {
                videoParts.push(randomValue);
            }
        } else if (value !== 'none' && value !== 'random') {
            const option = VIDEO_PRESET_DATA[key].options.find(opt => opt.value === value);
            if (option && option.value !== 'none') {
                videoParts.push(option.value);
            }
        }
    });
    if (videoParts.length > 0) {
        result.push(videoParts.join(','));
    }

    return result;
}
