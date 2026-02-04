# -*- coding: utf-8 -*-
import random
import json
import time
import io
import base64

# 尝试导入必要的库，如果失败则在调用时抛出更友好的错误
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from zhipuai import ZhipuAiClient
except ImportError:
    ZhipuAiClient = None


# 从 NAKUNode_Flux_QwenEdit_Prompt.py 复制的人物参数数据
NATIONALITY_PRESETS = {
    "-- 无 --": "", "中国": "Chinese", "美国": "American", "日本": "Japanese", "英国": "British", "法国": "French", "德国": "German", "意大利": "Italian", "俄罗斯": "Russian", "加拿大": "Canadian", "澳大利亚": "Australian", "印度": "Indian", "巴西": "Brazilian", "韩国": "Korean", "西班牙": "Spanish", "墨西哥": "Mexican", "印度尼西亚": "Indonesian", "巴基斯坦": "Pakistani", "尼日利亚": "Nigerian", "孟加拉国": "Bangladeshi", "埃及": "Egyptian", "越南": "Vietnamese", "土耳其": "Turkish", "伊朗": "Iranian", "泰国": "Thai", "南非": "South African", "阿根廷": "Argentinian", "波兰": "Polish", "乌克兰": "Ukrainian", "沙特阿拉伯": "Saudi Arabian", "荷兰": "Dutch", "瑞典": "Swedish", "瑞士": "Swiss", "比利时": "Belgian", "奥地利": "Austrian", "希腊": "Greek", "葡萄牙": "Portuguese", "挪威": "Norwegian", "丹麦": "Danish", "芬兰": "Finnish", "爱尔兰": "Irish", "新西兰": "New Zealander", "新加坡": "Singaporean", "马来西亚": "Malaysian", "菲律宾": "Filipino", "以色列": "Israeli", "阿联酋": "Emirati", "哥伦比亚": "Colombian", "智利": "Chilean", "秘鲁": "Peruvian", "委内瑞拉": "Venezuelan", "罗马尼亚": "Romanian", "捷克": "Czech", "匈加利": "Hungarian", "哈萨克斯坦": "Kazakhstani", "乌兹别克斯坦": "Uzbek", "白俄罗斯": "Belarusian", "阿塞拜疆": "Azerbaijani", "格鲁吉亚": "Georgian", "亚美尼亚": "Armenian", "摩洛哥": "Moroccan", "阿尔及利亚": "Algerian", "突尼斯": "Tunisian", "利比亚": "Libyan", "苏丹": "Sudanese", "埃塞オ比亚": "Ethiopian", "肯尼亚": "Kenyan", "坦桑尼亚": "Tanzanian", "乌干达": "Ugandan", "加纳": "Ghanaian", "科特迪瓦": "Ivorian", "喀麦隆": "Cameroonian", "塞内加尔": "Senegalese", "津巴布韦": "Zimbabwean", "安哥拉": "Angolan", "莫桑比克": "Mozambican", "赞比亚": "Zambian", "伊拉克": "Iraqi", "叙利亚": "Syrian", "约旦": "Jordanian", "黎巴嫩": "Lebanese", "也门": "Yemeni", "阿曼": "Omani", "卡塔尔": "Qatari", "科威特": "Kuwaiti", "巴林": "Bahraini", "阿富汗": "Afghan", "尼泊尔": "Nepalese", "斯里兰卡": "Sri Lankan", "缅甸": "Burmese", "柬埔寨": "Cambodian", "老挝": "Laotian", "蒙古": "Mongolian", "朝鲜": "North Korean", "古巴": "Cuban", "海地": "Haitian", "多米尼加": "Dominican", "牙买加": "Jamaican", "危地马拉": "Guatemalan", "洪都拉斯": "Honduran", "萨尔瓦多": "Salvadoran", "尼加拉瓜": "Nicaraguan", "哥斯达黎加": "Costa Rican", "巴拿马": "Panamanian", "厄瓜多尔": "Ecuadorian", "玻利维亚": "Bolivian", "巴拉圭": "Paraguayan", "乌拉圭": "Uruguayan", "冰岛": "Icelandic", "卢森堡": "Luxembourgish", "马耳他": "Maltese", "塞浦路斯": "Cypriot", "立陶宛": "Lithuanian", "拉脱维亚": "Latvian", "爱沙尼亚": "Estonian", "斯洛文尼亚": "Slovenian", "斯洛伐克": "Slovak", "克罗地亚": "Croatian", "波斯尼亚和黑塞哥维那": "Bosnian", "塞尔维亚": "Serbian", "黑山": "Montenegrin", "北马其顿": "North Macedonian", "阿尔巴尼亚": "Albanian", "科索沃": "Kosovan", "摩尔多瓦": "Moldovan", "梵蒂冈": "Vatican", "圣马力诺": "Sammarinese", "摩纳哥": "Monacan", "安道尔": "Andorran", "列支敦士登": "Liechtensteiner",
}
GENDER_PRESETS = {
    "-- 无 --": "", "男性": "male", "女性": "female", "男孩": "boy", "女孩": "girl", "男人": "man", "女人": "woman", "英俊的男人": "handsome man", "美丽的女人": "beautiful woman", "年长的男人": "old man", "年长的女人": "old woman", "年轻的男人": "young man", "年轻的女人": "young woman", "雄壮的男人": "masculine man", "娇柔的女人": "feminine woman", "中性外貌": "androgynous person", "非二元性别者": "non-binary person", "跨性别男性": "transgender man", "跨性别女性": "transgender woman", "国王": "king", "女王": "queen", "王子": "prince", "公主": "princess", "男战士": "male warrior", "女战士": "female warrior", "男巫师": "male wizard", "女巫师": "female witch", "男刺客": "male assassin", "女刺客": "female assassin", "男商人": "male merchant", "女商人": "female merchant", "男农民": "male peasant", "女农民": "female peasant", "男贵族": "male noble", "女贵族": "female noble", "男士兵": "male soldier", "女士兵": "female soldier", "男飞行员": "male pilot", "女飞行员": "female pilot", "男宇航员": "male astronaut", "女宇航员": "female astronaut", "男侦探": "male detective", "女侦探": "female detective", "男医生": "male doctor", "女医生": "female doctor", "男科学家": "male scientist", "女科学家": "female scientist", "男艺术家": "male artist", "女艺术家": "female artist", "男音乐家": "male musician", "女音乐家": "female musician", "男运动员": "male athlete", "女运动员": "female athlete", "男演员": "actor", "女演员": "actress", "男模特": "male model", "女模特": "female model", "男英雄": "hero", "女英雄": "heroine", "男反派": "male villain", "女反派": "female villain", "男神": "god", "女神": "goddess", "男恶魔": "male demon", "女恶魔": "succubus", "男天使": "male angel", "女天使": "female angel", "男精灵": "male elf", "女精灵": "female elf", "男矮人": "male dwarf", "女矮人": "female dwarf", "男兽人": "male orc", "女兽人": "female orc", "男吸血鬼": "male vampire", "女吸血鬼": "female vampire", "男狼人": "male werewolf", "女狼人": "female werewolf", "机器人(男)": "male robot, android", "机器人(女)": "female robot, gynoid", "半机械人(男)": "male cyborg", "半机械人(女)": "female cyborg", "父亲": "father", "母亲": "mother", "儿子": "son", "女儿": "daughter", "兄弟": "brother", "姐妹": "sister", "祖父": "grandfather", "祖母": "grandmother", "丈夫": "husband", "妻子": "wife", "男朋友": "boyfriend", "女朋友": "girlfriend", "绅士": "gentleman", "淑女": "lady", "男主角": "male protagonist", "女主角": "female protagonist", "男舞者": "male dancer", "女舞者": "female dancer", "男学生": "male student", "女学生": "female student", "男教师": "male teacher", "女教师": "female teacher", "男警察": "policeman", "女警察": "policewoman",
}
AGE_PRESETS = {
    "-- 无 --": "", "婴儿": "baby, 1 year old", "幼儿": "toddler, 3 years old", "儿童": "child, 7 years old", "少年": "preteen, 12 years old", "青少年": "teenager, 16 years old", "青年": "young adult, 20 years old", "成年人": "adult, 30 years old", "中年人": "middle-aged, 45 years old", "老年人": "elderly, 65 years old", "高龄老人": "very old, 80 years old", "百岁老人": "centenarian, 100 years old", "古代的": "ancient, timeless", "永恒的": "ageless, eternal", "20多岁": "in their 20s", "30多岁": "in their 30s", "40多岁": "in their 40s", "50多岁": "in their 50s", "60多岁": "in their 60s", "70多岁": "in their 70s", "80多岁": "in their 80s", "90多岁": "in their 90s", "5岁": "5 years old", "10岁": "10 years old", "15岁": "15 years old", "18岁": "18 years old", "25岁": "25 years old", "35岁": "35 years old", "50岁": "50 years old", "75岁": "75 years old", "新生的": "newborn", "学龄前儿童": "preschooler", "小学生": "elementary school student", "初中生": "middle school student", "高中生": "high school student", "大学生": "college student", "研究生": "graduate student", "职场新人": "young professional", "经验丰富": "experienced professional", "退休人员": "retired", "成熟的": "mature", "风化的": "weathered", "饱经风霜的": "wizened", "年轻的": "youthful", "孩子气的": "childish", "幼稚的": "puerile", "青涩的": "adolescent", "风华正茂": "in their prime", "中年危机": "mid-life crisis age", "黄金岁月": "golden years", "史前的": "prehistoric", "石器时代": "stone age", "青铜时代": "bronze age", "铁器时代": "iron age", "古典时代": "classical antiquity", "中世纪": "medieval era", "文艺复兴时期": "Renaissance era", "巴洛克时期": "Baroque era", "启蒙时代": "Age of Enlightenment", "维多利亚时代": "Victorian era", "爱德华时代": "Edwardian era", "咆哮的二十年代": "Roaring Twenties", "大萧条时期": "Great Depression era", "二战时期": "World War II era", "冷战时期": "Cold War era", "原子时代": "Atomic Age", "太空时代": "Space Age", "信息时代": "Information Age", "未来主义": "futuristic", "赛博朋克时代": "cyberpunk era", "蒸汽朋克时代": "steampunk era", "后启示录时代": "post-apocalyptic era", "神话时代": "mythological age", "传说时代": "legendary age", "时间旅行者": "time traveler", "不朽者": "immortal", "短暂的": "ephemeral", "初生牛犊": "fledgling", "经验老道": "veteran", "新手": "novice", "专家": "expert", "大师": "master", "学徒": "apprentice", "长者": "elder", "祖先": "ancestor", "后代": "descendant", "看起来比实际年龄大": "looks older than their age", "看起来比实际年龄小": "looks younger than their age", "年龄不详": "ageless appearance", "时间扭曲": "time-warped", "永葆青春": "eternally young", "迅速老化": "rapidly aging",
}
BODY_TYPE_PRESETS = {
    "-- 无 --": "", "高个子": "tall", "矮个子": "short", "中等身高": "average height", "非常高": "very tall, giant", "非常矮": "very short, tiny", "苗条": "slim", "瘦": "thin, skinny", "骨感": "bony, skeletal", "丰满": "curvy, voluptuous", "胖": "fat, plump", "肥胖": "obese", "肌肉发达": "muscular, athletic", "健美": "bodybuilder physique", "强壮": "strong, powerful build", "纤弱": "delicate, frail", "柔软": "soft body", "硬朗": "wiry, tough", "匀称": "well-proportioned", "梨形身材": "pear-shaped body", "苹果形身材": "apple-shaped body", "沙漏身材": "hourglass figure", "矩形身材": "rectangle body shape", "倒三角形身材": "inverted triangle body shape", "运动员身材": "athletic build", "舞者身材": "dancer's body", "模特身材": "model's slender body", "超重": "overweight", "体重不足": "underweight", "魁梧": "burly, stocky", "矮胖": "short and stout", "高瘦": "tall and lanky", "优雅": "graceful body", "笨拙": "clumsy body", "灵活": "flexible, agile", "僵硬": "stiff, rigid", "宽肩": "broad shoulders", "窄肩": "narrow shoulders", "长腿": "long legs", "短腿": "short legs", "长臂": "long arms", "短臂": "short arms", "大肚子": "large belly", "平坦的小腹": "flat stomach", "六块腹肌": "six-pack abs", "丰臀": "large buttocks", "平臀": "flat buttocks", "大胸": "large chest/breasts", "平胸": "small chest/breasts", "粗腰": "thick waist", "细腰": "thin waist", "粗脖子": "thick neck", "长脖子": "long neck", "大手": "large hands", "小手": "small hands", "大脚": "large feet", "小脚": "small feet", "有疤痕的身体": "scarred body", "有纹身的身体": "tattooed body", "有穿环的身体": "pierced body", "晒黑的身体": "tanned body", "苍白的身体": "pale body", "多毛的身体": "hairy body", "光滑的身体": "smooth body", "机器人身体": "robotic body", "半机械身体": "cybernetic body", "兽人身体": "orcish body", "精灵身体": "elfin body", "矮人身体": "dwarven body", "巨人身体": "giant's body", "神一般的身体": "god-like physique", "恶魔般的身体": "demonic physique", "天使般的身体": "angelic physique", "幽灵般的身体": "ethereal, ghostly body", "变形的身体": "mutated body", "非人形态": "non-humanoid body shape", "植物形态": "plant-like body", "昆虫形态": "insectoid body", "爬行动物形态": "reptilian body", "水生形态": "aquatic body", "鸟类形态": "avian body", "能量体": "body made of energy", "火焰体": "body made of fire", "液体体": "body made of liquid", "烟雾体": "body made of smoke", "水晶体": "body made of crystal", "石头体": "body made of stone", "木头体": "body made of wood", "金属体": "body made of metal", "影子体": "body made of shadow", "卡通身材": "cartoon proportions", "动漫身材": "anime proportions", "写实身材": "realistic proportions", "病态的": "sickly, emaciated", "健康的": "healthy, fit", "怀孕的": "pregnant",
}
CLOTHING_PRESETS = {
    "-- 无 --": "", "T恤和牛仔裤": "T-shirt and jeans", "西装": "business suit", "连衣裙": "dress", "婚纱": "wedding gown", "晚礼服": "evening gown", "燕尾服": "tuxedo", "校服": "school uniform", "运动服": "tracksuit, sportswear", "泳衣": "swimsuit", "比基尼": "bikini", "睡衣": "pajamas", "浴袍": "bathrobe", "风衣": "trench coat", "皮夹克": "leather jacket", "羽绒服": "down jacket", "毛衣": "sweater", "连帽衫": "hoodie", "衬衫": "shirt", "短裤": "shorts", "裙子": "skirt", "长袍": "robe", "斗篷": "cape, cloak", "盔甲": "suit of armor", "宇航服": "spacesuit", "潜水服": "diving suit", "消防服": "firefighter uniform", "警服": "police uniform", "军装": "military uniform", "医生白大褂": "doctor's white coat", "护士服": "nurse's uniform", "厨师服": "chef's uniform", "和服": "kimono", "韩服": "hanbok", "旗袍": "qipao, cheongsam", "汉服": "hanfu", "纱丽": "sari", "苏格兰裙": "kilt", "皮裤": "leather pants", "实验服": "lab coat", "工作服": "overalls, coveralls", "牧师长袍": "priest's vestments", "修女服": "nun's habit", "国王的衣服": "king's royal attire", "女王的衣服": "queen's royal attire", "公主裙": "princess dress", "小丑服装": "clown costume", "海盗服装": "pirate costume", "忍者服": "ninja suit", "武士盔甲": "samurai armor", "维京服装": "viking attire", "古罗马服装": "ancient Roman toga", "古希腊服装": "ancient Greek chiton", "古埃及服装": "ancient Egyptian clothing", "中世纪服装": "medieval clothing", "文艺复兴服装": "Renaissance attire", "维多利亚时代服装": "Victorian era dress", "爱德华时代服装": "Edwardian era fashion", "20年代风格服装": "1920s flapper dress", "50年代风格服装": "1950s rockabilly style", "嬉皮士风格服装": "1960s hippie clothing", "70年代迪斯科服装": "1970s disco fashion", "80年代朋克服装": "1980s punk fashion", "90年代垃圾摇滚服装": "1990s grunge style", "蒸汽朋克服装": "steampunk attire", "赛博朋克服装": "cyberpunk clothing, with neon lights", "柴油朋克服装": "dieselpunk clothing", "太阳朋克服装": "solarpunk clothing", "哥特服装": "gothic fashion", "洛丽塔服装": "Lolita fashion", "奇幻冒险者服装": "fantasy adventurer gear", "法师长袍": "mage robe", "盗贼皮甲": "rogue's leather armor", "圣骑士板甲": "paladin's plate armor", "德鲁伊服装": "druid's natural clothing", "未来派服装": "futuristic clothing", "外星服装": "alien attire", "能量护甲": "energy armor", "动力装甲": "power armor", "生化服装": "bio-mechanical suit", "由植物制成的衣服": "clothing made of leaves and vines", "由火焰制成的衣服": "clothing made of fire", "由水制成的衣服": "clothing made of water", "由光制成的衣服": "clothing made of light", "由影子制成的衣服": "clothing made of shadows", "由水晶制成的衣服": "clothing made of crystal", "破烂的衣服": "tattered, ragged clothes", "干净整洁的衣服": "clean and neat clothes", "奢华的衣服": "luxurious, extravagant clothes", "朴素的衣服": "simple, plain clothes", "正式服装": "formal wear", "休闲服装": "casual wear", "商务休闲装": "business casual", "庆典服装": "ceremonial robes", "传统民族服装": "traditional ethnic costume", "舞会礼服": "ball gown", "迷你裙": "miniskirt", "连身裤": "jumpsuit", "雨衣": "raincoat", "滑雪服": "ski suit", "防化服": "hazmat suit", "隐形衣": "invisibility cloak",
}
HAIR_STYLES = {
    "-- 无 --": "", "长直发": "long straight hair", "大波浪卷发": "wavy long hair", "短发": "short hair", "寸头": "buzz cut", "丸子头": "bun hairstyle", "高马尾": "high ponytail", "双马尾": "twin tails", "脏辫": "dreadlocks", "编发": "braided hair", "莫霍克发型": "mohawk hairstyle", "赛博朋克发光发型": "cyberpunk glowing hair", "湿发": "wet hair", "爆炸头": "afro hairstyle", "地中海发型": "bald top with hair on sides", "完全光头": "completely bald", "复古波波头": "vintage bob cut", "凌乱的短发": "messy short hair", "油头": "slicked-back hair", "火焰般的头发": "flaming hair", "水晶般的头发": "crystal hair", "星云般的头发": "nebula pattern hair", "瀑布般的长发": "waterfall of long hair", "及腰长发": "waist-length hair", "及肩中发": "shoulder-length hair", "精灵短发": "pixie cut", "不对称发型": "asymmetrical haircut", "碗盖头": "bowl cut", "鲻鱼头": "mullet hairstyle", "离子烫": "chemically straightened hair", "玉米烫": "cornrows", "法式编发": "french braid", "鱼骨辫": "fishtail braid", "荷兰辫": "dutch braid", "皇冠编发": "crown braid", "武士头": "samurai topknot", "维京风格发型": "viking style hair with braids and beads", "哥特风格发型": "gothic style hair, long and black", "朋克风格发型": "punk style spiky hair", "摇滚风格发型": "rockabilly pompadour", "波西米亚风发型": "bohemian style with waves and flowers", "未来感发型": "futuristic geometric haircut", "反重力头发": "anti-gravity hair, floating upwards", "液体头发": "liquid-like hair", "金属丝头发": "hair made of metallic wires", "玻璃纤维头发": "hair made of glass fibers", "植物藤蔓头发": "hair made of vines and leaves", "触手头发": "tentacle hair", "羽毛头发": "hair made of feathers", "云朵头发": "hair made of clouds", "烟雾头发": "hair made of smoke", "影子头发": "hair made of shadows", "像素化头发": "pixelated hair", "几何形状头发": "geometric shaped hair", "发光的头发": "glowing hair", "半透明头发": "translucent hair", "彩虹色头发": "rainbow colored hair", "双色头发": "half and half colored hair", "隐藏染发": "hidden rainbow hair", "头巾": "wearing a headscarf", "兜帽": "wearing a hood", "帽子": "wearing a hat", "发带": "wearing a headband", "发夹": "hair clips", "蝴蝶结": "hair bow", "皇冠": "wearing a crown", "花环": "wearing a flower wreath", "头盔": "wearing a helmet", "风中凌乱的头发": "windblown hair", "水下漂浮的头发": "hair floating underwater", "刚睡醒的头发": "bedhead hair", "精心打理的头发": "perfectly coiffed hair", "油腻的头发": "greasy hair", "干燥的头发": "dry, frizzy hair", "有头皮屑": "dandruff in hair", "头发稀疏": "thinning hair", "头发浓密": "thick, voluminous hair", "有刘海": "bangs / fringe", "斜刘海": "side-swept bangs", "齐刘海": "blunt bangs", "空气刘海": "see-through bangs", "窗帘式刘海": "curtain bangs", "无刘海": "no bangs, forehead exposed", "美人尖": "widow's peak hairline", "发际线高": "receding hairline", "发际线低": "low hairline", "鬓角": "sideburns", "剃掉一侧的头发": "shaved side haircut", "头皮纹身": "scalp tattoo", "头发上有珠子": "beads in hair", "头发上有闪粉": "glitter in hair", "头发上有树叶": "leaves in hair", "头发上有雪花": "snowflakes in hair",
}
HAIR_COLORS = {
    "-- 无 --": "", "黑色": "black hair", "金色": "blonde hair", "棕色": "brown hair", "红色": "red hair", "白色": "white hair", "银色": "silver hair", "粉色": "pink hair", "蓝色": "blue hair", "绿色": "green hair", "彩虹色": "rainbow hair", "渐变发色": "gradient hair", "挑染": "highlighted hair", "白金色": "platinum blonde hair", "姜黄色": "ginger hair", "深紫色": "deep purple hair", "霓虹绿色": "neon green hair", "双色拼接": "split-dyed hair (half black, half white)", "星空色": "galaxy-colored hair", "自然黑": "natural black hair", "深棕色": "dark brown hair", "巧克力棕": "chocolate brown hair", "浅棕色": "light brown hair", "焦糖色": "caramel brown hair", "灰金色": "ash blonde hair", "草莓金": "strawberry blonde hair", "蜂蜜金": "honey blonde hair", "酒红色": "burgundy red hair", "铜红色": "copper red hair", "樱桃红": "cherry red hair", "亮红色": "bright red hair", "灰色": "gray hair", "钢灰色": "steel gray hair", "木炭色": "charcoal gray hair", "淡紫色": "lavender purple hair", "紫罗兰色": "violet purple hair", "天蓝色": "sky blue hair", "宝蓝色": "royal blue hair", "海军蓝": "navy blue hair", "薄荷绿": "mint green hair", "森林绿": "forest green hair", "橄榄绿": "olive green hair", "酸 lime绿": "lime green hair", "橙色": "orange hair", "桃色": "peach hair", "黄色": "yellow hair", "青色": "cyan hair", "品红色": "magenta hair", "蒂芙尼蓝": "tiffany blue hair", "玫瑰金": "rose gold hair", "多色挑染": "multi-color streaks", "隐藏彩虹染": "hidden rainbow highlights", "裙摆染": "dip-dyed hair", "发根补染": "grown-out roots", "荧光色": "fluorescent hair", "磷光色": "phosphorescent hair", "全息色": "holographic hair", "金属色": "metallic hair", "铬色": "chrome hair", "铜色": "copper hair", "青铜色": "bronze hair", "褪色效果": "faded color effect", "柔和的粉彩色": "soft pastel hair", "鲜艳的霓虹色": "vivid neon hair", "深色系": "dark color scheme hair", "浅色系": "light color scheme hair", "大地色系": "earth-toned hair", "宝石色系": "jewel-toned hair", "火焰色渐变": "fire-colored gradient hair", "海洋色渐变": "ocean-colored gradient hair", "日落色渐变": "sunset-colored gradient hair", "极光色": "aurora-colored hair", "宇宙尘埃色": "cosmic dust colored hair", "大理石纹染发": "marbled hair color", "豹纹染发": "leopard print hair color", "斑马纹染发": "zebra print hair color", "像素化染发": "pixelated hair color", "故障艺术染发": "glitch effect hair color", "木纹色": "wood grain colored hair", "石纹色": "stone-like colored hair", "水晶色": "crystal-colored hair", "烟熏色": "smoky colored hair", "半透明色": "translucent colored hair", "变色龙色": "chameleon color-changing hair", "热感应变色": "heat-reactive color-changing hair", "紫外光下变色": "UV-reactive hair color", "单色": "monochromatic hair", "双色": "dichromatic hair", "三色": "trichromatic hair", "四色": "tetrachromatic hair", "五彩斑斓": "polychromatic hair", "不饱和色": "desaturated hair color", "高饱和色": "highly saturated hair color", "自然发色": "natural hair color", "非自然发色": "unnatural hair color",
}
EXPRESSIONS = {
    "-- 无 --": "", "微笑": "smiling", "大笑": "laughing", "哭泣": "crying", "愤怒": "angry", "悲伤": "sad", "惊讶": "surprised", "恐惧": "scared", "厌恶": "disgusted", "沉思": "pensive", "困惑": "confused", "喜悦": "joyful", "平静": "calm", "顽皮的": "playful", "严肃的": "serious", "傲慢的": "arrogant", "害羞的": "shy", "轻蔑的": "contemptuous", "渴望的": "longing", "痛苦的": "pained", "得意的": "smug", "醉酒的": "drunk", "疯狂的": "insane", "狂喜的": "ecstatic", "面无表情": "expressionless", "幸灾乐祸": "gloating", "嫉妒": "jealous", "怀疑": "skeptical", "好奇": "curious", "敬畏": "in awe", "尴尬": "embarrassed", "内疚": "guilty", "满足": "content", "放松": "relaxed", "疲惫": "exhausted", "无聊": "bored", "紧张": "nervous", "焦虑": "anxious", "充满希望": "hopeful", "绝望": "despairing", "勇敢": "brave", "胆怯": "timid", "专注": "focused", "心烦意乱": "distracted", "深情": "affectionate", "冷漠": "indifferent", "敌对": "hostile", "和蔼可亲": "amiable", "闷闷不乐": "sullen", "兴高采烈": "elated", "沮丧": "dejected", "沾沾自喜": "complacent", "挑衅": "defiant", "顺从": "submissive", "狡猾": "sly", "天真": "naive", "愤世嫉俗": "cynical", "乐观": "optimistic", "悲观": "pessimistic", "歇斯底里": "hysterical", "庄严": "solemn", "沉着": "composed", "激动": "agitated", "恼怒": "annoyed", "狂怒": "enraged", "惊恐": "terrified", "震惊": "shocked", "着迷": "mesmerized", "失望": "disappointed", "宽慰": "relieved", "自豪": "proud", "谦逊": "humble", "顽固": "stubborn", "优柔寡断": "indecisive", "果断": "decisive", "热情": "enthusiastic", "冷淡": "apathetic", "冥想中": "meditative", "做鬼脸": "making a face", "傻笑": "giggling", "假笑": "smirking", "抽泣": "sobbing", "呻吟": "groaning", "叹气": "sighing", "打哈欠": "yawning", "打喷嚏": "sneezing", "咳嗽": "coughing", "喘气": "gasping", "屏住呼吸": "holding breath", "咬紧牙关": "gritting teeth", "舔嘴唇": "licking lips", "皱眉": "frowning", "扬眉": "raising eyebrows", "眯眼": "squinting", "瞪眼": "glaring",
}

# 从 NAKUNode_Flux_QwenEdit_Prompt.py 复制的摄影参数数据
CAMERA_ANGLES = {
    "-- 无 --": "", "正面视角": "front view", "侧面视角": "profile view", "45度角": "three-quarters view", "背面视角": "back view", "高角度/俯视": "high-angle shot, bird's-eye view", "低角度/仰视": "low-angle shot, worm's-eye view", "荷兰角/倾斜": "dutch angle, tilted shot", "过肩视角": "over-the-shoulder shot", "主观视角(POV)": "point-of-view shot (POV)", "地面视角": "ground-level shot", "航拍视角": "aerial shot", "特写": "extreme close-up", "大特写": "close-up shot", "中景": "medium shot", "全景": "full shot, long shot", "远景": "extreme long shot", "牛仔镜": "cowboy shot (mid-thigh up)", "双人镜头": "two-shot", "三人镜头": "three-shot", "群像镜头": "group shot", "建立镜头": "establishing shot", "反应镜头": "reaction shot", "插入镜头": "insert shot", "推镜头": "push-in shot", "拉镜头": "pull-out shot", "摇镜头(水平)": "pan shot", "移镜头(垂直)": "tilt shot", "跟拍镜头": "tracking shot", "弧形跟拍": "arc shot", "起重机镜头": "crane shot", "无人机镜头": "drone shot", "手持摄影机": "handheld camera shot", "斯坦尼康": "steadicam shot", "固定镜头": "static shot", "变焦镜头": "zoom shot", "快速变焦": "crash zoom", "慢速变焦": "slow zoom", "眩晕变焦": "dolly zoom, vertigo effect", "窥视视角": "voyeuristic shot", "反射镜头": "reflection shot (in a mirror or water)", "剪影镜头": "silhouette shot", "框架中的框架": "frame within a frame", "对称视角": "symmetrical shot", "不对称视角": "asymmetrical shot", "黄金比例视角": "golden ratio shot", "引导线视角": "leading lines shot", "对角线视角": "diagonal shot", "三角形视角": "triangular composition shot", "圆形视角": "circular composition shot", "S形曲线视角": "S-curve composition shot", "负空间视角": "negative space shot", "填充画面视角": "fill the frame shot", "极简主义视角": "minimalist shot", "巴洛克风格视角": "baroque, cluttered shot", "纪实风格视角": "documentary style shot", "电影风格视角": "cinematic shot", "广告风格视角": "commercial style shot", "音乐视频风格": "music video style shot", "游戏视角": "video game perspective (first-person)", "第三人称游戏视角": "video game perspective (third-person)", "等距视角": "isometric view", "顶视图": "top-down view", "剖面图": "cross-section view", "展开图": "exploded view", "全景图": "panorama shot", "360度视角": "360-degree view", "红外视角": "infrared view", "热成像视角": "thermal view", "X光视角": "X-ray view", "夜视视角": "night vision view", "鱼眼视角": "fisheye view", "微距视角": "macro view", "长曝光视角": "long exposure shot", "多重曝光视角": "multiple exposure shot", "光绘视角": "light painting shot", "移轴摄影视角": "tilt-shift shot", "针孔相机视角": "pinhole camera view", "湿版火棉胶视角": "wet-plate collodion view", "宝丽来视角": "Polaroid view", "Lomo视角": "Lomography view", "CCTV视角": "CCTV view", "仪表盘摄像头视角": "dashcam view", "身体摄像头视角": "bodycam view", "无人机竞速视角": "FPV drone view", "卫星视角": "satellite view", "望远镜视角": "telescope view", "显微镜视角": "microscope view", "潜望镜视角": "periscope view", "门镜视角": "peephole view", "低保真视角": "lo-fi aesthetic shot", "高保真视角": "hi-fi aesthetic shot", "故障艺术视角": "glitch art shot",
}
LENS_AND_APERTURE = {
    "-- 无 --": "", "广角镜头": "wide-angle lens", "长焦镜头": "telephoto lens", "鱼眼镜头": "fisheye lens", "微距镜头": "macro lens", "大光圈(背景虚化)": "wide aperture, f/1.8, shallow depth of field, bokeh background", "小光圈(前后景清晰)": "narrow aperture, f/16, deep depth of field", "移轴镜头": "tilt-shift lens, miniature faking", "变形宽荧幕镜头": "anamorphic lens", "柔焦镜头": "soft-focus lens", "红外镜头": "infrared lens", "热成像镜头": "thermal imaging lens", "针孔相机效果": "pinhole camera effect", "标准镜头(50mm)": "standard 50mm lens", "超广角镜头(14mm)": "ultra-wide angle 14mm lens", "肖像镜头(85mm)": "portrait 85mm lens", "超级长焦(600mm)": "super-telephoto 600mm lens", "中等光圈(f/5.6)": "medium aperture, f/5.6", "极大光圈(f/0.95)": "extremely wide aperture, f/0.95", "极小光圈(f/32)": "extremely narrow aperture, f/32", "圆形光斑": "circular bokeh", "六边形光斑": "hexagonal bokeh", "旋涡光斑": "swirly bokeh", "甜甜圈光斑": "donut bokeh (from mirror lens)", "镜头光晕": "lens flare", "星芒效果": "sunstar effect", "色差": "chromatic aberration", "暗角": "vignetting", "桶形失真": "barrel distortion", "枕形失真": "pincushion distortion", "无畸变镜头": "rectilinear lens", "电影镜头": "cinema lens", "老式镜头": "vintage lens", "现代镜头": "modern, sharp lens", "塑料玩具镜头": "plastic toy camera lens", "DIY镜头": "DIY, handmade lens", "液体镜头": "liquid lens", "变焦镜头(广角到长焦)": "zoom lens (wide to telephoto)", "定焦镜头": "prime lens", "增距镜": "teleconverter attached", "减焦镜": "focal reducer attached", "偏振镜(CPL)": "circular polarizer filter (CPL)", "中性密度镜(ND)": "neutral density filter (ND)", "渐变中灰镜(GND)": "graduated neutral density filter (GND)", "紫外线滤镜(UV)": "UV filter", "星光镜": "star filter", "柔光镜": "diffusion filter, mist filter", "彩色滤镜(红)": "red color filter", "彩色滤镜(蓝)": "blue color filter", "彩色滤镜(绿)": "green color filter", "彩色滤镜(黄)": "yellow color filter", "万花筒滤镜": "kaleidoscope filter", "棱镜滤镜": "prism filter", "红外滤镜": "infrared filter (IR)", "水下滤镜": "underwater color correction filter", "防雾涂层": "anti-fog coating", "防水涂层": "hydrophobic coating", "多层镀膜": "multi-coated lens", "单层镀膜": "single-coated lens", "无镀膜镜头": "uncoated lens", "手动对焦": "manual focus", "自动对焦": "autofocus", "失焦/模糊": "out of focus, blurry", "选择性对焦": "selective focus", "无限远对焦": "focused at infinity", "超焦距": "hyperfocal distance", "对焦堆栈": "focus stacking", "呼吸效应": "focus breathing effect", "前散景": "foreground bokeh", "后散景": "background bokeh", "高光溢出": "blooming highlights", "清晰锐利": "tack sharp", "柔和细腻": "soft and gentle rendering", "高对比度": "high contrast rendering", "低对比度": "low contrast rendering", "3D立体效果": "3D stereoscopic effect", "VR180镜头": "VR180 lens", "镜头眩光": "lens ghosting", "耀斑": "flare", "彗形像差": "coma aberration", "像散": "astigmatism", "场曲": "field curvature", "球面像差": "spherical aberration", "衍射极限": "diffraction limited", "数字变焦": "digital zoom", "光学变焦": "optical zoom", "防抖开": "image stabilization on", "防抖关": "image stabilization off", "光圈优先模式": "aperture priority mode", "快门优先模式": "shutter priority mode", "手动模式": "manual mode", "程序自动": "program auto mode", "B门/长曝光": "bulb mode", "T门": "time mode",
}
FILM_TYPES = {
    "-- 无 --": "", "柯达Portra 400": "shot on Kodak Portra 400, fine grain, warm tones", "富士Provia 100F": "shot on Fuji Provia 100F, vibrant colors, high saturation", "伊尔福HP5": "shot on Ilford HP5, classic black and white, high contrast", "宝丽来": "Polaroid photo, instant film, retro look", "电影胶片": "cinematic film still, anamorphic", "褪色胶片": "faded film look, vintage colors", "Lomo相机效果": "Lomography style, high contrast, vignettes, saturated colors", "交叉冲洗": "cross-processing effect, surreal colors", "日系小清新": "Japanese photography style, airy, bright, soft colors", "湿版摄影": "wet-plate collodion photography look, antique", "CCTV监控画面": "CCTV footage style, low-res, timestamp", "8-bit像素艺术": "8-bit pixel art style", "柯达Ektar 100": "Kodak Ektar 100, ultra-fine grain, vivid colors", "柯达Tri-X 400": "Kodak Tri-X 400, grainy black and white, classic photojournalism look", "富士Velvia 50": "Fuji Velvia 50, high contrast, extreme saturation, for landscapes", "富士Superia 400": "Fuji Superia 400, cool tones, greenish cast", "Agfa Vista 200": "Agfa Vista 200, warm, reddish tones, nostalgic", "仙娜(CineStill) 800T": "CineStill 800T, tungsten balanced, halation effect on lights, cinematic night look", "红外胶片": "infrared film, false-color, dreamy landscapes", "正片(反转片)": "slide film, reversal film", "负片": "negative film", "过期胶片": "expired film look, unpredictable color shifts, increased grain", "一次性相机": "disposable camera look, harsh flash, soft focus", "大画幅相机(8x10)": "large format 8x10 camera, incredible detail, shallow depth of field", "中画幅相机(6x7)": "medium format 6x7 camera, rich tonality", "35mm胶片": "35mm film", "16mm电影胶片": "16mm film look, grainy, vintage cinema", "8mm电影胶片": "Super 8mm film look, very grainy, home movie feel", "IMAX胶片": "IMAX 70mm film, immense detail and clarity", "Technicolor电影": "Technicolor process, saturated, vibrant colors, classic Hollywood look", "黑白电影": "black and white cinematography", "有声黑白电影": "film noir cinematography", "德国表现主义": "German Expressionism style, distorted sets, strong shadows", "法国新浪潮": "French New Wave style, handheld, jump cuts", "意大利新现实主义": "Italian Neorealism style, non-professional actors, on-location shooting", "道格玛95": "Dogme 95 style, strict rules, naturalistic", "苏联蒙太奇": "Soviet Montage style, dynamic editing", "西部片风格": "Spaghetti Western style, extreme close-ups, wide shots", "恐怖片风格": "horror film style, found footage", "科幻片风格": "sci-fi film style, futuristic", "奇幻片风格": "fantasy film style, epic", "纪录片风格": "documentary style", "新闻摄影风格": "photojournalism style", "时尚摄影风格": "fashion photography style, editorial", "建筑摄影风格": "architectural photography style", "街头摄影风格": "street photography style", "体育摄影风格": "sports photography style, action frozen", "野生动物摄影": "wildlife photography style", "天文摄影": "astrophotography style", "微距摄影": "macro photography style", "航拍摄影": "aerial photography style", "水下摄影": "underwater photography style", "抽象摄影": "abstract photography style", "极简摄影": "minimalist photography style", "概念摄影": "conceptual photography style", "肖像摄影": "portrait photography style", "静物摄影": "still life photography style", "食物摄影": "food photography style", "产品摄影": "product photography style", "蓝晒法": "cyanotype process, blue and white print", "银版照相法": "daguerreotype process, mirror-like, detailed", "凹版印刷": "photogravure print look", "丝网印刷": "screenprint look", "木刻版画": "woodblock print look", "铜版画": "etching look", "石版画": "lithograph look", "水彩画": "watercolor painting style", "油画": "oil painting style", "丙烯画": "acrylic painting style", "蜡笔画": "crayon drawing style", "铅笔素描": "pencil sketch style", "炭笔素描": "charcoal sketch style", "钢笔画": "ink pen drawing style", "漫画书": "comic book art style", "动画片": "animation cel style", "定格动画": "stop-motion animation style", "粘土动画": "claymation style", "3D渲染": "3D render, CGI", "体素艺术": "voxel art style", "低多边形艺术": "low-poly art style", "故障艺术": "glitch art", "蒸汽波艺术": "vaporwave aesthetic", "赛博朋克艺术": "cyberpunk aesthetic", "蒸汽朋克艺术": "steampunk aesthetic", "柴油朋克艺术": "dieselpunk aesthetic", "原子朋克艺术": "atompunk aesthetic", "太阳朋克艺术": "solarpunk aesthetic", "生物朋克艺术": "biopunk aesthetic",
}
COLOR_PALETTES = {
    "-- 无 --": "", "单色": "monochromatic", "高饱和度": "vibrant, high saturation", "低饱和度/褪色": "desaturated, muted color palette", "暖色调": "warm color palette", "冷色调": "cool color palette", "粉彩色": "pastel color palette", "霓虹色": "neon color palette", "韦斯安德森风格": "Wes Anderson style, symmetrical, distinct color palette", "黑客帝国绿": "Matrix green color palette", "银翼杀手色调": "Blade Runner color palette, neon and dark tones", "双色调": "duotone color scheme", "三色调": "trichromatic color scheme", "黑暗学术风": "dark academia color palette, browns, grays, dark greens", "类似色": "analogous color scheme", "互补色": "complementary color scheme", "分裂互补色": "split-complementary color scheme", "矩形(四色)配色": "tetradic (rectangular) color scheme", "方形(四色)配色": "square color scheme", "高对比度": "high contrast colors", "低对比度": "low contrast colors", "黑白": "black and white", "深褐色(乌贼墨)": "sepia tone", "金色调": "golden hour palette", "蓝色调": "blue hour palette", "暮光色调": "twilight palette", "黎明色调": "dawn palette", "日落色调": "sunset palette", "彩虹色调": "rainbow palette", "金属色调": "metallic color palette (gold, silver, bronze)", "大地色调": "earth tones (browns, greens, beiges)", "海洋色调": "ocean tones (blues, greens, teals)", "森林色调": "forest tones (greens, browns)", "沙漠色调": "desert tones (oranges, yellows, browns)", "火山色调": "volcanic tones (reds, oranges, blacks)", "冰川色调": "glacial tones (whites, blues, cyans)", "城市色调": "urban color palette (grays, browns, blues)", "乡村色调": "rural color palette (greens, yellows, browns)", "复古色调": "retro color palette (e.g., 70s oranges and browns)", "80年代复古": "80s vaporwave palette (pinks, purples, teals)", "90年代复古": "90s grunge palette (muted reds, greens, browns)", "装饰艺术风格": "Art Deco color palette (gold, black, silver, bold colors)", "新艺术风格": "Art Nouveau color palette (earthy, organic colors)", "包豪斯风格": "Bauhaus color palette (primary colors: red, yellow, blue)", "波普艺术风格": "Pop Art color palette (bold, bright, contrasting colors)", "印象派风格": "Impressionist color palette (light, pastel colors)", "野兽派风格": "Fauvist color palette (intense, non-realistic colors)", "立体主义风格": "Cubist color palette (monochromatic, earthy tones)", "超现实主义风格": "Surrealist color palette (dreamlike, unexpected colors)", "极简主义风格": "minimalist color palette (neutrals, one or two accent colors)", "巴洛克风格": "Baroque color palette (rich, dramatic, dark colors)", "洛可可风格": "Rococo color palette (light, airy, pastel colors)", "哥特风格": "gothic color palette (dark, moody, black, red, purple)", "蒸汽朋克风格": "steampunk color palette (browns, brass, copper, dark red)", "赛博朋克风格": "cyberpunk color palette (neon, dark, blue, pink, purple)", "糖果色": "candy-colored palette", "宝石色": "jewel-toned palette (emerald, ruby, sapphire)", "荧光色": "fluorescent color palette", "磷光色": "phosphorescent color palette", "全息色": "holographic color palette", "热成像色": "thermal imaging color palette", "夜视绿色": "night vision green palette", "X光色": "X-ray color palette (black, white, gray)", "负片色": "inverted color palette", "故障艺术色": "glitchy color palette", "褪色/做旧": "faded, aged color palette", "手染色": "hand-tinted color palette", "水彩画": "watercolor palette", "油画色": "oil painting palette", "丙烯色": "acrylic paint palette", "蜡笔色": "crayon color palette", "彩色铅笔色": "colored pencil palette", "标记笔色": "marker pen palette", "自然光色": "natural light color palette", "人造光色": "artificial light color palette", "烛光色": "candlelight color palette", "霓虹灯色": "neon light color palette", "紫外光色": "blacklight color palette", "红灯区色": "red light district color palette", "黄金色": "golden color palette", "银色": "silver color palette", "铜色": "copper color palette", "铬色": "chrome color palette", "铁锈色": "rusty color palette", "血色": "blood-red color palette", "墨色": "inky black and white palette", "茶色": "tea-stained color palette", "咖啡色": "coffee-toned palette", "酒色": "wine-colored palette", "春天色": "spring color palette (fresh greens, pinks, yellows)", "夏天色": "summer color palette (bright blues, yellows, reds)", "秋天色": "autumn color palette (oranges, reds, browns, yellows)", "冬天色": "winter color palette (cool blues, whites, grays)",
}
COMPOSITIONS = {
    "-- 无 --": "", "三分法": "rule of thirds composition", "中心构图": "centered composition", "对称构图": "symmetrical composition", "引导线": "leading lines composition", "框架构图": "framing composition", "黄金比例": "golden ratio composition", "负空间": "negative space composition", "填充画面": "fill the frame composition", "对角线构图": "diagonal composition", "三角形构图": "triangle composition", "图案和重复": "patterns and repetition", "动态对称": "dynamic symmetry", "黄金三角": "golden triangles composition", "黄金螺旋": "golden spiral (Fibonacci spiral) composition", "不对称平衡": "asymmetrical balance", "径向平衡": "radial balance", "并置": "juxtaposition", "奇数法则": "rule of odds", "景深": "depth of field", "分层": "layering (foreground, middle ground, background)", "垂直构图": "vertical composition", "S形曲线构图": "S-curve composition", "C形曲线构图": "C-curve composition", "Z形构图": "Z-pattern composition", "交叉构图": "cross composition", "反射构图": "reflection composition", "透视构图": "perspective composition", "消失点构图": "vanishing point composition", "对称反射": "symmetrical reflection", "不对称平衡": "asymmetrical balance", "视觉重量平衡": "visual weight balance", "平面设计构图": "graphic design composition", "电影构图": "cinematographic composition", "广告构图": "advertising composition", "新闻构图": "photojournalism composition", "艺术构图": "fine art composition", "纪实构图": "documentary composition", "肖像构图": "portrait composition", "风景构图": "landscape composition", "街拍构图": "street photography composition", "微距构图": "macro composition", "建筑构图": "architectural composition", "时尚构图": "fashion composition", "美食构图": "food photography composition", "产品构图": "product photography composition", "运动构图": "sports composition", "野生动物构图": "wildlife composition", "水下构图": "underwater composition", "夜景构图": "night photography composition",
}

# 辅助函数: 用于处理随机选项
def get_random_value(data_dict, exclude_keys):
    """从字典中随机选择一个值，排除指定的键"""
    valid_keys = [k for k in data_dict.keys() if k not in exclude_keys]
    if not valid_keys:
        return ""
    random_key = random.choice(valid_keys)
    return data_dict[random_key]


# 内置的prompt集合
BUILTIN_PROMPTS = {
    "Qwen/Zimage": {
        "system_prompt": "你是一位拥有顶级审美和摄影知识的 AI 艺术总监。你的任务是接收用户的简单指令，对指令进行延展，增加更多的细节描述。最终以 [画面风格] +[主体描述] +[场景描述]+ [细节修饰] + [画面构图] + [光线信息] +[画面色彩倾向]+ [画质参数]这样的格式输出一段客观描述的自然语句。\\n画面风格包括：例如\"真实的画面\"\"日式动漫\"\"写实照片\"\"真实的写真照\"等等\\n主体描述包括：主体人物的详细描述（地域、性别、年龄、体型、动作、表情、情绪、服装造型），画面焦点的主体描述（物体/生物的细节描述，例如颜色、形状、细节、动作、大小等等）\\n细节修饰包括：突出1-3个关键细节（如面料纹理、饰品反光、发丝飘动、环境虚化等）\\n画面构图包括：运用一种或多种经典构图法（如三分法、框架式、引导线、低角度仰拍等），优先优化用户指令中的构图效果，若用户未指定，则输出最具美感的构图。\\n光线信息包括：根据氛围和场景，选择最匹配的光线类型（如侧逆光、黄金时刻逆光、漫射光等）。优先优化用户指令中的光线效果，例如用户输入\"逆光\"。优化结果应为：\"一束从人物侧后方出现的温暖光源，勾勒出人物的脸部的轮廓。\"\\n最终输出一段不多于 200 字的中文自然语句，语句不能出现换行的情况，不能出现除了\"，\"\"。\"\"！\"\"：\"以外的其他符号。避免中英混杂。\\n可以增加一些氛围的描述例如\"高级感\"、\"电影调色\"、\"冷暖色调对比\"能有效提升画面的质感，避免产生廉价的\"网感\"图片。\\n# 示例参考：\\n用户：\"一个妖娆的古装女子\"\\n最终输出：一位20岁左右的盛唐贵女，柳叶眉丹凤眼，红唇微启，乌黑高髻插点翠鎏金步摇与珍珠流苏簪，佩戴多层璎珞项圈，身穿大红色织金蹙金绣齐胸襦裙，衣襟袖口满布凤凰牡丹缠枝纹，金线熠熠生辉，腰系碧玉蹀躞带，侧身回眸一手抚髻一手搭雕花屏风，S型身姿妖娆眼神妩媚，背景为唐代宫廷内殿烛光摇曳纱帘半透，超精细工笔重彩风格参考《簪花仕女图》与敦煌壁画色彩，8K，高清细节。\\n\\n需要避免以下问题：\\n1.模糊不清的描述（如\"好看的东西\"）。\\n2.自相矛盾的元素（如\"白天的满天繁星\"）。\\n3.过于冗长或堆砌无关词汇。\\n4.描述出现换行的情况。",
        "user_prompt": "{需求}"
    },
    "Flux.2": {
        "system_prompt": "你是一位精通光影、构图、色彩心理学以及数字渲染技术的顶级艺术指导。你深知 Midjourney,  Flux 等顶级 AI 绘画模型的底层逻辑。你的目标是将用户简单的概念转化为**视觉冲击力极强、细节惊艳绝伦、具有电影级质感**的绘画提示词。\\n\\n## Workflow (工作流)\\n1.  **Analyze (分析):** 提取用户输入的核心主体、情感基调和场景。\\n2.  **Enhance (增强):** 自动补充缺失的美学元素（光影、材质、相机参数、艺术风格）。\\n3.  **Structure (结构化):** 按照\"主体描述 + 环境氛围 + 艺术风格 + 技术参数\"的黄金公式重组。\\n4.  **Output (输出):** 提供英文的自然语言提示词 (Prompt)，不能出现换行的情况。\\n\\n## The Golden Formula (黄金公式)\\n[Subject & Action] + [Environment & Context] + [Lighting & Atmosphere] + [Camera & Composition] + [Style & Medium] + [Color Palette] + [Quality Boosters]\\n\\n## Knowledge Base (美学词库 - 自动调用)\\n\\n### 1. Lighting (光影 - 决定质感)\\n* **Keywords:** Cinematic lighting (电影布光), Volumetric lighting (体积光/丁达尔效应), Rembrandt lighting (伦勃朗光), Bioluminescence (生物发光), Subsurface scattering (次表面散射 - 皮肤通透感), God rays (耶酥光).\\n\\n### 2. Composition (构图 - 决定张力)\\n* **Keywords:** Golden ratio (黄金比例), Rule of thirds (三分法), Low angle shot (低角度仰拍 - 宏大感), Extreme close-up (极端特写 - 细节感), Wide angle (广角), Depth of field (景深/背景虚化).\\n\\n### 3. Texture & Material (材质 - 决定真实度)\\n* **Keywords:** Hyper-realistic (超写实), Intricate details (错综复杂的细节), 8k texture (8k纹理), Unreal Engine 5 render (虚幻5渲染), Ray tracing (光线追踪).\\n\\n### 4. Style Modifiers (风格修饰)\\n* **Keywords:** Cyberpunk (赛博朋克), Steampunk (蒸汽朋克), Baroque (巴洛克), Minimalism (极简主义), Ukiyo-e (浮世绘), Concept art (概念设计).\\n\\n## Rules (约束)\\n1.  **Language:** 始终输出**英文**提示词，并且需要以自然语句进行描述。禁止换行。\\n2.  **No Conflicts:** 确保风格词不冲突（例如不要同时写\"黑白\"和\"彩虹色\"）。\\n3.  **Quality:** 必须包含提升画质的\"魔咒\" (Masterpiece, Best quality, Sharp focus)。\\n\\n## Interaction (交互示例)\\n**用户输入**：\\n人物：一名汉服美女在雪地，孤独唯美\\n\\n**示例输出**：\\nA beautiful young woman in traditional Hanfu, delicate pale skin with realistic texture, sorrowful eyes looking at the distance, petite figure. Wearing a red silk Hanfu cloak, heavy fabric draped elegantly over shoulders, snowflakes melting on the fabric, distinct contrast between red cloth and white snow. Standing alone in a vast snowy landscape, minimalist composition, massive negative space, soft overcast light, muted colors with vibrant red accent, cinematic shot, depth of field, shot on 35mm film, ethereal atmosphere, ultra-detailed, 8k",
        "user_prompt": "{需求}"
    }
}


class NakuNodePromptEVO:
    """
    NakuNode Prompt Evolution - 文字驱动的提示词生成器
    """

    @classmethod
    def INPUT_TYPES(s):
        # 创建AI模型选择列表
        model_list = ["Qwen/Zimage", "Flux.2"]

        # 创建API提供商列表
        provider_list = ["无", "智谱", "硅基流动"]

        inputs = {
            "required": {
                "文字需求": ("STRING", {"multiline": True, "default": "请输入您的图片生成需求"}),
                "AI模型选择": (model_list, {"default": "Qwen/Zimage"}),
                "API提供商": (provider_list, {"default": "无"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),

                # 添加摄影参数选项
                "相机视角": (["-- 无 --", "随机"] + list(CAMERA_ANGLES.keys()),),
                "镜头与光圈": (["-- 无 --", "随机"] + list(LENS_AND_APERTURE.keys()),),
                "胶片与风格": (["-- 无 --", "随机"] + list(FILM_TYPES.keys()),),
                "色彩与色调": (["-- 无 --", "随机"] + list(COLOR_PALETTES.keys()),),
                "构图方式": (["-- 无 --", "随机"] + list(COMPOSITIONS.keys()),),

                # 添加人物参数选项
                "国籍": (["-- 无 --", "随机"] + list(NATIONALITY_PRESETS.keys()),),
                "性别": (["-- 无 --", "随机"] + list(GENDER_PRESETS.keys()),),
                "年龄": (["-- 无 --", "随机"] + list(AGE_PRESETS.keys()),),
                "体型": (["-- 无 --", "随机"] + list(BODY_TYPE_PRESETS.keys()),),
                "服饰": (["-- 无 --", "随机"] + list(CLOTHING_PRESETS.keys()),),
                "表情": (["-- 无 --", "随机"] + list(EXPRESSIONS.keys()),),
                "发型": (["-- 无 --", "随机"] + list(HAIR_STYLES.keys()),),
                "发色": (["-- 无 --", "随机"] + list(HAIR_COLORS.keys()),),
            },
            "optional": {
                "API密钥": ("STRING", {"multiline": False, "default": "请输入API密钥"}),
                "硅基流动模型选择": (["KIMI-K2", "Qwen3", "DeepSeekV3", "GLM", "KIMI"], {"default": "Qwen3"}),  # 仅在选择硅基流动时使用
            }
        }

        return inputs

    RETURN_TYPES = ("STRING",)  # 输出描述
    RETURN_NAMES = ("生成的提示词",)
    FUNCTION = "generate_prompt"
    CATEGORY = "NakuNode/提示词生成"

    def generate_prompt(self, 文字需求, AI模型选择, API提供商, 随机种子,
                       相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式,
                       国籍, 性别, 年龄, 体型, 服饰, 表情, 发型, 发色,
                       API密钥=None, 硅基流动模型选择="Qwen3"):
        # 设置随机种子
        if 随机种子 == -1:
            随机种子 = random.randint(0, 0xffffffffffffffff)
        random.seed(随机种子)

        print(f"【NakuNode-Prompt】 开始处理请求 - API提供商: {API提供商}, AI模型选择: {AI模型选择}")
        print(f"【NakuNode-Prompt】 文字需求: {文字需求}")

        # 处理摄影参数 - 将它们直接附加到用户输入的提示词后面
        params = []
        data_map = {
            "相机视角": CAMERA_ANGLES,
            "镜头与光圈": LENS_AND_APERTURE,
            "胶片与风格": FILM_TYPES,
            "色彩与色调": COLOR_PALETTES,
            "构图方式": COMPOSITIONS,
            "国籍": NATIONALITY_PRESETS,
            "性别": GENDER_PRESETS,
            "年龄": AGE_PRESETS,
            "体型": BODY_TYPE_PRESETS,
            "服饰": CLOTHING_PRESETS,
            "表情": EXPRESSIONS,
            "发型": HAIR_STYLES,
            "发色": HAIR_COLORS
        }

        for param_name, param_value in [("相机视角", 相机视角), ("镜头与光圈", 镜头与光圈),
                                        ("胶片与风格", 胶片与风格), ("色彩与色调", 色彩与色调),
                                        ("构图方式", 构图方式), ("国籍", 国籍), ("性别", 性别),
                                        ("年龄", 年龄), ("体型", 体型), ("服饰", 服饰),
                                        ("表情", 表情), ("发型", 发型), ("发色", 发色)]:
            if param_value == "随机":
                selected_value = get_random_value(data_map[param_name], ["-- 无 --", "随机"])
                params.append(selected_value)
                print(f"【NakuNode-Prompt】 {param_name} (随机): {selected_value}")
            elif param_value != "-- 无 --":
                selected_value = data_map[param_name].get(param_value, "")
                params.append(selected_value)
                print(f"【NakuNode-Prompt】 {param_name}: {param_value} -> {selected_value}")

        # 将摄影参数附加到用户输入的提示词后面
        photo_params_str = ", ".join(filter(None, params))
        if photo_params_str:
            # 将摄影参数附加到原始需求后面
            enhanced_文字需求 = f"{文字需求}, {photo_params_str}"
            print(f"【NakuNode-Prompt】 增强后的需求: {enhanced_文字需求}")
        else:
            enhanced_文字需求 = 文字需求
            print(f"【NakuNode-Prompt】 未添加额外参数，使用原始需求: {enhanced_文字需求}")

        # 获取选定模型的提示词模板
        model_config = BUILTIN_PROMPTS.get(AI模型选择, BUILTIN_PROMPTS["Qwen/Zimage"])
        print(f"【NakuNode-Prompt】 使用模型配置: {AI模型选择}")

        # 构建完整的提示词
        system_prompt = model_config["system_prompt"]
        user_prompt = model_config["user_prompt"].format(需求=enhanced_文字需求)
        print(f"【NakuNode-Prompt】 System Prompt: {system_prompt[:100]}...")  # 只打印前100个字符
        print(f"【NakuNode-Prompt】 User Prompt: {user_prompt[:100]}...")      # 只打印前100个字符

        # 根据API提供商和模型选择决定是否调用API
        if API提供商 == "无" or not API密钥 or API密钥 == "请输入API密钥":
            # 不调用API，直接返回用户输入的文本和选择的选项，以逗号分隔
            print("【NakuNode-Prompt】 API提供商为'无'或API密钥为空，直接组合用户输入和选项")

            # 将所有参数组合成一个字符串
            all_parts = [文字需求] if 文字需求.strip() else []

            # 添加所有非空的参数
            for param_name, param_value in [("相机视角", 相机视角), ("镜头与光圈", 镜头与光圈),
                                            ("胶片与风格", 胶片与风格), ("色彩与色调", 色彩与色调),
                                            ("构图方式", 构图方式), ("国籍", 国籍), ("性别", 性别),
                                            ("年龄", 年龄), ("体型", 体型), ("服饰", 服饰),
                                            ("表情", 表情), ("发型", 发型), ("发色", 发色)]:
                if param_value and param_value not in ["-- 无 --", "随机"]:
                    selected_value = data_map[param_name].get(param_value, "")
                    if selected_value:
                        all_parts.append(selected_value)

            # 用逗号连接所有部分
            combined_prompt = ", ".join(all_parts)
            print(f"【NakuNode-Prompt】 组合后的提示词: {combined_prompt}")
            return (combined_prompt,)
        elif API提供商 == "硅基流动":
            # 硅基流动API调用
            print("【NakuNode-Prompt】 使用硅基流动API")
            if not API密钥 or API密钥 == "请输入API密钥":
                print("【NakuNode-Prompt】 错误：API密钥为空或未填写")
                raise ValueError("使用硅基流动时，请在API密钥字段中填入您的API密钥。")

            if OpenAI is None:
                print("【NakuNode-Prompt】 错误：OpenAI库未安装")
                raise ImportError("请安装openai库: pip install openai")

            # 根据模型选择设置对应的模型名称
            model_mapping = {
                "KIMI-K2": "Pro/moonshotai/Kimi-K2-Instruct-0905",
                "Qwen3": "Qwen/Qwen3-235B-A22B-Instruct-2507",
                "DeepSeekV3": "Pro/deepseek-ai/DeepSeek-V3.2",
                "GLM": "Pro/zai-org/GLM-4.7",
                "KIMI": "Pro/moonshotai/Kimi-K2.5"
            }

            selected_model = model_mapping.get(硅基流动模型选择, "Pro/zai-org/GLM-4.7")
            print(f"【NakuNode-Prompt】 选择的模型: {selected_model}")

            try:
                print("【NakuNode-Prompt】 正在创建客户端...")
                # 创建客户端
                client = OpenAI(
                    api_key=API密钥,
                    base_url="https://api.siliconflow.cn/v1"
                )
                print("【NakuNode-Prompt】 客户端创建成功")

                print("【NakuNode-Prompt】 正在调用API...")
                # 调用API
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                print("【NakuNode-Prompt】 API调用成功")

                # 获取API响应
                result = response.choices[0].message.content
                print(f"【NakuNode-Prompt】 API返回结果: {result[:100]}...")  # 只打印前100个字符
                return (result,)
            except Exception as e:
                error_msg = f"API调用失败: {str(e)}"
                print(error_msg)
                return (error_msg,)
        elif API提供商 == "智谱":
            # 智谱AI处理逻辑
            print("【NakuNode-Prompt】 使用智谱AI")
            if not API密钥 or API密钥 == "请输入API密钥":
                print("【NakuNode-Prompt】 错误：API密钥为空或未填写")
                raise ValueError("使用智谱AI时，请在API密钥字段中填入您的API密钥。")

            if ZhipuAiClient is None:
                print("【NakuNode-Prompt】 错误：ZhipuAiClient库未安装")
                raise ImportError("请安装zhipuai库: pip install zhipuai")

            try:
                print("【NakuNode-Prompt】 正在创建智谱AI客户端...")
                # 创建智谱AI客户端
                client = ZhipuAiClient(api_key=API密钥)
                print("【NakuNode-Prompt】 智谱AI客户端创建成功")

                print("【NakuNode-Prompt】 正在调用智谱AI API...")
                # 调用智谱AI API
                response = client.chat.completions.create(
                    model="glm-4.7",
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                    thinking={
                        "type": "enabled",    # 启用深度思考模式
                    },
                    max_tokens=65536,          # 最大输出 tokens
                    temperature=1.0           # 控制输出的随机性
                )
                print("【NakuNode-Prompt】 智谱AI API调用成功")

                # 获取API响应
                result = response.choices[0].message.content
                print(f"【NakuNode-Prompt】 智谱AI返回结果: {result[:100]}...")  # 只打印前100个字符
                return (result,)
            except Exception as e:
                error_msg = f"智谱AI API调用失败: {str(e)}"
                print(error_msg)
                return (error_msg,)
        else:
            # 默认情况，不调用API
            print(f"【NakuNode-Prompt】 未知的API提供商: {API提供商}，不调用API")
            full_prompt = f"{system_prompt}\n\n用户需求：{user_prompt}"
            return (full_prompt,)


# --- 注册节点到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "NakuNodePromptEVO": NakuNodePromptEVO
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodePromptEVO": "NakuNode-PromptEVO"
}