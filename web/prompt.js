// NakuNode-PromptEVO 前端实现

import { app } from "/scripts/app.js";

// 预设数据
const PRESET_DATA = {
    // 摄影参数
    photography: {
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
    },
    // 人物设计
    character: {
        nationality: {
            label: "人物国籍",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "中国人", value: "Chinese" },
                { label: "日本人", value: "Japanese" },
                { label: "韩国人", value: "Korean" },
                { label: "东亚人 (黄种人)", value: "East Asian" },
                { label: "亚洲人", value: "Asian" },
                { label: "东南亚人", value: "Southeast Asian" },
                { label: "南亚人 (如印度裔)", value: "South Asian, Indian" },
                { label: "中东/阿拉伯人", value: "Middle Eastern, Arab" },
                { label: "白种人", value: "Caucasian, White" },
                { label: "黑种人", value: "Black, African descent" },
                { label: "非洲人", value: "African" },
                { label: "欧洲人", value: "European" },
                { label: "北欧人 (斯堪的纳维亚)", value: "Nordic, Scandinavian" },
                { label: "俄罗斯/斯拉夫人", value: "Russian, Slavic" },
                { label: "英国人", value: "British" },
                { label: "法国人", value: "French" },
                { label: "意大利人", value: "Italian" },
                { label: "地中海人", value: "Mediterranean" },
                { label: "拉美裔/西班牙裔", value: "Hispanic, Latino" },
                { label: "北美人 (美国/加拿大)", value: "North American" },
                { label: "南美人", value: "South American" },
                { label: "澳洲/大洋洲人", value: "Australian, Oceanian" },
                { label: "太平洋岛民", value: "Pacific Islander, Polynesian" },
                { label: "原住民/土著", value: "Indigenous, Native" },
                { label: "混血儿", value: "Mixed race, Biracial" }
            ]
        },
        gender: {
            label: "人物性别",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "男性", value: "male" },
                { label: "女性", value: "female" },
                { label: "跨性别男性", value: "transgender male, transman, FTM" },
                { label: "跨性别女性", value: "transgender female, transwoman, MTF" },
                { label: "非二元性别", value: "non-binary, enby" },
                { label: "伪娘/男娘", value: "femboy, otokonoko, crossdressing male" },
                { label: "人妖", value: "ladyboy, kathoey" },
                { label: "中性/雌雄同体", value: "androgynous, genderless" },
                { label: "假小子/男装丽人", value: "tomboy, crossdressing female" },
                { label: "流体性别", value: "genderfluid" }
            ]
        },
        age: {
            label: "人物年龄",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "婴儿", value: "baby, infant" },
                { label: "幼儿", value: "toddler, little kid" },
                { label: "儿童", value: "child, kid" },
                { label: "孩子气的", value: "childish, childlike appearance" },
                { label: "小学生", value: "elementary school student, primary schooler" },
                { label: "10 岁", value: "10 years old, 10yo" },
                { label: "少年/少女", value: "early teenager" },
                { label: "中学生", value: "middle school student, junior high student" },
                { label: "15 岁", value: "15 years old, 15yo" },
                { label: "青少年", value: "teenager, adolescent, teen" },
                { label: "高中生", value: "high school student, highschooler" },
                { label: "18 岁", value: "18 years old, 18yo" },
                { label: "年轻的", value: "young, youthful" },
                { label: "大学生", value: "college student, university student" },
                { label: "二十多岁 (青年)", value: "young adult, in twenties, 20s" },
                { label: "轻熟的", value: "young mature, sophisticated, late 20s to early 30s" },
                { label: "三十多岁", value: "in thirties, 30s" },
                { label: "成熟的", value: "mature, mature appearance" },
                { label: "成年人", value: "adult, grown-up" },
                { label: "中年人", value: "middle-aged, middle age" },
                { label: "四十多岁", value: "in forties, 40s" },
                { label: "五十多岁", value: "in fifties, 50s" },
                { label: "六十多岁", value: "in sixties, 60s" },
                { label: "老年人 (长者)", value: "elderly, old person" },
                { label: "高龄老人 (80 岁以上)", value: "80 years old, frail elderly" }
            ]
        },
        body: {
            label: "人物体型",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "苗条", value: "slim, slender" },
                { label: "极瘦/骨感", value: "skinny, bony, emaciated" },
                { label: "娇小", value: "petite, small stature, tiny" },
                { label: "修长/高瘦", value: "tall and lanky, willowy" },
                { label: "薄肌/精壮", value: "lean muscle, toned body, lithe" },
                { label: "运动员身材", value: "athletic body, fitness body" },
                { label: "肌肉发达", value: "muscular, well-built" },
                { label: "健美/魔鬼肌肉", value: "bodybuilder, heavily muscled, shredded" },
                { label: "魁梧/壮硕", value: "burly, hulking, massive body" },
                { label: "微胖/肉感", value: "chubby, softly plump, fleshy" },
                { label: "丰满/曲线优美", value: "voluptuous, curvy body, thick" },
                { label: "肥胖", value: "fat, obese, overweight" },
                { label: "老爹身材/啤酒肚", value: "dad bod, potbelly" },
                { label: "梨形身材", value: "pear-shaped body, bottom-heavy" },
                { label: "沙漏型身材", value: "hourglass figure, snatched waist" },
                { label: "倒三角身材", value: "inverted triangle body, broad shoulders narrow waist" },
                { label: "苹果形身材", value: "apple-shaped body, top-heavy" },
                { label: "模特身材", value: "model body, high fashion proportions, tall and slim" },
                { label: "九头身", value: "9-heads tall proportions, extremely long legs" },
                { label: "丰乳肥臀", value: "thicc, large breasts and wide hips" },
                { label: "平胸/中性身材", value: "flat chest, washboard, androgynous body" },
                { label: "宽肩", value: "broad shoulders, wide shoulders" },
                { label: "水蛇腰/极细腰", value: "tiny waist, wasp waist" },
                { label: "瑜伽身材/柔韧", value: "yoga body, flexible body, limber" },
                { label: "半机械身体", value: "cyborg body, cybernetic implants" },
                { label: "全机械/仿生人身体", value: "android body, robotic body, mechanical joints" },
                { label: "巨人的身体", value: "giant body, towering stature" },
                { label: "侏儒/矮人身材", value: "dwarf proportions, short and stocky" },
                { label: "兽人的身体", value: "beastman body, orc body, muscular humanoid beast" },
                { label: "精灵般的体态", value: "ethereal body, elven physiology, graceful" },
                { label: "恶魔般的身材", value: "demonic body, succubus/incubus figure" },
                { label: "触手/异种身体", value: "tentacles on body, eldritch body, xenomorph" },
                { label: "怪物/畸变身体", value: "monstrous body, mutated body, grotesque" },
                { label: "液态/史莱姆身体", value: "liquid body, slime girl/boy figure" },
                { label: "孕妇体态", value: "pregnant body, maternity body, pregnant belly" }
            ]
        },
        clothing: {
            label: "人物服装",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "学生装", value: "school uniform, student uniform" },
                { label: "水手服", value: "sailor suit, sailor uniform, seifuku" },
                { label: "日式校服/死库水", value: "school swimsuit, sukumizu" },
                { label: "休闲装", value: "casual wear, t-shirt and jeans" },
                { label: "连帽衫/卫衣", value: "hoodie, oversized hoodie" },
                { label: "针织毛衣", value: "knit sweater, ribbed sweater, turtleneck" },
                { label: "吊带连衣裙/夏日裙", value: "sundress, camisole dress" },
                { label: "睡衣/真丝睡袍", value: "pajamas, sleepwear, silk robe, negligee" },
                { label: "运动服/体操服", value: "sportswear, gym clothes, track suit" },
                { label: "瑜伽服", value: "yoga pants, sports bra, athletic wear" },
                { label: "商务西装/套装", value: "business suit, formal suit, tie, office lady (OL) outfit" },
                { label: "燕尾服", value: "tuxedo, tailcoat, bowtie" },
                { label: "华丽晚礼服", value: "evening gown, graceful dress, elegant dress" },
                { label: "婚纱", value: "wedding dress, bridal gown, lace veil" },
                { label: "旗袍", value: "cheongsam, qipao, china dress" },
                { label: "和服/浴衣", value: "kimono, yukata, floral pattern, obi" },
                { label: "汉服", value: "hanfu, traditional chinese clothes, wide sleeves" },
                { label: "华丽长外套", value: "ornate long coat, fancy trench coat, tailored coat" },
                { label: "防风大衣/风衣", value: "trench coat, winter coat, overcoat" },
                { label: "斗篷/披风", value: "cape, cloak, hooded cloak" },
                { label: "中世纪骑士盔甲", value: "plate armor, knight armor, gauntlets" },
                { label: "刺客装束/夜行衣", value: "assassin outfit, stealth suit, hood and dark clothes" },
                { label: "魔法少女装", value: "magical girl outfit, frilled skirt, magical girl attire" },
                { label: "女巫服", value: "witch dress, witch hat, wizard robe" },
                { label: "奇幻修女装/祭司服", value: "nun outfit, priestess robe, fantasy habit" },
                { label: "宇航服", value: "spacesuit, astronaut suit, space helmet" },
                { label: "赛博朋克服装", value: "cyberpunk clothes, neon glowing accents, futuristic fashion" },
                { label: "机甲驾驶服/战斗紧身衣", value: "plugsuit, mecha pilot suit, form-fitting bodysuit" },
                { label: "乳胶紧身衣/皮带衣", value: "latex bodysuit, catsuit, tight leather suit" },
                { label: "机能风/高科技服装", value: "techwear, tactical clothing, straps and buckles" },
                { label: "废土风/末日生存装", value: "post-apocalyptic clothes, wasteland scavenger gear, tattered clothes" },
                { label: "蒸汽朋克服装", value: "steampunk clothes, corset, brass details, goggles" },
                { label: "洛丽塔服装", value: "lolita fashion, classical lolita, frills and lace" },
                { label: "哥特裙装", value: "gothic dress, gothic fashion, dark elegant clothes" },
                { label: "朋克风/摇滚装", value: "punk fashion, spiked leather jacket, ripped jeans" },
                { label: "地雷系/量产型服装", value: "jirai kei, girly and dark" },
                { label: "内衣", value: "underwear, lingerie, bra and panties, lace underwear" },
                { label: "三点式泳衣", value: "bikini, two-piece swimsuit, string bikini" },
                { label: "女仆装", value: "maid outfit, french maid, frilled apron, headpiece" },
                { label: "护士服", value: "nurse uniform, nurse cap, clinical outfit" },
                { label: "军装/警服", value: "military uniform, police uniform, brass buttons, epaulettes" },
                { label: "工装/背带裤", value: "overalls, dungarees, cargo pants, workwear" },
                { label: "兔女郎装", value: "bunny girl outfit, bunny ears headband, leotard, fishnet tights" },
                { label: "海盗装束", value: "pirate outfit, tricorn hat, swashbuckler gear, eye patch" },
                { label: "战损装/破损衣物", value: "torn clothes, battle-damaged outfit, shredded garments, torn edges" }
            ]
        },
        expression: {
            label: "人物表情",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "微笑", value: "smile, smiling, gentle smile" },
                { label: "大笑", value: "laughing, big smile, open mouth laugh" },
                { label: "愤怒", value: "angry, furious, mad, angry eyes" },
                { label: "沉思", value: "pensive, deep in thought, contemplative" },
                { label: "困惑", value: "confused, puzzled, tilted head" },
                { label: "敬畏", value: "awestruck, in awe, amazed" },
                { label: "好奇", value: "curious, inquisitive" },
                { label: "紧张", value: "nervous, anxious, sweating" },
                { label: "歇斯底里", value: "hysterical, manic, crazed expression" },
                { label: "充满敌意", value: "hostile, glaring, aggressive stare" },
                { label: "充满希望", value: "hopeful, bright eyes, optimistic" },
                { label: "冥想/平静", value: "serene, tranquil, meditating, eyes closed peacefully" },
                { label: "冷漠/面无表情", value: "expressionless, blank face, apathetic, emotionless" },
                { label: "悲伤/落泪", value: "sad, crying, weeping, tears, sorrow" },
                { label: "恐惧/惊恐", value: "terrified, scared, horrified, pale face" },
                { label: "惊讶/震惊", value: "shocked, surprised, wide-eyed, jaw drop" },
                { label: "害羞/脸红", value: "shy, blushing, flushed face" },
                { label: "得意/傲慢", value: "smug, smirk, arrogant, knowing smile" },
                { label: "厌恶/嫌弃", value: "disgusted, grimacing, sneer, looking down" },
                { label: "调皮/吐舌头", value: "playful, tongue out, winking, cheekiness" },
                { label: "疲惫/困倦", value: "tired, exhausted, sleepy, heavy eyelids" },
                { label: "沮丧/失落", value: "depressed, gloomy, looking down, downcast eyes" },
                { label: "狂喜/极度兴奋", value: "ecstatic, overjoyed, euphoric" },
                { label: "痛苦/挣扎", value: "in pain, agonizing, wincing, gritting teeth" },
                { label: "诱惑/抛媚眼", value: "seductive, alluring, bedroom eyes, flirty" },
                { label: "坚定/决心", value: "determined, resolute, intense gaze, serious" },
                { label: "疯狂/病娇", value: "crazy smile, yandere, unhinged, crazy eyes" },
                { label: "呆滞/失神", value: "blank stare, lifeless eyes, vacant expression, empty eyes" },
                { label: "委屈/撇嘴", value: "aggrieved, pouting, pouting lips, sad eyes" },
                { label: "阴险/狡诈", value: "sinister smile, evil grin, deceitful" },
                { label: "怀疑/不信", value: "suspicious, squinting, distrustful" },
                { label: "嘲讽/讥笑", value: "mocking, sarcastic smile, scoffing" },
                { label: "专注/认真", value: "focused, concentrating, sharp gaze" },
                { label: "无聊/打哈欠", value: "bored, yawning, unamused" },
                { label: "尴尬/汗颜", value: "embarrassed, awkward smile, sweatdrop" },
                { label: "撒娇/恳求", value: "pleading, puppy dog eyes, begging, upturned eyes" },
                { label: "惊慌失措", value: "panicked, flustered, frantic" },
                { label: "苦笑/无奈", value: "wry smile, forced smile, helpless" },
                { label: "贪婪/垂涎", value: "greedy, lustful, drooling" },
                { label: "释然/欣慰", value: "relieved, soft smile, gentle expression" },
                { label: "捂嘴笑", value: "covering mouth, laughing behind hand, giggling silently" },
                { label: "扁嘴撒娇", value: "pouting, duck lips, acting spoiled, cute pout" },
                { label: "鼓起脸颊 (气鼓鼓)", value: "puffed cheeks, puffing out cheeks, cute angry" },
                { label: "咬下唇", value: "biting lower lip, biting lip" },
                { label: "翻白眼", value: "rolling eyes, annoyed expression" },
                { label: "皱眉头", value: "furrowed brow, frowning, knitted brows" },
                { label: "泪眼汪汪", value: "teary eyes, eyes brimming with tears, watery eyes" },
                { label: "似笑非笑", value: "half-smile, faint smile, enigmatic expression" },
                { label: "咬牙切齿", value: "gritting teeth, clenched teeth, seething" },
                { label: "俏皮吐舌眨眼 (诶嘿)", value: "one eye closed, tongue out, winking and tongue out, tehepero" }
            ]
        },
        hairStyle: {
            label: "人物发型",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "短发", value: "short hair, short crop" },
                { label: "长直发", value: "long straight hair, flowing hair" },
                { label: "大波浪卷发", value: "long wavy hair, curly hair, big waves" },
                { label: "鲍勃头/波波头", value: "bob cut, short bob" },
                { label: "精灵短发", value: "pixie cut, very short hair" },
                { label: "寸头", value: "buzz cut, crew cut, close-cropped hair" },
                { label: "光头", value: "bald, hairless, shaved head" },
                { label: "高马尾", value: "high ponytail, single ponytail" },
                { label: "低马尾", value: "low ponytail" },
                { label: "双马尾", value: "twintails, pigtails, twin tails" },
                { label: "侧单马尾", value: "side ponytail" },
                { label: "麻花辫/单编发", value: "braided hair, plait, single braid" },
                { label: "双麻花辫", value: "twin braids, double braids" },
                { label: "丸子头/盘发", value: "hair bun, hair updo, chignon" },
                { label: "双丸子头/哪吒头", value: "double buns, space buns" },
                { label: "半扎发", value: "half up half down, half updo" },
                { label: "齐刘海", value: "blunt bangs, straight bangs, fringe" },
                { label: "中分/偏分", value: "parted hair, center parting, side parting" },
                { label: "公主切/姬发式", value: "hime cut, blunt sidelocks" },
                { label: "大背头", value: "slicked-back hair, brushed back" },
                { label: "莫霍克发型", value: "mohawk, faux hawk" },
                { label: "飞机头", value: "pompadour, quiff" },
                { label: "狼尾发型", value: "mullet, wolf cut" },
                { label: "脏辫", value: "dreadlocks, locs, braided dreads" },
                { label: "爆炸头", value: "afro, huge curly hair" },
                { label: "武士头/发髻", value: "samurai hair, topknot, chonmage" },
                { label: "不对称发型", value: "asymmetrical hair, uneven haircut" },
                { label: "凌乱发型/碎发", value: "messy hair, bed head, tousled hair" },
                { label: "钻头卷/螺旋卷", value: "drill hair, ringlets, corkscrew curls" },
                { label: "呆毛/翘发", value: "ahoge, standing hair, single hair antenna" },
                { label: "触角刘海/龙须刘海", value: "antenna hair, long bangs framing face" },
                { label: "编发王冠", value: "crown braid, braided crown" },
                { label: "挑染/挂耳染", value: "streaked hair, colored inner hair, highlights" },
                { label: "渐变发色", value: "gradient hair, ombre hair, two-tone hair" },
                { label: "朋克风格发型", value: "punk style hair, spiked hair, punk hair" },
                { label: "赛博朋克发光发型", value: "cyberpunk glowing hair, neon hair, luminescent hair" },
                { label: "火焰般头发", value: "fire-like hair, flaming hair, hair made of fire" },
                { label: "星空发型", value: "galaxy hair, starry hair, cosmos in hair" },
                { label: "水波/流体发型", value: "water-like hair, liquid hair, fluid hair" },
                { label: "失重/漂浮发型", value: "floating hair, anti-gravity hair" }
            ]
        },
        hairColor: {
            label: "人物发色",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "金色", value: "blonde hair, golden hair" },
                { label: "银白色", value: "silver-white hair, snow-white hair" },
                { label: "纯黑色", value: "jet black hair, obsidian hair" },
                { label: "棕色/栗色", value: "brown hair, chestnut hair, brunette" },
                { label: "红色", value: "red hair, crimson hair, scarlet hair" },
                { label: "铜色", value: "copper hair, auburn hair, rusty red hair" },
                { label: "奶茶色", value: "milk tea hair, light beige hair, creamy brown hair" },
                { label: "玫瑰金", value: "rose gold hair, pinkish-blonde hair" },
                { label: "亚麻灰", value: "ash blonde hair, flaxen hair" },
                { label: "奶奶灰/灰银色", value: "ash gray hair, silver-gray hair" },
                { label: "樱花粉", value: "pastel pink hair, cherry blossom pink hair" },
                { label: "薄荷绿", value: "mint green hair, pastel green hair" },
                { label: "雾霾蓝", value: "dusty blue hair, ash blue hair" },
                { label: "薰衣草紫", value: "lavender hair, pastel purple hair" },
                { label: "蜜桃橘", value: "peachy hair, pastel orange hair" },
                { label: "酒红色", value: "burgundy hair, wine red hair" },
                { label: "蓝黑色", value: "blue-black hair, midnight blue hair" },
                { label: "橄榄绿", value: "olive green hair, dark green hair" },
                { label: "宝蓝色", value: "sapphire blue hair, deep blue hair" },
                { label: "宝石色系", value: "jewel-toned hair, rich vibrant jewel hair colors" },
                { label: "火焰色渐变", value: "flame gradient hair, red to yellow ombre hair, fire-colored hair" },
                { label: "彩虹渐变色", value: "rainbow gradient hair, prism hair" },
                { label: "日落色渐变", value: "sunset gradient hair, orange to purple ombre hair" },
                { label: "粉蓝渐变 (棉花糖色)", value: "pink to blue ombre hair, cotton candy gradient" },
                { label: "黑红渐变", value: "black to red ombre hair" },
                { label: "紫银渐变", value: "purple to silver ombre hair" },
                { label: "深浅同色渐变", value: "monochromatic gradient hair, dark to light tone ombre" },
                { label: "红蓝拼色", value: "split red and blue hair, half red half blue hair" },
                { label: "黑白拼色", value: "split black and white hair, half black half white hair" },
                { label: "多色挑染", value: "multi-color highlights, colorful streaked hair" },
                { label: "隐藏染/内层染", value: "underlights, hidden dyed inner hair, inner color" },
                { label: "爆顶染 (发根异色)", value: "neon roots, contrasting dyed roots" },
                { label: "发尾挂染", value: "dip-dyed hair, colored hair tips" },
                { label: "荧光色", value: "fluorescent hair, vivid neon colors" },
                { label: "赛博朋克霓虹色", value: "cyberpunk neon hair, vivid magenta and cyan hair" },
                { label: "夜光/发光色", value: "glowing hair, luminescent hair, bioluminescent hair" },
                { label: "星空发色", value: "galaxy hair color, cosmic colored hair, starry night hair" },
                { label: "极光色", value: "aurora hair color, iridescent green and purple hair" },
                { label: "镭射/全息色彩", value: "holographic hair, iridescent hair color" },
                { label: "珍珠/贝母偏光色", value: "pearlescent hair, opalescent hair, soft glowing pastel" }
            ]
        }
    },
    // 场景设计
    scene: {
        outdoor: {
            label: "户外场景",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "雪山山顶", value: "snowy mountain peak, snow-capped summit, top of a snowy mountain" },
                { label: "雪山山脊", value: "snowy mountain ridge, traversing the snow ridge" },
                { label: "壮丽峡谷", value: "grand canyon, massive gorge, steep rocky valley" },
                { label: "悬崖边缘", value: "cliff edge, standing on a precipice, sheer drop" },
                { label: "高山草甸", value: "alpine meadow, high altitude grassland" },
                { label: "迷雾山脉", value: "misty mountains, fog-covered peaks, rolling hills in fog" },
                { label: "火山火山口", value: "volcano crater, active volcano rim, glowing lava" },
                { label: "冰川/冰洞", value: "glacier, frozen ice cave, shimmering ice cavern" },
                { label: "宁静雪原", value: "vast snowfield, silent snowy landscape, pure white snow" },
                { label: "极光冰原", value: "ice field under aurora borealis, northern lights landscape" },
                { label: "森林", value: "lush forest, deep woods, dense woodland" },
                { label: "烧毁的森林", value: "burnt forest, charred trees, scorched woodland, smoking ashes" },
                { label: "热带雨林", value: "tropical rainforest, thick jungle vegetation, vines" },
                { label: "秋季落叶林", value: "autumn forest, glowing yellow and red leaves, fall foliage" },
                { label: "幽暗沼泽", value: "gloomy swamp, murky marsh, foggy bog" },
                { label: "竹林", value: "bamboo forest, dense bamboo grove, sunlight filtering through bamboo" },
                { label: "巨树之森", value: "giant tree forest, overgrown ancient massive trees" },
                { label: "发光蘑菇林", value: "glowing mushroom forest, bioluminescent fungi" },
                { label: "海面", value: "sea surface, vast ocean, open water" },
                { label: "深海", value: "deep sea, underwater exploration, ocean floor" },
                { label: "阳光沙滩", value: "sunny tropical beach, white sand shoreline, palm trees" },
                { label: "宁静湖泊", value: "tranquil lake, mirror-like lake surface, calm waters" },
                { label: "汹涌瀑布", value: "roaring waterfall, cascading huge falls" },
                { label: "蜿蜒河流", value: "winding river, meandering stream through nature" },
                { label: "冰封湖面", value: "frozen lake, cracked ice surface" },
                { label: "浅滩/天空之镜", value: "salt flat, shallow water reflecting the sky, salar de uyuni" },
                { label: "海岸礁石", value: "rocky coastline, ocean waves crashing on dark rocks" },
                { label: "水下珊瑚礁", value: "vibrant coral reef, rich underwater ecology" },
                { label: "辽阔草原", value: "vast grassland, sweeping green plains, breezy prairie" },
                { label: "缤纷花海", value: "endless flower field, sea of colorful blooming flowers" },
                { label: "金色麦田", value: "golden wheat field, crop field in harvest season" },
                { label: "长满野草的废墟", value: "overgrown ruins, tall grass blowing in the wind" },
                { label: "浩瀚沙漠", value: "vast desert, rolling sand dunes, sahara" },
                { label: "沙漠绿洲", value: "desert oasis, palm trees and clear pool in barren desert" },
                { label: "戈壁荒野", value: "gobi desert, rocky wasteland, barren terrain" },
                { label: "末日废土", value: "post-apocalyptic wasteland, desolate devastated landscape" },
                { label: "楼顶天台", value: "rooftop terrace, building roof, looking over the cityscape" },
                { label: "露营地", value: "campsite, glowing tents under the stars, campfire setup" },
                { label: "繁华霓虹街道", value: "cyberpunk neon-lit street, crowded city street at night" },
                { label: "废弃都市街道", value: "abandoned city street, dilapidated urban buildings" },
                { label: "欧洲小镇石板路", value: "cobblestone street, historic european townscape" },
                { label: "古神庙遗迹", value: "ancient temple ruins, forgotten mystical shrine" },
                { label: "跨海大桥", value: "massive bridge over water, grand suspension bridge" },
                { label: "荒野铁轨尽头", value: "abandoned railway tracks fading into the rough distance" },
                { label: "云海之上", value: "above the clouds, sea of endless clouds, high altitude view" },
                { label: "漂浮岛屿", value: "floating island in the sky, anti-gravity landmass" },
                { label: "璀璨星空下", value: "under the starry night sky, milky way galaxy background" },
                { label: "外星地表", value: "alien planet landscape, extraterrestrial bizarre terrain" },
                { label: "水晶洞穴", value: "glowing crystal cave, magical mineral cavern" },
                { label: "魔法森林", value: "magical ethereal forest, floating light motes, fairy lights" }
            ]
        },
        indoor: {
            label: "室内场景",
            options: [
                { label: "无", value: "none" },
                { label: "随机", value: "random" },
                { label: "宜家风格客厅", value: "IKEA-style living room" },
                { label: "包豪斯风格客厅", value: "Bauhaus-style living room" },
                { label: "包豪斯风格主卧", value: "Bauhaus-style master bedroom" },
                { label: "宜家风格儿童房", value: "IKEA-style children's room" },
                { label: "健身房", value: "gym, fitness center" },
                { label: "写字楼健身房", value: "office building gym, corporate fitness room" },
                { label: "写字楼办公室", value: "office building workspace, modern office interior" },
                { label: "AI 智能科技工厂", value: "AI-powered smart factory, high-tech manufacturing plant" },
                { label: "汽车制造工厂", value: "automotive manufacturing plant, car assembly line interior" },
                { label: "室内游泳池", value: "indoor swimming pool, covered aquatic center" },
                { label: "教室", value: "classroom, educational space" },
                { label: "实验室", value: "laboratory, research lab" },
                { label: "赛博朋克实验室", value: "cyberpunk laboratory, neon-lit tech lab" },
                { label: "中世纪风格客厅", value: "medieval-style living room, gothic interior lounge" },
                { label: "木屋客厅", value: "log cabin living room, rustic wooden interior" },
                { label: "现代极简厨房", value: "modern minimalist kitchen, sleek cooking space" },
                { label: "日式榻榻米房间", value: "Japanese tatami room, traditional zen interior" },
                { label: "工业风咖啡馆", value: "industrial-style café, exposed brick coffee shop" },
                { label: "复古理发店", value: "vintage barbershop, retro hair salon interior" },
                { label: "图书馆阅览室", value: "library reading room, quiet study space" },
                { label: "豪华酒店大堂", value: "luxury hotel lobby, grand reception hall" },
                { label: "地下酒吧", value: "underground speakeasy, dimly lit cocktail lounge" },
                { label: "艺术画廊展厅", value: "art gallery exhibition hall, white cube gallery space" },
                { label: "电竞比赛场馆", value: "esports arena interior, competitive gaming venue" },
                { label: "家庭影院", value: "home theater room, private cinema setup" },
                { label: "瑜伽冥想室", value: "yoga meditation room, tranquil wellness space" },
                { label: "蒸汽朋克书房", value: "steampunk study room, brass-and-gear library" },
                { label: "未来主义餐厅", value: "futuristic restaurant interior, sci-fi dining space" },
                { label: "北欧风卧室", value: "Scandinavian-style bedroom, light and airy sleeping area" },
                { label: "复古游戏厅", value: "retro arcade room, 80s-style game parlor" },
                { label: "温室花房", value: "indoor greenhouse, botanical conservatory" },
                { label: "录音棚控制室", value: "recording studio control room, audio production booth" },
                { label: "医院手术室", value: "hospital operating room, sterile surgical suite" },
                { label: "太空舱睡眠舱", value: "space pod sleeping capsule, compact rest unit" },
                { label: "阁楼工作室", value: "attic art studio, skylight creative workspace" },
                { label: "地铁站台", value: "subway platform interior, urban transit station" },
                { label: "超市货架区", value: "supermarket aisle, grocery store interior" },
                { label: "古董钟表店", value: "antique clock shop, vintage timepiece store interior" },
                { label: "VR 体验馆", value: "VR experience center, immersive virtual reality room" },
                { label: "儿童游乐中心", value: "indoor children's play center, colorful activity zone" },
                { label: "高端珠宝店", value: "luxury jewelry boutique, elegant display showroom" },
                { label: "烘焙坊厨房", value: "artisan bakery kitchen, pastry preparation area" },
                { label: "禅意茶室", value: "zen tea room, minimalist Japanese tearoom" },
                { label: "地下停车场", value: "underground parking garage, concrete vehicle lot" },
                { label: "天文台控制室", value: "observatory control room, stargazing operations center" },
                { label: "水族馆隧道", value: "aquarium underwater tunnel, marine life viewing corridor" },
                { label: "复古电话亭", value: "vintage telephone booth, classic red phone kiosk" },
                { label: "智能家居客厅", value: "smart home living room, AI-integrated domestic space" },
                { label: "废弃仓库改造 loft", value: "converted warehouse loft, urban industrial apartment" },
                { label: "古老城堡大厅", value: "ancient castle great hall, medieval fortress interior" },
                { label: "魔法学校教室", value: "magic school classroom, mystical academy space" },
                { label: "大学图书馆自习室", value: "university library study room, quiet academic corner" },
                { label: "校园食堂", value: "campus cafeteria, student dining hall" },
                { label: "高中化学实验室", value: "high school chemistry lab, educational science lab" },
                { label: "大学宿舍房间", value: "college dormitory room, student living quarters" },
                { label: "学校礼堂", value: "school auditorium, assembly hall for events" },
                { label: "历史博物馆内的古代学校", value: "ancient school inside a history museum, historical educational exhibit" },
                { label: "城堡图书馆", value: "castle library, grand book-filled chamber" },
                { label: "骑士训练场", value: "knight training ground, castle courtyard for jousting" },
                { label: "城堡密室", value: "castle secret chamber, hidden underground vault" },
                { label: "中世纪城堡厨房", value: "medieval castle kitchen, historic cooking area" },
                { label: "城堡塔楼观景室", value: "castle tower observation room, panoramic view lookout" },
                { label: "现代艺术学院工作室", value: "modern art academy studio, contemporary creative space" },
                { label: "未来科技学校实验室", value: "future tech school laboratory, advanced research facility" }
            ]
        }
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
    name: "NakuNode.PromptEVO",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "NakuNodePromptEVO") {
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
                title.textContent = 'NakuNode Prompt Builder';
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
                const selections = {};

                // 初始化 selections
                Object.keys(PRESET_DATA).forEach(cat => {
                    selections[cat] = {};
                    Object.keys(PRESET_DATA[cat]).forEach(subcat => {
                        selections[cat][subcat] = 'none';
                    });
                });

                // 创建摄影参数区域
                contentArea.appendChild(createCategoryTitle('📷 摄影参数'));
                Object.keys(PRESET_DATA.photography).forEach(key => {
                    contentArea.appendChild(createSelectWidget('photography', key, PRESET_DATA.photography[key], (cat, subcat, value) => {
                        selections[cat][subcat] = value;
                    }));
                });

                // 创建人物设计区域
                contentArea.appendChild(createCategoryTitle('👤 人物设计'));
                Object.keys(PRESET_DATA.character).forEach(key => {
                    contentArea.appendChild(createSelectWidget('character', key, PRESET_DATA.character[key], (cat, subcat, value) => {
                        selections[cat][subcat] = value;
                    }));
                });

                // 创建场景设计区域
                contentArea.appendChild(createCategoryTitle('🌍 场景设计'));
                Object.keys(PRESET_DATA.scene).forEach(key => {
                    contentArea.appendChild(createSelectWidget('scene', key, PRESET_DATA.scene[key], (cat, subcat, value) => {
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

                    console.log("\n[NakuNode-Prompt] ╔════════════════════════════════════════════════════════╗");
                    console.log("[NakuNode-Prompt] ║     Prompt Builder - Generated Parameters              ║");
                    console.log("[NakuNode-Prompt] ╚════════════════════════════════════════════════════════╝");
                    console.log(`[NakuNode-Prompt] Full prompt string: ${generatedPrompt}`);
                    
                    // 解析并显示每个分类的参数
                    if (promptParts.length >= 1 && promptParts[0]) {
                        console.log("\n[NakuNode-Prompt] 📷 Photography Parameters:");
                        promptParts[0].split(',').forEach((item, i) => console.log(`  ${i+1}. ${item}`));
                    }
                    
                    if (promptParts.length >= 2 && promptParts[1]) {
                        console.log("\n[NakuNode-Prompt] 👤 Character Parameters:");
                        promptParts[1].split(',').forEach((item, i) => console.log(`  ${i+1}. ${item}`));
                    }
                    
                    if (promptParts.length >= 3 && promptParts[2]) {
                        console.log("\n[NakuNode-Prompt] 🌍 Scene Parameters:");
                        promptParts[2].split(',').forEach((item, i) => console.log(`  ${i+1}. ${item}`));
                    }

                    // 更新节点的 extra_prompts 输入
                    if (self.widgets) {
                        for (let i = 0; i < self.widgets.length; i++) {
                            const widget = self.widgets[i];
                            if (widget.name === "extra_prompts") {
                                widget.value = generatedPrompt;
                                console.log(`\n[NakuNode-Prompt] ✅ Saved to extra_prompts field`);
                                break;
                            }
                        }
                    }

                    // 移除弹窗
                    document.body.removeChild(overlay);

                    // 标记画布为脏，强制刷新
                    app.graph.setDirtyCanvas(true, true);

                    console.log("\n[NakuNode-Prompt] 🎉 Prompt generated and saved. Please manually execute the workflow.");
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
            const randomValue = getRandomValue(PRESET_DATA.photography[key].options);
            if (randomValue) {
                photographyParts.push(randomValue);
            }
        } else if (value !== 'none' && value !== 'random') {
            // 找到对应的输出值
            const option = PRESET_DATA.photography[key].options.find(opt => opt.value === value);
            if (option && option.value !== 'none') {
                photographyParts.push(option.value);
            }
        }
    });
    if (photographyParts.length > 0) {
        result.push(photographyParts.join(','));
    }

    // 处理人物设计
    const characterParts = [];
    Object.keys(selections.character).forEach(key => {
        const value = selections.character[key];
        if (value === 'random') {
            const randomValue = getRandomValue(PRESET_DATA.character[key].options);
            if (randomValue) {
                characterParts.push(randomValue);
            }
        } else if (value !== 'none' && value !== 'random') {
            const option = PRESET_DATA.character[key].options.find(opt => opt.value === value);
            if (option && option.value !== 'none') {
                characterParts.push(option.value);
            }
        }
    });
    if (characterParts.length > 0) {
        result.push(characterParts.join(','));
    }

    // 处理场景设计
    const sceneParts = [];
    Object.keys(selections.scene).forEach(key => {
        const value = selections.scene[key];
        if (value === 'random') {
            const randomValue = getRandomValue(PRESET_DATA.scene[key].options);
            if (randomValue) {
                sceneParts.push(randomValue);
            }
        } else if (value !== 'none' && value !== 'random') {
            const option = PRESET_DATA.scene[key].options.find(opt => opt.value === value);
            if (option && option.value !== 'none') {
                sceneParts.push(option.value);
            }
        }
    });
    if (sceneParts.length > 0) {
        result.push(sceneParts.join(','));
    }

    return result;
}
