import requests
import json
import torch
import numpy as np
from PIL import Image
import io
import base64
import time
import jwt
import re
import random

# --------------------------------------------------------------------------------
# 辅助函数: 用于处理随机选项
# --------------------------------------------------------------------------------
def get_random_value(data_dict, exclude_keys):
    """从字典中随机选择一个值，排除指定的键"""
    valid_keys = [k for k in data_dict.keys() if k not in exclude_keys]
    if not valid_keys:
        return ""
    random_key = random.choice(valid_keys)
    return data_dict[random_key]

# --------------------------------------------------------------------------------
# 预设数据 (保持不变)
# --------------------------------------------------------------------------------

# --- 人像参数数据 ---
NATIONALITY_PRESETS = {
    "-- 无 --": "", "中国": "Chinese", "美国": "American", "日本": "Japanese", "英国": "British", "法国": "French", "德国": "German", "意大利": "Italian", "俄罗斯": "Russian", "加拿大": "Canadian", "澳大利亚": "Australian", "印度": "Indian", "巴西": "Brazilian", "韩国": "Korean", "西班牙": "Spanish", "墨西哥": "Mexican", "印度尼西亚": "Indonesian", "巴基斯坦": "Pakistani", "尼日利亚": "Nigerian", "孟加拉国": "Bangladeshi", "埃及": "Egyptian", "越南": "Vietnamese", "土耳其": "Turkish", "伊朗": "Iranian", "泰国": "Thai", "南非": "South African", "阿根廷": "Argentinian", "波兰": "Polish", "乌克兰": "Ukrainian", "沙特阿拉伯": "Saudi Arabian", "荷兰": "Dutch", "瑞典": "Swedish", "瑞士": "Swiss", "比利时": "Belgian", "奥地利": "Austrian", "希腊": "Greek", "葡萄牙": "Portuguese", "挪威": "Norwegian", "丹麦": "Danish", "芬兰": "Finnish", "爱尔兰": "Irish", "新西兰": "New Zealander", "新加坡": "Singaporean", "马来西亚": "Malaysian", "菲律宾": "Filipino", "以色列": "Israeli", "阿联酋": "Emirati", "哥伦比亚": "Colombian", "智利": "Chilean", "秘鲁": "Peruvian", "委内瑞拉": "Venezuelan", "罗马尼亚": "Romanian", "捷克": "Czech", "匈加利": "Hungarian", "哈萨克斯坦": "Kazakhstani", "乌兹别克斯坦": "Uzbek", "白俄罗斯": "Belarusian", "阿塞拜疆": "Azerbaijani", "格鲁吉亚": "Georgian", "亚美尼亚": "Armenian", "摩洛哥": "Moroccan", "阿尔及利亚": "Algerian", "突尼斯": "Tunisian", "利比亚": "Libyan", "苏丹": "Sudanese", "埃塞オ比亚": "Ethiopian", "肯尼亚": "Kenyan", "坦桑尼亚": "Tanzanian", "乌干达": "Ugandan", "加纳": "Ghanaian", "科特迪瓦": "Ivorian", "喀麦隆": "Cameroonian", "塞内加尔": "Senegalese", "津巴布韦": "Zimbabwean", "安哥拉": "Angolan", "莫桑比克": "Mozambican", "赞比亚": "Zambian", "伊拉克": "Iraqi", "叙利亚": "Syrian", "约旦": "Jordanian", "黎巴嫩": "Lebanese", "也门": "Yemeni", "阿曼": "Omani", "卡塔尔": "Qatari", "科威特": "Kuwaiti", "巴林": "Bahraini", "阿富汗": "Afghan", "尼泊尔": "Nepalese", "斯里兰卡": "Sri Lankan", "缅甸": "Burmese", "柬埔寨": "Cambodian", "老挝": "Laotian", "蒙古": "Mongolian", "朝鲜": "North Korean", "古巴": "Cuban", "海地": "Haitian", "多米尼加": "Dominican", "牙买加": "Jamaican", "危地马拉": "Guatemalan", "洪都拉斯": "Honduran", "萨尔瓦多": "Salvadoran", "尼加拉瓜": "Nicaraguan", "哥斯达黎加": "Costa Rican", "巴拿马": "Panamanian", "厄瓜多尔": "Ecuadorian", "玻利维亚": "Bolivian", "巴拉圭": "Paraguayan", "乌拉圭": "Uruguayan", "冰岛": "Icelandic", "卢森堡": "Luxembourgish", "马耳他": "Maltese", "塞浦路斯": "Cypriot", "立陶宛": "Lithuanian", "拉脱维亚": "Latvian", "爱沙尼亚": "Estonian", "斯洛文尼亚": "Slovenian", "斯洛伐克": "Slovak", "克罗地亚": "Croatian", "波斯尼亚和黑塞哥维那": "Bosnian", "塞尔维亚": "Serbian", "黑山": "Montenegrin", "北马其顿": "North Macedonian", "阿尔巴尼亚": "Albanian", "科索沃": "Kosovan", "摩尔多瓦": "Moldovan", "梵蒂冈": "Vatican", "圣马力诺": "Sammarinese", "摩纳哥": "Monacan", "安道尔": "Andorran", "列支敦士登": "Liechtensteiner",
}
SKIN_COLOR_PRESETS = {
    "-- 无 --": "", "白皙": "fair skin", "象牙白": "ivory skin", "瓷白": "porcelain skin", "粉白": "pale pink skin", "苍白": "pale skin", "雪白": "snow-white skin", "杏色": "apricot skin tone", "米色": "beige skin tone", "自然色": "natural skin tone", "浅肤色": "light skin", "中等肤色": "medium skin tone", "橄榄色": "olive skin", "小麦色": "wheat-colored skin, tanned", "古铜色": "bronze skin", "焦糖色": "caramel skin", "棕褐色": "tan skin", "深棕色": "dark brown skin", "巧克力色": "chocolate skin", "乌木色": "ebony skin", "黝黑": "dark skin", "黄皮肤": "yellow-toned skin", "红润": "rosy skin, ruddy complexion", "病态的": "sallow skin", "灰色": "ashen skin, gray tone", "蓝色": "blue skin", "绿色": "green skin", "紫色": "purple skin", "红色": "red skin", "金色": "golden skin", "银色": "silver skin", "金属色": "metallic skin", "铬色": "chrome skin", "半透明": "translucent skin", "发光的": "glowing skin", "生物发光": "bioluminescent skin", "磷光": "phosphorescent skin", "彩虹色": "rainbow-colored skin", "大理石纹": "marbled skin", "木纹": "wood grain skin", "石质": "stone-like skin", "水晶质": "crystalline skin", "火焰质": "flaming skin", "液体质": "liquid skin", "烟雾质": "smoky skin", "影子质": "shadowy skin", "星云质": "nebula skin", "像素化": "pixelated skin", "故障艺术": "glitchy skin", "几何图案": "geometric patterned skin", "部落图腾": "tribal patterns on skin", "电路板图案": "circuit board patterns on skin", "花卉图案": "floral patterns on skin", "动物斑纹(豹)": "leopard print skin", "动物斑纹(虎)": "tiger stripe skin", "动物斑纹(斑马)": "zebra stripe skin", "鳞片": "scaly skin", "羽毛": "feathered skin", "毛皮": "furry skin", "树皮": "bark-like skin", "龟裂": "cracked skin", "晒伤": "sunburned skin", "冻伤": "frostbitten skin", "湿润": "wet skin", "油腻": "oily skin", "干燥": "dry skin", "多汗": "sweaty skin", "沾满泥土": "mud-covered skin", "沾满沙子": "sandy skin", "沾满灰尘": "dusty skin", "沾满鲜血": "blood-splattered skin", "沾满油漆": "paint-splattered skin", "沾满金粉": "gold dust on skin", "沾满亮片": "glitter on skin", "有雀斑": "freckled skin", "有痣": "moles on skin", "有疤痕": "scarred skin", "有皱纹": "wrinkled skin", "有纹身": "tattooed skin", "有彩绘": "body-painted skin", "健康的": "healthy complexion", "不健康的": "unhealthy complexion", "年轻的": "youthful skin", "年迈的": "aged skin", "僵尸绿": "zombie green skin", "吸血鬼白": "vampiric pale skin", "兽人绿": "orcish green skin", "精灵白": "elven fair skin", "恶魔红": "demonic red skin", "天使光辉": "angelic glowing skin", "机器人灰": "robotic gray metal skin", "外星人灰": "alien gray skin", "爬行动物绿": "reptilian green skin", "两栖动物色": "amphibian colored skin", "深海生物色": "deep-sea creature colored skin",
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
FACE_SHAPES = {
    "-- 无 --": "", "鹅蛋脸": "oval face", "瓜子脸": "sunflower seed face", "圆脸": "round face", "方脸": "square face", "长脸": "long face", "心形脸": "heart-shaped face", "菱形脸": "diamond-shaped face", "三角脸": "triangle face", "娃娃脸": "baby face", "模特脸": "model's sharp face", "胖乎乎的脸": "chubby face", "消瘦的脸": "gaunt face", "有棱角的脸": "angular face", "高颧骨": "high cheekbones", "下颌线分明": "strong jawline", "V形脸": "V-shaped face", "梨形脸": "pear-shaped face", "男性化方脸": "masculine square face", "女性化柔和脸": "feminine soft face", "精灵般的脸": "elfin face", "饱满的脸颊": "full cheeks", "凹陷的脸颊": "hollow cheeks", "古典脸": "classical face", "英雄脸": "heroic face", "反派脸": "villainous face", "疲惫的脸": "weary face", "饱经风霜的脸": "weather-beaten face", "孩子气的脸": "childlike face", "贵族脸": "aristocratic face", "平民脸": "commoner's face", "机器人脸": "robotic face", "仿生人脸": "android face", "兽人脸": "orcish face", "哥布林脸": "goblin face", "矮人脸": "dwarven face", "吸血鬼脸": "vampiric face", "狼人脸": "werewolf face", "恶魔脸": "demonic face", "天使脸": "angelic face", "雕塑般的脸": "sculpted face", "不对称的脸": "asymmetrical face", "浮肿的脸": "puffy face", "瘦长的脸": "gaunt long face", "宽脸": "broad face", "窄脸": "narrow face", "肉感脸": "fleshy face", "骨感脸": "bony face", "晒伤的脸": "sunburned face", "苍白的脸": "pale face", "红润的脸": "ruddy face", "友善的脸": "friendly face", "冷酷的脸": "cold face", "智慧的脸": "wise face", "天真的脸": "innocent face", "狡猾的脸": "cunning face", "多愁善感的脸": "melancholic face", "快乐的脸": "joyful face", "愤怒的脸": "furious face", "恐惧的脸": "fearful face", "惊讶的脸": "surprised face", "厌恶的脸": "disgusted face", "漫画风格的脸": "comic book style face", "卡通脸": "cartoon face", "写实脸": "photorealistic face", "油画质感脸": "oil painting style face", "水彩质感脸": "watercolor style face", "像素化脸": "pixelated face", "几何脸": "geometric face", "破碎的脸": "shattered face", "融化的脸": "melting face", "木偶脸": "puppet face", "面具脸": "masked face", "伤痕累累的脸": "scarred face", "带有纹身的脸": "tattooed face", "带有穿环的脸": "pierced face", "发光的脸": "glowing face", "半机械脸": "cybernetically enhanced face", "外星人脸": "alien face", "植物融合脸": "plant-infused face", "水晶化脸": "crystallized face", "火焰组成的脸": "face made of fire", "流水组成的脸": "face made of water", "烟雾组成的脸": "face made of smoke", "影子脸": "shadowy face", "星云脸": "nebula face", "老年人的脸": "elderly face", "年轻人的脸": "youthful face", "中年人的脸": "middle-aged face", "婴儿肥": "baby fat cheeks", "酒窝": "dimples", "美人尖": "widow's peak", "无下巴": "chinless", "双下巴": "double chin", "强壮的下巴": "strong chin", "尖下巴": "pointed chin", "方下巴": "square chin", "圆下巴": "round chin",
}
EYE_TYPES = {
    "-- 无 --": "", "杏眼": "almond eyes", "丹凤眼": "phoenix eyes", "桃花眼": "peach blossom eyes", "圆眼": "round eyes", "细长眼": "slender eyes", "下垂眼": "downturned eyes", "上斜眼": "upturned eyes", "深陷的眼睛": "deep-set eyes", "突出的眼睛": "protruding eyes", "宽眼距": "wide-set eyes", "窄眼距": "close-set eyes", "单眼皮": "monolid eyes", "双眼皮": "double eyelid eyes", "欧式大双": "prominent double eyelids", "眯缝眼": "squinting eyes", "疲惫的眼睛": "tired eyes", "睁大的眼睛": "wide-open eyes", "狐狸眼": "fox eyes", "猫眼": "cat eyes", "鹰眼": "hawk eyes", "蛇眼": "snake eyes", "龙眼": "dragon eyes", "昆虫复眼": "insectoid compound eyes", "无神的眼睛": "vacant eyes", "锐利的眼睛": "sharp eyes", "温柔的眼睛": "gentle eyes", "悲伤的眼睛": "sad eyes", "快乐的眼睛": "joyful eyes", "愤怒的眼睛": "angry eyes", "恐惧的眼睛": "fearful eyes", "好奇的眼睛": "curious eyes", "充满智慧的眼睛": "wise eyes", "天真的眼睛": "innocent eyes", "狡猾的眼睛": "cunning eyes", "催眠的眼睛": "hypnotic eyes", "发光的眼睛": "glowing eyes", "没有瞳孔的眼睛": "pupil-less eyes", "巨大的眼睛": "oversized eyes", "微小的眼睛": "tiny eyes", "不对称的眼睛": "asymmetrical eyes", "肿胀的眼睛": "swollen eyes", "黑眼圈": "dark circles under eyes", "长睫毛": "long eyelashes", "短睫毛": "short eyelashes", "浓密的睫毛": "thick eyelashes", "稀疏的睫毛": "sparse eyelashes", "白色睫毛": "white eyelashes", "彩色睫毛": "colored eyelashes", "浓眉": "thick eyebrows", "细眉": "thin eyebrows", "一字眉": "unibrow", "高挑的眉毛": "high-arched eyebrows", "平直的眉毛": "straight eyebrows", "断眉": "broken eyebrow", "白眉": "white eyebrows", "赛博格义眼": "cybernetic eyes", "机械眼": "mechanical eyes", "时钟眼": "clockwork eyes", "漩涡眼": "vortex eyes", "星云眼": "nebula eyes", "火焰眼": "flaming eyes", "水晶眼": "crystal eyes", "宝石眼": "gemstone eyes", "多瞳眼": "multiple pupils per eye", "泪眼汪汪": "tearful eyes", "布满血丝的眼睛": "bloodshot eyes", "卡通风格眼睛": "cartoonish eyes", "动漫风格眼睛": "anime style eyes", "写实风格眼睛": "photorealistic eyes", "油画风格眼睛": "oil painting style eyes", "像素化眼睛": "pixelated eyes", "纽扣眼": "button eyes", "空洞的眼窝": "empty eye sockets", "闭着眼睛": "closed eyes", "眨眼": "winking eye", "斜视": "cross-eyed", "翻白眼": "rolling eyes", "戴着单片眼镜": "wearing a monocle", "戴着眼镜": "wearing glasses", "戴着眼罩": "wearing an eyepatch", "戴着护目镜": "wearing goggles", "戴着VR头显": "wearing a VR headset", "眼角有皱纹": "crow's feet wrinkles", "眼下有痣": "mole under eye", "眼角有疤": "scar near eye", "眼部有彩绘": "face paint around eyes", "烟熏妆": "smoky eyes makeup", "闪亮眼影": "glittery eyeshadow", "猫眼线": "cat-eye eyeliner", "未来感眼妆": "futuristic eye makeup",
}
EYE_COLORS = {
    "-- 无 --": "", "黑色": "black eyes", "深棕色": "dark brown eyes", "浅棕色": "light brown eyes", "琥珀色": "amber eyes", "榛色": "hazel eyes", "蓝色": "blue eyes", "绿色": "green eyes", "灰色": "gray eyes", "紫罗兰色": "violet eyes", "异色瞳": "heterochromia eyes", "发光的红眼": "glowing red eyes", "赛博格义眼": "cybernetic eyes", "熔岩般的眼睛": "molten lava eyes", "星空般的眼睛": "galaxy eyes", "全白的眼睛": "solid white eyes", "金色的眼睛": "golden eyes", "银色的眼睛": "silver eyes", "冰蓝色的眼睛": "ice blue eyes", "森林绿的眼睛": "forest green eyes", "血红色的眼睛": "blood red eyes", "橙色的眼睛": "orange eyes", "黄色的眼睛": "yellow eyes", "粉色的眼睛": "pink eyes", "青色眼睛": "cyan eyes", "品红色眼睛": "magenta eyes", "彩虹色眼睛": "rainbow eyes", "漩涡状眼睛": "swirling vortex eyes", "有图案的虹膜": "patterned iris", "猫眼状瞳孔": "cat-like slit pupils", "山羊状瞳孔": "goat-like horizontal pupils", "无瞳孔": "pupil-less eyes", "多瞳孔": "multiple pupils", "星形瞳孔": "star-shaped pupils", "钻石般的眼睛": "diamond eyes", "祖母绿眼睛": "emerald eyes", "蓝宝石眼睛": "sapphire eyes", "红宝石眼睛": "ruby eyes", "黑曜石眼睛": "obsidian eyes", "蛋白石眼睛": "opal eyes", "月光石眼睛": "moonstone eyes", "大理石纹眼睛": "marbled eyes", "木纹眼睛": "wood grain eyes", "金属色眼睛": "metallic eyes", "铬色眼睛": "chrome eyes", "铜色眼睛": "copper eyes", "青铜色眼睛": "bronze eyes", "霓虹色眼睛": "neon eyes", "磷光眼睛": "phosphorescent eyes", "全息眼睛": "holographic eyes", "像素化眼睛": "pixelated eyes", "故障艺术眼睛": "glitch effect eyes", "褪色的眼睛": "faded color eyes", "暗淡的眼睛": "dull eyes", "明亮的眼睛": "bright eyes", "清澈的眼睛": "clear eyes", "混浊的眼睛": "cloudy eyes", "失明的眼睛": "blind eyes", "烟熏色眼睛": "smoky eyes", "水汪汪的眼睛": "watery eyes", "油画般的眼睛": "oil-painted eyes", "水彩画般的眼睛": "watercolor eyes", "墨水般的眼睛": "inky black eyes", "天空蓝眼睛": "sky blue eyes", "海洋绿眼睛": "ocean green eyes", "日落色眼睛": "sunset-colored eyes", "黎明色眼睛": "dawn-colored eyes", "暮光色眼睛": "twilight-colored eyes", "火焰色眼睛": "fire-colored eyes", "闪电色眼睛": "lightning-colored eyes", "宇宙色眼睛": "cosmic eyes", "万花筒眼睛": "kaleidoscope eyes", "液体黄金眼睛": "liquid gold eyes", "液体白银眼睛": "liquid silver eyes", "水银眼睛": "mercury eyes", "有裂纹的眼睛": "cracked iris", "分段色虹膜": "sectoral heterochromia", "中央异色瞳": "central heterochromia", "深邃的眼睛": "deep, profound eyes", "空洞的眼睛": "hollow eyes", "机器人发光眼": "glowing robotic eyes", "外星昆虫眼": "alien insectoid eyes", "爬行动物眼": "reptilian eyes", "鸟类眼睛": "avian eyes", "哺乳动物眼睛": "mammalian eyes", "深海生物眼": "deep-sea creature eyes", "幽灵般的眼睛": "ghostly eyes",
}
EXPRESSIONS = {
    "-- 无 --": "", "微笑": "smiling", "大笑": "laughing", "哭泣": "crying", "愤怒": "angry", "悲伤": "sad", "惊讶": "surprised", "恐惧": "scared", "厌恶": "disgusted", "沉思": "pensive", "困惑": "confused", "喜悦": "joyful", "平静": "calm", "顽皮的": "playful", "严肃的": "serious", "傲慢的": "arrogant", "害羞的": "shy", "轻蔑的": "contemptuous", "渴望的": "longing", "痛苦的": "pained", "得意的": "smug", "醉酒的": "drunk", "疯狂的": "insane", "狂喜的": "ecstatic", "面无表情": "expressionless", "幸灾乐祸": "gloating", "嫉妒": "jealous", "怀疑": "skeptical", "好奇": "curious", "敬畏": "in awe", "尴尬": "embarrassed", "内疚": "guilty", "满足": "content", "放松": "relaxed", "疲惫": "exhausted", "无聊": "bored", "紧张": "nervous", "焦虑": "anxious", "充满希望": "hopeful", "绝望": "despairing", "勇敢": "brave", "胆怯": "timid", "专注": "focused", "心烦意乱": "distracted", "深情": "affectionate", "冷漠": "indifferent", "敌对": "hostile", "和蔼可亲": "amiable", "闷闷不乐": "sullen", "兴高采烈": "elated", "沮丧": "dejected", "沾沾自喜": "complacent", "挑衅": "defiant", "顺从": "submissive", "狡猾": "sly", "天真": "naive", "愤世嫉俗": "cynical", "乐观": "optimistic", "悲观": "pessimistic", "歇斯底里": "hysterical", "庄严": "solemn", "沉着": "composed", "激动": "agitated", "恼怒": "annoyed", "狂怒": "enraged", "惊恐": "terrified", "震惊": "shocked", "着迷": "mesmerized", "失望": "disappointed", "宽慰": "relieved", "自豪": "proud", "谦逊": "humble", "顽固": "stubborn", "优柔寡断": "indecisive", "果断": "decisive", "热情": "enthusiastic", "冷淡": "apathetic", "冥想中": "meditative", "做鬼脸": "making a face", "傻笑": "giggling", "假笑": "smirking", "抽泣": "sobbing", "呻吟": "groaning", "叹气": "sighing", "打哈欠": "yawning", "打喷嚏": "sneezing", "咳嗽": "coughing", "喘气": "gasping", "屏住呼吸": "holding breath", "咬紧牙关": "gritting teeth", "舔嘴唇": "licking lips", "皱眉": "frowning", "扬眉": "raising eyebrows", "眯眼": "squinting", "瞪眼": "glaring",
}
NOSE_TYPES = {
    "-- 无 --": "", "希腊鼻": "Greek nose", "罗马鼻": "Roman nose", "鹰钩鼻": "aquiline nose", "小翘鼻": "upturned nose", "蒜头鼻": "bulbous nose", "高挺鼻梁": "high bridge nose", "宽鼻子": "wide nose", "小鼻子": "small nose", "塌鼻子": "flat nose", "有雀斑的鼻子": "freckled nose", "带鼻环的鼻子": "pierced nose", "有鼻涕": "with nasal discharge", "湿润的鼻子": "wet nose", "干燥的鼻子": "dry nose", "有鼻毛": "with nose hair visible", "有粉刺的鼻子": "with pimples on nose", "有疤痕的鼻子": "scarred nose", "歪斜的鼻子": "crooked nose", "鹰钩鼻": "hooked nose", "蒜头鼻": "potato nose", "朝天鼻": "snub nose", "尖鼻子": "pointed nose", "圆鼻头": "round nasal tip", "扁平鼻": "flat nose", "狮子鼻": "pug nose", "长鼻子": "long nose", "短鼻子": "short nose", "窄鼻": "narrow nose", "宽鼻": "broad nose", "高鼻梁": "high nasal bridge", "低鼻梁": "low nasal bridge", "驼峰鼻": "bumpy nose with hump", "分裂鼻": "cleft nose", "象鼻": "elephant trunk nose", "猪鼻子": "pig nose", "动物鼻": "animal-like nose", "机器人鼻": "robotic nose", "外星人鼻": "alien nose", "奇异鼻形": "unusual nose shape", "理想鼻型": "ideal nose shape", "古典鼻型": "classical nose shape", "现代鼻型": "modern nose shape", "卡通鼻": "cartoon-style nose", "几何鼻": "geometric nose shape", "破损鼻": "broken nose", "整形后": "post-rhinoplasty nose", "鼻孔外露": "visible nostrils", "鼻孔朝上": "upward-facing nostrils", "鼻孔朝下": "downward-facing nostrils", "鼻孔不对称": "asymmetrical nostrils", "鼻尖上翘": "upturned nasal tip", "鼻尖下垂": "drooping nasal tip", "鼻尖突出": "projecting nasal tip", "鼻尖圆钝": "rounded nasal tip", "鼻尖尖锐": "sharp nasal tip", "鼻翼宽大": "wide alar base", "鼻翼窄小": "narrow alar base", "鼻翼厚实": "thick alar base", "鼻翼薄削": "thin alar base", "鼻中隔偏曲": "deviated septum visible", "鼻窦炎外观": "appearance of sinusitis", "过敏性鼻炎": "allergic rhinitis appearance", "酒糟鼻": "rhinophyma, enlarged red nose", "冻疮鼻": "chilblain nose", "晒伤鼻": "sunburned nose", "受伤鼻": "injured nose", "手术鼻": "surgically altered nose", "化妆品鼻": "makeup-enhanced nose", "阴影鼻": "artistically shaded nose", "高光鼻": "artistically highlighted nose", "轮廓鼻": "contoured nose", "光影鼻": "nose defined by light and shadow", "透视鼻": "nose with proper perspective", "解剖鼻": "anatomically accurate nose", "比例鼻": "proportionally correct nose", "美学鼻": "aesthetically pleasing nose", "功能鼻": "functionally sound nose", "呼吸鼻": "breath-friendly nose", "嗅觉鼻": "nose with keen sense of smell", "家族鼻": "family-heritage nose", "种族鼻": "ethnically typical nose", "个人鼻": "personally distinctive nose", "独特鼻": "unique nose", "普通鼻": "ordinary nose", "无名鼻": "unremarkable nose", "标志鼻": "signature nose", "明星鼻": "celebrity-style nose", "偶像鼻": "idol-type nose", "理想型鼻": "ideal-type nose", "梦幻鼻": "dream nose", "完美鼻": "perfect nose",
}
LIP_SHAPES = {
    "-- 无 --": "", "丰满的嘴唇": "full lips", "薄嘴唇": "thin lips", "M唇": "Cupid's bow lips", "心形唇": "heart-shaped lips", "宽嘴唇": "wide lips", "下垂的嘴角": "downturned lips", "涂着口红": "wearing lipstick", "咬着嘴唇": "biting lip", "微微张开的嘴唇": "slightly parted lips", "干裂的嘴唇": "chapped lips", "黑色的口红": "black lipstick", "蓝色的口红": "blue lipstick", "金属色口红": "metallic lipstick", "上扬的嘴角": "upturned lips", "紧闭的嘴唇": "tightly closed lips", "撅嘴": "pouting lips", "露齿笑": "toothy grin", "傻笑": "goofy smile", "假笑": "smirk", "冷笑": "sneer", "饱满的下唇": "full bottom lip", "饱满的上唇": "full top lip", "唇线分明": "defined lip line", "唇线模糊": "undefined lip line", "有唇珠": "prominent philtrum", "无唇珠": "flat philtrum", "唇色(粉)": "pink lips", "唇色(红)": "red lips", "唇色(裸)": "nude lips", "唇色(紫)": "purple lips", "唇色(苍白)": "pale lips", "唇彩": "glossy lips", "哑光唇": "matte lips", "渐变唇": "gradient lips", "双色唇": "two-tone lips", "有唇钉": "lip piercing", "拉链嘴": "zipper mouth", "缝合的嘴": "stitched mouth", "獠牙": "fangs", "尖牙": "sharp teeth", "龅牙": "buck teeth", "牙齿不齐": "crooked teeth", "完美的牙齿": "perfect teeth", "金牙": "gold tooth", "缺牙": "missing tooth", "舌头伸出": "tongue sticking out", "吹口哨": "whistling", "抽烟": "smoking a cigarette", "叼着玫瑰": "rose in mouth", "吃棒棒糖": "eating a lollipop", "吹泡泡糖": "blowing bubble gum", "嘴角有痣": "mole near lips", "嘴角有疤": "scar near lips", "有胡须": "mustache", "有山羊胡": "goatee", "络腮胡": "full beard", "嘴角有食物残渣": "food crumbs on lips", "嘴角流口水": "drooling", "机器人嘴": "robotic mouth", "兽嘴": "bestial maw", "鸟喙": "beak", "昆虫口器": "insectoid mandibles", "卡通嘴": "cartoon mouth", "写实嘴": "realistic mouth", "油画嘴": "oil-painted mouth", "水彩嘴": "watercolor mouth", "像素化嘴": "pixelated mouth", "几何嘴": "geometric mouth", "水晶嘴": "crystal mouth", "火焰嘴": "flaming mouth", "影子嘴": "shadowy mouth", "外星人嘴": "alien mouth", "植物嘴": "plant-like mouth", "多嘴": "multiple mouths", "无嘴": "mouthless", "优雅的嘴唇": "elegant lips", "性感的嘴唇": "sensual lips", "孩子气的嘴唇": "childish lips", "年迈的嘴唇": "aged lips", "干瘪的嘴唇": "shriveled lips", "湿润的嘴唇": "wet lips", "柔软的嘴唇": "soft lips", "坚硬的嘴唇": "firm lips", "有纹身的嘴唇": "tattooed lips", "发光的嘴唇": "glowing lips", "半透明的嘴唇": "translucent lips", "彩虹色口红": "rainbow lipstick", "闪粉口红": "glitter lipstick", "夜光口红": "glow-in-the-dark lipstick", "吃东西": "eating", "喝水": "drinking", "说话": "talking", "喊叫": "shouting", "唱歌": "singing", "耳语": "whispering",
}
HAIR_STYLES = {
    "-- 无 --": "", "长直发": "long straight hair", "大波浪卷发": "wavy long hair", "短发": "short hair", "寸头": "buzz cut", "丸子头": "bun hairstyle", "高马尾": "high ponytail", "双马尾": "twin tails", "脏辫": "dreadlocks", "编发": "braided hair", "莫霍克发型": "mohawk hairstyle", "赛博朋克发光发型": "cyberpunk glowing hair", "湿发": "wet hair", "爆炸头": "afro hairstyle", "地中海发型": "bald top with hair on sides", "完全光头": "completely bald", "复古波波头": "vintage bob cut", "凌乱的短发": "messy short hair", "油头": "slicked-back hair", "火焰般的头发": "flaming hair", "水晶般的头发": "crystal hair", "星云般的头发": "nebula pattern hair", "瀑布般的长发": "waterfall of long hair", "及腰长发": "waist-length hair", "及肩中发": "shoulder-length hair", "精灵短发": "pixie cut", "不对称发型": "asymmetrical haircut", "碗盖头": "bowl cut", "鲻鱼头": "mullet hairstyle", "离子烫": "chemically straightened hair", "玉米烫": "cornrows", "法式编发": "french braid", "鱼骨辫": "fishtail braid", "荷兰辫": "dutch braid", "皇冠编发": "crown braid", "武士头": "samurai topknot", "维京风格发型": "viking style hair with braids and beads", "哥特风格发型": "gothic style hair, long and black", "朋克风格发型": "punk style spiky hair", "摇滚风格发型": "rockabilly pompadour", "波西米亚风发型": "bohemian style with waves and flowers", "未来感发型": "futuristic geometric haircut", "反重力头发": "anti-gravity hair, floating upwards", "液体头发": "liquid-like hair", "金属丝头发": "hair made of metallic wires", "玻璃纤维头发": "hair made of glass fibers", "植物藤蔓头发": "hair made of vines and leaves", "触手头发": "tentacle hair", "羽毛头发": "hair made of feathers", "云朵头发": "hair made of clouds", "烟雾头发": "hair made of smoke", "影子头发": "hair made of shadows", "像素化头发": "pixelated hair", "几何形状头发": "geometric shaped hair", "发光的头发": "glowing hair", "半透明头发": "translucent hair", "彩虹色头发": "rainbow colored hair", "双色头发": "half and half colored hair", "隐藏染发": "hidden rainbow hair", "头巾": "wearing a headscarf", "兜帽": "wearing a hood", "帽子": "wearing a hat", "发带": "wearing a headband", "发夹": "hair clips", "蝴蝶结": "hair bow", "皇冠": "wearing a crown", "花环": "wearing a flower wreath", "头盔": "wearing a helmet", "风中凌乱的头发": "windblown hair", "水下漂浮的头发": "hair floating underwater", "刚睡醒的头发": "bedhead hair", "精心打理的头发": "perfectly coiffed hair", "油腻的头发": "greasy hair", "干燥的头发": "dry, frizzy hair", "有头皮屑": "dandruff in hair", "头发稀疏": "thinning hair", "头发浓密": "thick, voluminous hair", "有刘海": "bangs / fringe", "斜刘海": "side-swept bangs", "齐刘海": "blunt bangs", "空气刘海": "see-through bangs", "窗帘式刘海": "curtain bangs", "无刘海": "no bangs, forehead exposed", "美人尖": "widow's peak hairline", "发际线高": "receding hairline", "发际线低": "low hairline", "鬓角": "sideburns", "剃掉一侧的头发": "shaved side haircut", "头皮纹身": "scalp tattoo", "头发上有珠子": "beads in hair", "头发上有闪粉": "glitter in hair", "头发上有树叶": "leaves in hair", "头发上有雪花": "snowflakes in hair",
}
HAIR_COLORS = {
    "-- 无 --": "", "黑色": "black hair", "金色": "blonde hair", "棕色": "brown hair", "红色": "red hair", "白色": "white hair", "银色": "silver hair", "粉色": "pink hair", "蓝色": "blue hair", "绿色": "green hair", "彩虹色": "rainbow hair", "渐变发色": "gradient hair", "挑染": "highlighted hair", "白金色": "platinum blonde hair", "姜黄色": "ginger hair", "深紫色": "deep purple hair", "霓虹绿色": "neon green hair", "双色拼接": "split-dyed hair (half black, half white)", "星空色": "galaxy-colored hair", "自然黑": "natural black hair", "深棕色": "dark brown hair", "巧克力棕": "chocolate brown hair", "浅棕色": "light brown hair", "焦糖色": "caramel brown hair", "灰金色": "ash blonde hair", "草莓金": "strawberry blonde hair", "蜂蜜金": "honey blonde hair", "酒红色": "burgundy red hair", "铜红色": "copper red hair", "樱桃红": "cherry red hair", "亮红色": "bright red hair", "灰色": "gray hair", "钢灰色": "steel gray hair", "木炭色": "charcoal gray hair", "淡紫色": "lavender purple hair", "紫罗兰色": "violet purple hair", "天蓝色": "sky blue hair", "宝蓝色": "royal blue hair", "海军蓝": "navy blue hair", "薄荷绿": "mint green hair", "森林绿": "forest green hair", "橄榄绿": "olive green hair", "酸 lime绿": "lime green hair", "橙色": "orange hair", "桃色": "peach hair", "黄色": "yellow hair", "青色": "cyan hair", "品红色": "magenta hair", "蒂芙尼蓝": "tiffany blue hair", "玫瑰金": "rose gold hair", "多色挑染": "multi-color streaks", "隐藏彩虹染": "hidden rainbow highlights", "裙摆染": "dip-dyed hair", "发根补染": "grown-out roots", "荧光色": "fluorescent hair", "磷光色": "phosphorescent hair", "全息色": "holographic hair", "金属色": "metallic hair", "铬色": "chrome hair", "铜色": "copper hair", "青铜色": "bronze hair", "褪色效果": "faded color effect", "柔和的粉彩色": "soft pastel hair", "鲜艳的霓虹色": "vivid neon hair", "深色系": "dark color scheme hair", "浅色系": "light color scheme hair", "大地色系": "earth-toned hair", "宝石色系": "jewel-toned hair", "火焰色渐变": "fire-colored gradient hair", "海洋色渐变": "ocean-colored gradient hair", "日落色渐变": "sunset-colored gradient hair", "极光色": "aurora-colored hair", "宇宙尘埃色": "cosmic dust colored hair", "大理石纹染发": "marbled hair color", "豹纹染发": "leopard print hair color", "斑马纹染发": "zebra print hair color", "像素化染发": "pixelated hair color", "故障艺术染发": "glitch effect hair color", "木纹色": "wood grain colored hair", "石纹色": "stone-like colored hair", "水晶色": "crystal-colored hair", "烟熏色": "smoky colored hair", "半透明色": "translucent colored hair", "变色龙色": "chameleon color-changing hair", "热感应变色": "heat-reactive color-changing hair", "紫外光下变色": "UV-reactive hair color", "单色": "monochromatic hair", "双色": "dichromatic hair", "三色": "trichromatic hair", "四色": "tetrachromatic hair", "五彩斑斓": "polychromatic hair", "不饱和色": "desaturated hair color", "高饱和色": "highly saturated hair color", "自然发色": "natural hair color", "非自然发色": "unnatural hair color",
}
SKIN_TEXTURES = {
    "-- 无 --": "", "光滑细腻": "smooth skin", "雀斑": "freckles", "皱纹": "wrinkles", "伤疤": "scars", "晒黑的皮肤": "tanned skin", "苍白的皮肤": "pale skin", "油性皮肤": "oily skin", "水光肌": "dewy skin", "金属质感皮肤": "metallic skin", "发光的皮肤": "glowing skin", "有纹身": "tattoos on skin", "龟裂的皮肤": "cracked skin, like earth", "树皮般的皮肤": "bark-like skin", "水晶般的皮肤": "crystalline skin", "半透明的皮肤": "translucent skin", "被雨淋湿的皮肤": "rain-drenched skin", "沾满泥土的皮肤": "mud-covered skin", "沾满油漆的皮肤": "paint-splattered skin", "古铜色皮肤": "bronzed skin", "象牙色皮肤": "ivory skin", "橄榄色皮肤": "olive skin", "焦糖色皮肤": "caramel skin", "乌木色皮肤": "ebony skin", "白皙皮肤": "fair skin", "黝黑皮肤": "dark skin", "黄皮肤": "yellow-toned skin", "红润皮肤": "rosy skin", "病态的皮肤": "sallow skin", "有痣": "moles on skin", "胎记": "birthmark", "老年斑": "age spots", "毛孔粗大": "visible pores", "粉刺": "acne", "水痘疤痕": "chickenpox scars", "手术疤痕": "surgical scar", "烧伤疤痕": "burn scar", "刀伤疤痕": "knife scar", "缝合线": "stitches", "干燥脱皮": "dry, peeling skin", "湿润的皮肤": "moist, wet skin", "出汗的皮肤": "sweaty skin", "有光泽的皮肤": "shiny skin", "哑光皮肤": "matte skin", "天鹅绒般的皮肤": "velvety skin", "丝绸般的皮肤": "silky skin", "皮革般的皮肤": "leathery skin", "鳞片皮肤": "scaly skin", "羽毛皮肤": "feathered skin", "毛皮": "furry skin", "多毛的": "hairy skin", "无毛的": "hairless skin", "机械义肢": "cybernetic limbs", "皮肤下的电路": "circuits visible under skin", "生物发光图案": "bioluminescent patterns on skin", "全息纹身": "holographic tattoos", "像素化皮肤": "pixelated skin", "故障艺术皮肤": "glitch effect skin", "几何图案皮肤": "geometric patterned skin", "大理石纹皮肤": "marbled skin", "木纹皮肤": "wood grain skin", "石化皮肤": "petrified skin", "熔岩皮肤": "molten lava skin", "冰冻皮肤": "frozen, icy skin", "火焰皮肤": "flaming skin", "烟雾皮肤": "smoky skin", "影子皮肤": "shadowy skin", "星云皮肤": "nebula skin", "透明皮肤": "transparent skin, organs visible", "果冻状皮肤": "jelly-like skin", "彩绘": "body paint", "涂鸦": "graffiti on skin", "沾满鲜血": "blood-splattered skin", "沾满灰尘": "dusty skin", "沾满沙子": "sandy skin", "沾满面粉": "flour-covered skin", "沾满金粉": "covered in gold dust", "沾满亮片": "covered in glitter", "长满苔藓": "moss-covered skin", "长满藤蔓": "vine-covered skin", "长满蘑菇": "mushrooms growing on skin", "腐烂的皮肤": "decaying skin", "僵尸皮肤": "zombie skin", "木乃伊皮肤": "mummified skin", "机器人外壳": "robotic shell", "玩偶皮肤": "doll-like porcelain skin", "充气娃娃皮肤": "inflatable plastic skin", "卡通皮肤": "cartoon skin", "油画皮肤": "oil-painted skin", "水彩皮肤": "watercolor skin", "蜡质皮肤": "waxy skin", "年轻的皮肤": "youthful skin", "年迈的皮肤": "elderly, wrinkled skin", "婴儿皮肤": "baby-soft skin", "健康的肤色": "healthy complexion", "不健康的肤色": "unhealthy complexion",
}

# --- 摄影参数数据 ---
CAMERA_ANGLES = {
    "-- 无 --": "", "正面视角": "front view", "侧面视角": "profile view", "45度角": "three-quarters view", "背面视角": "back view", "高角度/俯视": "high-angle shot, bird's-eye view", "低角度/仰视": "low-angle shot, worm's-eye view", "荷兰角/倾斜": "dutch angle, tilted shot", "过肩视角": "over-the-shoulder shot", "主观视角(POV)": "point-of-view shot (POV)", "地面视角": "ground-level shot", "航拍视角": "aerial shot", "特写": "extreme close-up", "大特写": "close-up shot", "中景": "medium shot", "全景": "full shot, long shot", "远景": "extreme long shot", "牛仔镜": "cowboy shot (mid-thigh up)", "双人镜头": "two-shot", "三人镜头": "three-shot", "群像镜头": "group shot", "建立镜头": "establishing shot", "反应镜头": "reaction shot", "插入镜头": "insert shot", "推镜头": "push-in shot", "拉镜头": "pull-out shot", "摇镜头(水平)": "pan shot", "移镜头(垂直)": "tilt shot", "跟拍镜头": "tracking shot", "弧形跟拍": "arc shot", "起重机镜头": "crane shot", "无人机镜头": "drone shot", "手持摄影机": "handheld camera shot", "斯坦尼康": "steadicam shot", "固定镜头": "static shot", "变焦镜头": "zoom shot", "快速变焦": "crash zoom", "慢速变焦": "slow zoom", "眩晕变焦": "dolly zoom, vertigo effect", "窥视视角": "voyeuristic shot", "反射镜头": "reflection shot (in a mirror or water)", "剪影镜头": "silhouette shot", "框架中的框架": "frame within a frame", "对称视角": "symmetrical shot", "不对称视角": "asymmetrical shot", "黄金比例视角": "golden ratio shot", "引导线视角": "leading lines shot", "对角线视角": "diagonal shot", "三角形视角": "triangular composition shot", "圆形视角": "circular composition shot", "S形曲线视角": "S-curve composition shot", "负空间视角": "negative space shot", "填充画面视角": "fill the frame shot", "极简主义视角": "minimalist shot", "巴洛克风格视角": "baroque, cluttered shot", "纪实风格视角": "documentary style shot", "电影风格视角": "cinematic shot", "广告风格视角": "commercial style shot", "音乐视频风格": "music video style shot", "游戏视角": "video game perspective (first-person)", "第三人称游戏视角": "video game perspective (third-person)", "等距视角": "isometric view", "顶视图": "top-down view", "剖面图": "cross-section view", "展开图": "exploded view", "全景图": "panorama shot", "360度视角": "360-degree view", "红外视角": "infrared view", "热成像视角": "thermal view", "X光视角": "X-ray view", "夜视视角": "night vision view", "鱼眼视角": "fisheye view", "微距视角": "macro view", "长曝光视角": "long exposure shot", "多重曝光视角": "multiple exposure shot", "光绘视角": "light painting shot", "移轴摄影视角": "tilt-shift shot", "针孔相机视角": "pinhole camera view", "湿版火棉胶视角": "wet-plate collodion view", "宝丽来视角": "Polaroid view", "Lomo视角": "Lomography view", "CCTV视角": "CCTV view", "仪表盘摄像头视角": "dashcam view", "身体摄像头视角": "bodycam view", "无人机竞速视角": "FPV drone view", "卫星视角": "satellite view", "望远镜视角": "telescope view", "显微镜视角": "microscope view", "潜望镜视角": "periscope view", "门镜视角": "peephole view", "低保真视角": "lo-fi aesthetic shot", "高保真视角": "hi-fi aesthetic shot", "故障艺术视角": "glitch art shot",
}
LENS_AND_APERTURE = {
    "-- 无 --": "", "广角镜头": "wide-angle lens", "长焦镜头": "telephoto lens", "鱼眼镜头": "fisheye lens", "微距镜头": "macro lens", "大光圈(背景虚化)": "wide aperture, f/1.8, shallow depth of field, bokeh background", "小光圈(前后景清晰)": "narrow aperture, f/16, deep depth of field", "移轴镜头": "tilt-shift lens, miniature faking", "变形宽荧幕镜头": "anamorphic lens", "柔焦镜头": "soft-focus lens", "红外镜头": "infrared lens", "热成像镜头": "thermal imaging lens", "针孔相机效果": "pinhole camera effect", "标准镜头(50mm)": "standard 50mm lens", "超广角镜头(14mm)": "ultra-wide angle 14mm lens", "肖像镜头(85mm)": "portrait 85mm lens", "超级长焦(600mm)": "super-telephoto 600mm lens", "中等光圈(f/5.6)": "medium aperture, f/5.6", "极大光圈(f/0.95)": "extremely wide aperture, f/0.95", "极小光圈(f/32)": "extremely narrow aperture, f/32", "圆形光斑": "circular bokeh", "六边形光斑": "hexagonal bokeh", "旋涡光斑": "swirly bokeh", "甜甜圈光斑": "donut bokeh (from mirror lens)", "镜头光晕": "lens flare", "星芒效果": "sunstar effect", "色差": "chromatic aberration", "暗角": "vignetting", "桶形失真": "barrel distortion", "枕形失真": "pincushion distortion", "无畸变镜头": "rectilinear lens", "电影镜头": "cinema lens", "老式镜头": "vintage lens", "现代镜头": "modern, sharp lens", "塑料玩具镜头": "plastic toy camera lens", "DIY镜头": "DIY, handmade lens", "液体镜头": "liquid lens", "变焦镜头(广角到长焦)": "zoom lens (wide to telephoto)", "定焦镜头": "prime lens", "增距镜": "teleconverter attached", "减焦镜": "focal reducer attached", "偏振镜(CPL)": "circular polarizer filter (CPL)", "中性密度镜(ND)": "neutral density filter (ND)", "渐变中灰镜(GND)": "graduated neutral density filter (GND)", "紫外线滤镜(UV)": "UV filter", "星光镜": "star filter", "柔光镜": "diffusion filter, mist filter", "彩色滤镜(红)": "red color filter", "彩色滤镜(蓝)": "blue color filter", "彩色滤镜(绿)": "green color filter", "彩色滤镜(黄)": "yellow color filter", "万花筒滤镜": "kaleidoscope filter", "棱镜滤镜": "prism filter", "红外滤镜": "infrared filter (IR)", "水下滤镜": "underwater color correction filter", "防雾涂层": "anti-fog coating", "防水涂层": "hydrophobic coating", "多层镀膜": "multi-coated lens", "单层镀膜": "single-coated lens", "无镀膜镜头": "uncoated lens", "手动对焦": "manual focus", "自动对焦": "autofocus", "失焦/模糊": "out of focus, blurry", "选择性对焦": "selective focus", "无限远对焦": "focused at infinity", "超焦距": "hyperfocal distance", "对焦堆栈": "focus stacking", "呼吸效应": "focus breathing effect", "前散景": "foreground bokeh", "后散景": "background bokeh", "高光溢出": "blooming highlights", "清晰锐利": "tack sharp", "柔和细腻": "soft and gentle rendering", "高对比度": "high contrast rendering", "低对比度": "low contrast rendering", "3D立体效果": "3D stereoscopic effect", "VR180镜头": "VR180 lens", "镜头眩光": "lens ghosting", "耀斑": "flare", "彗形像差": "coma aberration", "像散": "astigmatism", "场曲": "field curvature", "球面像差": "spherical aberration", "衍射极限": "diffraction limited", "数字变焦": "digital zoom", "光学变焦": "optical zoom", "防抖开": "image stabilization on", "防抖关": "image stabilization off", "光圈优先模式": "aperture priority mode", "快门优先模式": "shutter priority mode", "手动模式": "manual mode", "程序自动": "program auto mode", "B门/长曝光": "bulb mode", "T门": "time mode",
}
FILM_TYPES = {
    "-- 无 --": "", "柯达Portra 400": "shot on Kodak Portra 400, fine grain, warm tones", "富士Provia 100F": "shot on Fuji Provia 100F, vibrant colors, high saturation", "伊尔福HP5": "shot on Ilford HP5, classic black and white, high contrast", "宝丽来": "Polaroid photo, instant film, retro look", "电影胶片": "cinematic film still, anamorphic", "褪色胶片": "faded film look, vintage colors", "Lomo相机效果": "Lomography style, high contrast, vignettes, saturated colors", "交叉冲洗": "cross-processing effect, surreal colors", "日系小清新": "Japanese photography style, airy, bright, soft colors", "湿版摄影": "wet-plate collodion photography look, antique", "CCTV监控画面": "CCTV footage style, low-res, timestamp", "8-bit像素艺术": "8-bit pixel art style", "柯达Ektar 100": "Kodak Ektar 100, ultra-fine grain, vivid colors", "柯达Tri-X 400": "Kodak Tri-X 400, grainy black and white, classic photojournalism look", "富士Velvia 50": "Fuji Velvia 50, high contrast, extreme saturation, for landscapes", "富士Superia 400": "Fuji Superia 400, cool tones, greenish cast", "Agfa Vista 200": "Agfa Vista 200, warm, reddish tones, nostalgic", "仙娜(CineStill) 800T": "CineStill 800T, tungsten balanced, halation effect on lights, cinematic night look", "红外胶片": "infrared film, false-color, dreamy landscapes", "正片(反转片)": "slide film, reversal film", "负片": "negative film", "过期胶片": "expired film look, unpredictable color shifts, increased grain", "一次性相机": "disposable camera look, harsh flash, soft focus", "大画幅相机(8x10)": "large format 8x10 camera, incredible detail, shallow depth of field", "中画幅相机(6x7)": "medium format 6x7 camera, rich tonality", "35mm胶片": "35mm film", "16mm电影胶片": "16mm film look, grainy, vintage cinema", "8mm电影胶片": "Super 8mm film look, very grainy, home movie feel", "IMAX胶片": "IMAX 70mm film, immense detail and clarity", "Technicolor电影": "Technicolor process, saturated, vibrant colors, classic Hollywood look", "黑白电影": "black and white cinematography", "有声黑白电影": "film noir cinematography", "德国表现主义": "German Expressionism style, distorted sets, strong shadows", "法国新浪潮": "French New Wave style, handheld, jump cuts", "意大利新现实主义": "Italian Neorealism style, non-professional actors, on-location shooting", "道格玛95": "Dogme 95 style, strict rules, naturalistic", "苏联蒙太奇": "Soviet Montage style, dynamic editing", "西部片风格": "Spaghetti Western style, extreme close-ups, wide shots", "恐怖片风格": "horror film style, found footage", "科幻片风格": "sci-fi film style, futuristic", "奇幻片风格": "fantasy film style, epic", "纪录片风格": "documentary style, cinéma vérité", "新闻摄影风格": "photojournalism style", "时尚摄影风格": "fashion photography style, editorial", "建筑摄影风格": "architectural photography style", "街头摄影风格": "street photography style", "体育摄影风格": "sports photography style, action frozen", "野生动物摄影": "wildlife photography style", "天文摄影": "astrophotography style", "微距摄影": "macro photography style", "航拍摄影": "aerial photography style", "水下摄影": "underwater photography style", "抽象摄影": "abstract photography style", "极简摄影": "minimalist photography style", "概念摄影": "conceptual photography style", "肖像摄影": "portrait photography style", "静物摄影": "still life photography style", "食物摄影": "food photography style", "产品摄影": "product photography style", "蓝晒法": "cyanotype process, blue and white print", "银版照相法": "daguerreotype process, mirror-like, detailed", "凹版印刷": "photogravure print look", "丝网印刷": "screenprint look", "木刻版画": "woodblock print look", "铜版画": "etching look", "石版画": "lithograph look", "水彩画": "watercolor painting style", "油画": "oil painting style", "丙烯画": "acrylic painting style", "蜡笔画": "crayon drawing style", "铅笔素描": "pencil sketch style", "炭笔素描": "charcoal sketch style", "钢笔画": "ink pen drawing style", "漫画书": "comic book art style", "动画片": "animation cel style", "定格动画": "stop-motion animation style", "粘土动画": "claymation style", "3D渲染": "3D render, CGI", "体素艺术": "voxel art style", "低多边形艺术": "low-poly art style", "故障艺术": "glitch art", "蒸汽波艺术": "vaporwave aesthetic", "赛博朋克艺术": "cyberpunk aesthetic", "蒸汽朋克艺术": "steampunk aesthetic", "柴油朋克艺术": "dieselpunk aesthetic", "原子朋克艺术": "atompunk aesthetic", "太阳朋克艺术": "solarpunk aesthetic", "生物朋克艺术": "biopunk aesthetic",
}
COLOR_PALETTES = {
    "-- 无 --": "", "单色": "monochromatic", "高饱和度": "vibrant, high saturation", "低饱和度/褪色": "desaturated, muted color palette", "暖色调": "warm color palette", "冷色调": "cool color palette", "粉彩色": "pastel color palette", "霓虹色": "neon color palette", "韦斯安德森风格": "Wes Anderson style, symmetrical, distinct color palette", "黑客帝国绿": "Matrix green color palette", "银翼杀手色调": "Blade Runner color palette, neon and dark tones", "双色调": "duotone color scheme", "三色调": "trichromatic color scheme", "黑暗学术风": "dark academia color palette, browns, grays, dark greens", "类似色": "analogous color scheme", "互补色": "complementary color scheme", "分裂互补色": "split-complementary color scheme", "矩形(四色)配色": "tetradic (rectangular) color scheme", "方形(四色)配色": "square color scheme", "高对比度": "high contrast colors", "低对比度": "low contrast colors", "黑白": "black and white", "深褐色(乌贼墨)": "sepia tone", "金色调": "golden hour palette", "蓝色调": "blue hour palette", "暮光色调": "twilight palette", "黎明色调": "dawn palette", "日落色调": "sunset palette", "彩虹色调": "rainbow palette", "金属色调": "metallic color palette (gold, silver, bronze)", "大地色调": "earth tones (browns, greens, beiges)", "海洋色调": "ocean tones (blues, greens, teals)", "森林色调": "forest tones (greens, browns)", "沙漠色调": "desert tones (oranges, yellows, browns)", "火山色调": "volcanic tones (reds, oranges, blacks)", "冰川色调": "glacial tones (whites, blues, cyans)", "城市色调": "urban color palette (grays, browns, blues)", "乡村色调": "rural color palette (greens, yellows, browns)", "复古色调": "retro color palette (e.g., 70s oranges and browns)", "80年代复古": "80s vaporwave palette (pinks, purples, teals)", "90年代复古": "90s grunge palette (muted reds, greens, browns)", "装饰艺术风格": "Art Deco color palette (gold, black, silver, bold colors)", "新艺术风格": "Art Nouveau color palette (earthy, organic colors)", "包豪斯风格": "Bauhaus color palette (primary colors: red, yellow, blue)", "波普艺术风格": "Pop Art color palette (bold, bright, contrasting colors)", "印象派风格": "Impressionist color palette (light, pastel colors)", "野兽派风格": "Fauvist color palette (intense, non-realistic colors)", "立体主义风格": "Cubist color palette (monochromatic, earthy tones)", "超现实主义风格": "Surrealist color palette (dreamlike, unexpected colors)", "极简主义风格": "minimalist color palette (neutrals, one or two accent colors)", "巴洛克风格": "Baroque color palette (rich, dramatic, dark colors)", "洛可可风格": "Rococo color palette (light, airy, pastel colors)", "哥特风格": "gothic color palette (dark, moody, black, red, purple)", "蒸汽朋克风格": "steampunk color palette (browns, brass, copper, dark red)", "赛博朋克风格": "cyberpunk color palette (neon, dark, blue, pink, purple)", "糖果色": "candy-colored palette", "宝石色": "jewel-toned palette (emerald, ruby, sapphire)", "荧光色": "fluorescent color palette", "磷光色": "phosphorescent color palette", "全息色": "holographic color palette", "热成像色": "thermal imaging color palette", "夜视绿色": "night vision green palette", "X光色": "X-ray color palette (black, white, gray)", "负片色": "inverted color palette", "故障艺术色": "glitchy color palette", "褪色/做旧": "faded, aged color palette", "手染色": "hand-tinted color palette", "水彩画": "watercolor palette", "油画色": "oil painting palette", "丙烯色": "acrylic paint palette", "蜡笔色": "crayon color palette", "彩色铅笔色": "colored pencil palette", "标记笔色": "marker pen palette", "自然光色": "natural light color palette", "人造光色": "artificial light color palette", "烛光色": "candlelight color palette", "霓虹灯色": "neon light color palette", "紫外光色": "blacklight color palette", "红灯区色": "red light district color palette", "黄金色": "golden color palette", "银色": "silver color palette", "铜色": "copper color palette", "铬色": "chrome color palette", "铁锈色": "rusty color palette", "血色": "blood-red color palette", "墨色": "inky black and white palette", "茶色": "tea-stained color palette", "咖啡色": "coffee-toned palette", "酒色": "wine-colored palette", "春天色": "spring color palette (fresh greens, pinks, yellows)", "夏天色": "summer color palette (bright blues, yellows, reds)", "秋天色": "autumn color palette (oranges, reds, browns, yellows)", "冬天色": "winter color palette (cool blues, whites, grays)",
}
COMPOSITIONS = {
    "-- 无 --": "", "三分法": "rule of thirds composition", "中心构图": "centered composition", "对称构图": "symmetrical composition", "引导线": "leading lines composition", "框架构图": "framing composition", "黄金比例": "golden ratio composition", "负空间": "negative space composition", "填充画面": "fill the frame composition", "对角线构图": "diagonal composition", "三角形构图": "triangle composition", "图案和重复": "patterns and repetition", "动态对称": "dynamic symmetry", "黄金三角": "golden triangles composition", "黄金螺旋": "golden spiral (Fibonacci spiral) composition", "不对称平衡": "asymmetrical balance", "径向平衡": "radial balance", "并置": "juxtaposition", "奇数法则": "rule of odds", "景深": "depth of field", "分层": "layering (foreground, middle ground, background)",
}

# --- 主节点预设数据 ---
STYLE_TRANSFER_PRESETS = {
    "-- 无 --": "", "梵高风格": "in the style of Vincent van Gogh", "毕加索立体主义": "in the style of Picasso's cubism", "达芬奇风格": "in the style of Leonardo da Vinci", "莫奈印象派": "in the style of Monet's impressionism", "达利超现实主义": "in the style of Salvador Dalí's surrealism", "安迪·沃霍尔波普艺术": "in the style of Andy Warhol's pop art", "草间弥生风格": "in the style of Yayoi Kusama, polka dots", "葛饰北斋浮世绘": "in the style of Hokusai's ukiyo-e", "伦勃朗光影": "in the style of Rembrandt", "卡拉瓦乔明暗对照法": "in the style of Caravaggio, chiaroscuro", "维米尔风格": "in the style of Vermeer", "弗里达·卡罗风格": "in the style of Frida Kahlo", "爱德华·蒙克表现主义": "in the style of Edvard Munch's expressionism", "古斯塔夫·克里姆特风格": "in the style of Gustav Klimt, golden", "杰克逊·波洛克滴画": "in the style of Jackson Pollock's drip painting", "马克·罗斯科色域绘画": "in the style of Mark Rothko's color field painting", "吉卜力工作室动画风格": "in the style of Studio Ghibli, Hayao Miyazaki anime", "新海诚动画风格": "in the style of Makoto Shinkai, detailed anime", "今敏动画风格": "in the style of Satoshi Kon, surreal anime", "大友克洋《阿基拉》风格": "in the style of Katsuhiro Otomo, Akira", "迪士尼经典动画": "in the style of classic Disney animation", "皮克斯3D动画": "in the style of Pixar 3D animation", "蒂姆·波顿哥特风格": "in the style of Tim Burton, gothic, whimsical", "韦斯·安德森对称美学": "in the style of Wes Anderson, symmetrical, pastel colors", "昆汀·塔伦蒂诺电影感": "in the style of a Quentin Tarantino film", "王家卫电影感": "in the style of Wong Kar-wai, neon, melancholic", "大卫·林奇超现实电影": "in the style of a David Lynch film, surreal, dreamlike", "《银翼杀手》赛博朋克": "in the style of Blade Runner, cyberpunk noir", "《黑客帝国》数字朋克": "in the style of The Matrix, digital, green tint", "《疯狂的麦克斯》废土朋克": "in the style of Mad Max, post-apocalyptic, desert punk", "《星球大战》太空歌剧": "in the style of Star Wars, space opera", "《指环王》史诗奇幻": "in the style of Lord of the Rings, epic fantasy", "《哈利·波特》魔法世界": "in the style of Harry Potter, magical realism", "《侠盗猎车手》游戏艺术": "in the style of Grand Theft Auto (GTA) game art", "《最终幻想》游戏艺术": "in the style of Final Fantasy game art", "《塞尔达传说》游戏艺术": "in the style of The Legend of Zelda game art", "《我的世界》体素艺术": "in the style of Minecraft, voxel art", "《辐射》复古未来主义": "in the style of Fallout, retrofuturism", "《生化奇兵》装饰艺术": "in the style of BioShock, Art Deco", "《赛博朋克2077》游戏艺术": "in the style of Cyberpunk 2077 game art", "《守望先锋》游戏艺术": "in the style of Overwatch game art", "《英雄联盟》游戏艺术": "in the style of League of Legends game art", "蒸汽朋克": "steampunk style", "柴油朋克": "dieselpunk style", "原子朋克": "atompunk style", "太阳朋克": "solarpunk style", "生物朋克": "biopunk style", "洛可可风格": "Rococo style", "巴洛克风格": "Baroque style", "哥特艺术": "Gothic art style", "装饰艺术": "Art Deco style", "新艺术运动": "Art Nouveau style", "包豪斯": "Bauhaus style", "极简主义": "minimalism style", "抽象表现主义": "abstract expressionism", "未来主义": "futurism", "构成主义": "constructivism", "至上主义": "suprematism", "达达主义": "Dadaism", "野兽派": "Fauvism", "点画派": "Pointillism", "象征主义": "Symbolism", "拉斐尔前派": "Pre-Raphaelite style", "古典主义": "Classicism", "新古典主义": "Neoclassicism", "浪漫主义": "Romanticism", "现实主义": "Realism", "自然主义": "Naturalism", "迷幻艺术": "psychedelic art", "低多边形艺术": "low poly art", "故障艺术": "glitch art", "蒸汽波": "vaporwave aesthetic", "像素艺术": "pixel art", "ASCII艺术": "ASCII art", "黑白漫画": "black and white manga style", "少女漫画": "shoujo manga style", "少年漫画": "shonen manga style", "美国漫画(黄金时代)": "American comic book style (Golden Age)", "美国漫画(现代)": "modern American comic book style", "欧洲漫画(丁丁历险记)": "bande dessinée style (e.g., The Adventures of Tintin)", "涂鸦艺术": "graffiti art, street art", "壁画": "mural art", "宣传海报": "propaganda poster style", "复古广告": "vintage advertisement style", "技术蓝图": "technical blueprint style", "建筑草图": "architectural sketch style", "儿童画": "child's drawing style", "蜡笔画": "crayon drawing style", "铅笔素描": "pencil sketch", "炭笔画": "charcoal drawing", "钢笔画": "ink drawing", "水彩画": "watercolor painting", "油画": "oil painting", "丙烯画": "acrylic painting", "版画": "woodblock print", "剪纸艺术": "paper cut art", "折纸艺术": "origami style", "雕塑": "sculpture style", "马赛克艺术": "mosaic art", "彩色玻璃": "stained glass window style", "纹身艺术": "tattoo art style",
}
PROPS_PRESETS = {
    "-- 无 --": "", "剑": "holding a sword", "盾": "holding a shield", "魔法书": "holding a magic book", "法杖": "holding a magic staff", "弓箭": "holding a bow and arrow", "手枪": "holding a pistol", "步枪": "holding a rifle", "激光枪": "holding a laser gun", "光剑": "holding a lightsaber", "匕首": "holding a dagger", "战斧": "holding a battle axe", "长矛": "holding a spear", "锤子": "holding a hammer", "镰刀": "holding a scythe", "鞭子": "holding a whip", "魔杖": "holding a magic wand", "水晶球": "holding a crystal ball", "药水瓶": "holding a potion bottle", "古老的卷轴": "holding an ancient scroll", "地图": "holding a map", "指南针": "holding a compass", "望远镜": "holding a telescope", "放大镜": "holding a magnifying glass", "灯笼": "holding a lantern", "火把": "holding a torch", "蜡烛": "holding a candle", "钥匙": "holding a key", "锁": "holding a lock", "时钟/怀表": "holding a clock/pocket watch", "沙漏": "holding an hourglass", "羽毛笔": "holding a quill pen", "墨水瓶": "holding an ink bottle", "书": "holding a book", "报纸": "reading a newspaper", "信件": "holding a letter", "手机": "holding a smartphone", "笔记本电脑": "using a laptop", "平板电脑": "using a tablet", "相机": "holding a camera", "麦克风": "holding a microphone", "耳机": "wearing headphones", "吉他": "playing a guitar", "小提琴": "playing a violin", "钢琴": "playing a piano", "长笛": "playing a flute", "鼓": "playing the drums", "画笔": "holding a paintbrush", "调色板": "holding a palette", "雕刻刀": "holding a carving knife", "手术刀": "holding a scalpel", "听诊器": "wearing a stethoscope", "注射器": "holding a syringe", "烧杯": "holding a beaker", "试管": "holding a test tube", "扳手": "holding a wrench", "螺丝刀": "holding a screwdriver", "电钻": "holding a power drill", "锯子": "holding a saw", "渔竿": "holding a fishing rod", "球(篮球/足球等)": "holding a ball (basketball/soccer ball etc.)", "球拍(网球/羽毛球等)": "holding a racket (tennis/badminton etc.)", "高尔夫球杆": "holding a golf club", "棒球棒": "holding a baseball bat", "橄榄球": "holding a rugby ball/football", "扑克牌": "holding playing cards", "骰子": "holding dice", "国际象棋棋子": "holding a chess piece", "魔方": "solving a Rubik's cube", "雨伞": "holding an umbrella", "手提箱": "carrying a suitcase", "背包": "wearing a backpack", "手提包": "carrying a handbag", "购物袋": "carrying shopping bags", "花束": "holding a bouquet of flowers", "单枝玫瑰": "holding a single rose", "气球": "holding a balloon", "风筝": "flying a kite", "泡泡棒": "blowing bubbles", "棒棒糖": "eating a lollipop", "冰淇淋": "eating an ice cream cone", "咖啡杯": "drinking from a coffee cup", "茶杯": "drinking from a teacup", "酒杯": "holding a wine glass", "啤酒杯": "holding a beer mug", "烟斗": "smoking a pipe", "雪茄": "smoking a cigar", "扇子": "holding a hand fan", "面具": "holding a mask", "王冠": "wearing a crown", "权杖": "holding a scepter", "宝珠": "holding an orb", "头盔": "wearing a helmet", "护目镜": "wearing goggles", "眼镜": "wearing glasses", "单片眼镜": "wearing a monocle", "项链": "wearing a necklace", "手镯": "wearing a bracelet", "戒指": "wearing a ring", "耳环": "wearing earrings", "手套": "wearing gloves", "围巾": "wearing a scarf", "帽子": "wearing a hat", "领带": "wearing a tie", "领结": "wearing a bow tie",
}
SCENE_PRESETS_DATA = {
    "-- 无 --": "", "自定义": "custom scene", "默认": "default scene",
    # 现实场景
    "舒适的客厅": "cozy living room with a fireplace", "现代化的厨房": "modern kitchen with stainless steel appliances", "阳光明媚的卧室": "sun-drenched bedroom with large windows", "凌乱的家庭办公室": "messy home office with stacks of books", "摆满植物的阳台": "balcony filled with potted plants", "后院烧烤": "backyard barbecue with friends", "儿童游乐场": "children's playground with swings and a slide", "社区游泳池": "community swimming pool on a sunny day", "车库里的乐队排练": "band practice in a garage", "阁楼储藏室": "dusty attic storage room", "地下室洗衣房": "basement laundry room", "屋顶花园": "rooftop garden with city views", "繁忙的城市街道": "busy city street with traffic and pedestrians", "拥挤的地铁车厢": "crowded subway car during rush hour", "安静的城市公园": "quiet city park with a pond and benches", "街角的咖啡店": "corner coffee shop with patrons", "人来人往的购物中心": "bustling shopping mall", "安静的图书馆阅览室": "silent library reading room", "大学校园的草坪": "university campus lawn", "农贸市场": "farmer's market with stalls of fresh produce", "海边木栈道": "beach boardwalk at sunset", "山间徒步小径": "hiking trail in the mountains", "乡村公路": "country road with fields on either side", "夜间的加油站": "gas station at night", "汽车修理厂": "auto repair shop with tools and cars", "户外篮球场": "outdoor basketball court", "足球场": "soccer field during a match", "网球场": "tennis court", "高尔夫球场": "golf course with green fairways", "保龄球馆": "bowling alley with neon lights", "电影院": "movie theater with red velvet seats", "艺术博物馆": "art museum with classical paintings", "自然历史博物馆": "natural history museum with dinosaur skeletons", "科技馆": "science museum with interactive exhibits", "水族馆": "aquarium with a large shark tank", "动物园": "zoo with various animal enclosures", "植物园温室": "botanical garden conservatory", "机场航站楼": "airport terminal with passengers", "火车站台": "train station platform", "港口的集装箱码头": "shipping container port", "工厂流水线": "factory assembly line", "建筑工地": "construction site with cranes", "医院急诊室": "hospital emergency room", "牙医诊所": "dentist's office", "法庭": "courtroom during a trial", "警察局": "police station", "消防站": "fire station", "邮局": "post office", "银行大厅": "bank lobby", "超市": "supermarket aisle", "百货公司": "department store", "书店": "bookstore with shelves of books", "唱片店": "record store with vinyls", "古董店": "antique shop filled with old items", "花店": "flower shop", "理发店": "barbershop", "美容院": "beauty salon", "健身房": "gym with workout equipment", "室内攀岩馆": "indoor rock climbing gym", "滑板公园": "skate park with ramps", "音乐节现场": "music festival crowd", "露天市场": "open-air market in a historic town square", "酒店大堂": "hotel lobby", "汽车旅馆房间": "motel room", "露营地": "campsite with a tent and campfire", "农场": "farm with a barn and animals", "葡萄园": "vineyard with rows of grapes", "海滩上的篝火晚会": "bonfire party on the beach", "灯塔": "lighthouse on a rocky coast", "谷仓舞会": "barn dance with country music", "河边钓鱼": "fishing on a riverbank", "湖上划船": "boating on a calm lake", "森林小屋": "cabin in the woods", "沙漠中的绿洲": "oasis in the desert", "冰川洞穴": "ice cave inside a glacier", "温泉": "natural hot spring", "瀑布下": "underneath a waterfall", "悬崖边": "on the edge of a cliff overlooking the ocean",
    # 幻想场景
    "繁华的东京街头": "bustling Tokyo street at night, neon signs, crowds of people", "宁静的京都寺庙": "serene Kyoto temple garden, moss, stone lanterns, autumn leaves", "赛博朋克城市": "cyberpunk city, rainy, towering skyscrapers, flying vehicles, holographic ads", "废弃的后启示录城市": "post-apocalyptic city ruins, overgrown with nature, abandoned cars", "中世纪幻想城堡": "medieval fantasy castle on a mountain, dragons flying in the sky", "魔法森林": "enchanted forest, glowing mushrooms, ancient trees with faces, ethereal mist", "蒸汽朋克实验室": "steampunk laboratory, brass and copper machinery, glowing vials, intricate clockwork", "维多利亚时代的伦敦街道": "Victorian London street, gas lamps, cobblestone, horse-drawn carriages, fog", "古埃及金字塔": "ancient Egyptian pyramids at sunset, camels, vast desert", "古罗马斗兽场": "Roman Colosseum, gladiators, cheering crowds", "未来派空间站": "futuristic space station orbiting a planet, view of Earth from window", "外星沙漠星球": "alien desert planet, two suns, strange rock formations, alien flora", "爱丽丝梦游仙境": "Alice in Wonderland, giant mushrooms, talking flowers, whimsical", "克苏鲁神话中的沉没都市": "sunken city of R'lyeh, non-euclidean geometry, Cthulhu mythos", "天空之城": "floating city in the sky, waterfalls cascading down, fantastical architecture", "地心世界": "journey to the center of the earth, giant crystals, prehistoric creatures", "无限的白色空间": "infinite white void, minimalist, empty space", "分形的超现实景观": "fractal surreal landscape", "镜子大厅": "hall of mirrors, endless reflections", "糖果王国": "kingdom made of candy and sweets", "发条城市": "clockwork city, everything is made of gears and cogs", "水晶洞穴": "crystal cave, glowing crystals", "被遗忘的亚特兰蒂斯": "the lost city of Atlantis, underwater ruins", "世界树": "at the base of the world tree, Yggdrasil", "奥林匹斯山": "Mount Olympus, home of the Greek gods", "戴森球": "Dyson sphere, megastructure enclosing a star", "环形世界": "Ringworld, artificial ring orbiting a star", "黑洞的事件视界": "at the event horizon of a black hole", "多重宇宙的交汇点": "nexus of the multiverse, portals to other worlds", "梦境": "a surreal dreamscape", "天堂": "heaven, clouds, gates of pearl, angels", "地狱": "hell, fire, brimstone, demons",
}
LIGHTING_PRESETS_DATA = {
    "-- 无 --": "", "自定义": "custom lighting", "默认": "default lighting", "伦勃朗光": "Rembrandt lighting, dramatic, chiaroscuro", "蝴蝶光": "Butterfly lighting, glamorous, beauty shot", "黄金时刻": "Golden hour lighting, warm, soft, long shadows", "蓝色时刻": "Blue hour lighting, cool tones, serene", "电影黑色调": "Film noir style, low-key, deep shadows", "赛博朋克霓虹光": "Cyberpunk neon lighting, vibrant, reflective", "水下光线": "Underwater caustics, light rays", "魔法光芒": "Magical aura, enchanted glow", "强烈闪光灯": "Harsh on-camera flash, direct", "丁达尔效应/耶稣光": "Tyndall effect, god rays, sunbeams", "柔和的窗光": "soft window light", "烛光": "candlelight, intimate, warm", "舞台聚光灯": "stage spotlight", "篝火": "campfire light", "月光": "moonlight, cool, silvery", "恐怖顶光": "horror movie top light", "高调光": "high-key lighting, bright, few shadows", "低调光": "low-key lighting, dark, high contrast", "轮廓光/边缘光": "rim lighting, backlighting", "剪影": "silhouette", "投影光": "light from a projector", "生物荧光": "bioluminescent glow", "神圣光辉": "divine glow", "镜头光晕": "lens flare", "爆炸光": "explosion light flash", "火焰光": "firelight", "激光": "laser beams", "黑光灯/紫外光": "blacklight, UV light", "日落": "sunset glow", "黎明": "dawn light", "阴天": "overcast day, diffused light", "雨天反射": "rainy day reflections on wet streets", "雾中光": "light diffused by fog", "闪电": "lightning flash", "工作室柔光箱": "studio softbox lighting", "环形闪光灯": "ring flash, shadowless", "车头灯": "car headlights at night", "电视/屏幕光": "light from a screen", "熔岩光": "lava glow", "星光": "starlight", "环形光": "loop lighting", "分割光": "split lighting", "眼神光": "catchlight in eyes", "硬光": "hard light, sharp shadows", "柔光": "soft light, diffused shadows", "顺光": "front lighting", "侧光": "side lighting", "逆光": "backlighting", "顶光": "top lighting", "底光": "underlighting", "暖色温": "warm color temperature", "冷色温": "cool color temperature", "中性色温": "neutral color temperature", "双色光": "duotone lighting (e.g., blue and pink)", "三点布光": "three-point lighting (key, fill, back)", "伦勃朗三角": "Rembrandt triangle on cheek", "派拉蒙光": "Paramount lighting (same as butterfly)", "宽光": "broad lighting", "窄光": "short lighting", "负补光": "negative fill, increasing shadows", "反光板补光": "reflector fill light", "环境光": "ambient light", "自然光": "natural light", "人造光": "artificial light", "闪烁的光": "flickering light", "脉冲光": "pulsing light", "移动的光": "moving light", "彩色凝胶光": "colored gel lighting", "图案片/Gobo": "gobo light patterns", "体积光": "volumetric lighting, light beams visible in air", "薄雾中的光": "light in haze or mist", "烟雾中的光": "light in smoke", "灰尘中的光": "light beams in dusty air", "水下光束": "underwater light beams", "极光": "aurora borealis lighting", "闪烁的霓虹灯招牌": "flickering neon sign", "迪斯科球": "disco ball lighting", "频闪灯": "strobe light", "警车灯": "police car lights", "救护车灯": "ambulance lights", "灯塔光束": "lighthouse beam", "手电筒光束": "flashlight beam", "探照灯": "searchlight", "日食光": "solar eclipse lighting", "月食光": "lunar eclipse lighting", "烟花": "fireworks lighting", "仙女棒": "sparkler light", "电脑屏幕的冷光": "cool glow from a computer monitor", "手机屏幕的光": "glow from a phone screen", "壁炉的暖光": "warm glow from a fireplace", "熔炉的光": "glow from a furnace", "焊接电弧光": "welding arc light", "鬼火/磷光": "will-o'-the-wisp, phosphorescence", "幽灵光": "ghostly, ethereal light", "万花筒光": "kaleidoscope lighting", "全息投影光": "holographic projection light", "故障艺术光": "glitchy, distorted light", "像素化光": "pixelated light", "能量光环": "energy aura", "气场光": "chi/qi energy glow", "魔法符文发光": "glowing magical runes",
}
POSE_PRESETS_DATA = {
    "-- 无 --": "", "自定义": "custom pose", "默认姿势": "default pose", "自信地站立": "standing confidently, hands on hips", "双臂交叉": "arms crossed", "奔跑中": "dynamic running pose", "跳跃瞬间": "energetic mid-jump pose", "回眸一笑": "looking back over the shoulder with a smile", "战斗姿态": "fighting stance", "超级英雄落地": "superhero landing pose", "沉思者": "The Thinker pose", "优雅地跳舞": "dancing gracefully", "躺在草地上": "lying on the grass, relaxed", "坐着": "sitting", "蹲着": "crouching", "跪着": "kneeling", "行走": "walking", "鞠躬": "bowing", "敬礼": "saluting", "祈祷": "praying", "拥抱": "hugging", "指向": "pointing", "阅读": "reading a book", "写作": "writing", "绘画": "painting", "烹饪": "cooking", "弹吉他": "playing a guitar", "拉小提琴": "playing a violin", "唱歌": "singing", "驾驶": "driving", "骑行": "riding a bike", "游泳": "swimming", "攀爬": "climbing", "射箭": "aiming a bow and arrow", "举重": "lifting weights", "瑜伽姿势": "yoga pose", "芭蕾舞姿": "ballet pose", "躲藏": "hiding", "窥视": "peeking", "伸懒腰": "stretching", "打电话": "talking on the phone", "使用电脑": "using a laptop", "喝水": "drinking", "吃饭": "eating", "悬浮": "floating, levitating", "投掷": "throwing", "接住": "catching", "跌倒": "falling", "领导者姿势": "leader pose, commanding presence", "魔法师施法": "casting a spell", "武士拔刀": "samurai drawing a katana", "侦探观察": "detective observing clues", "宇航员失重漂浮": "astronaut floating in zero-gravity", "随意站立": "standing casually", "倚靠": "leaning against a wall", "盘腿坐": "sitting cross-legged", "侧卧": "lying on side", "俯卧": "lying on stomach", "仰卧": "lying on back", "单脚站立": "balancing on one leg", "滑板": "skateboarding", "冲浪": "surfing", "滑雪": "skiing", "单板滑雪": "snowboarding", "打篮球": "playing basketball", "踢足球": "playing soccer", "打网球": "playing tennis", "打高尔夫": "swinging a golf club", "拳击": "boxing stance", "击剑": "fencing stance", "冥想": "meditating", "指挥": "conducting an orchestra", "拍照": "taking a photo", "检查手表": "checking watch", "系鞋带": "tying shoelaces", "背包客": "hiking with a backpack", "演讲": "giving a speech", "耳语": "whispering", "欢呼": "cheering", "挥手": "waving", "握手": "shaking hands", "敬酒": "toasting with a glass", "打字": "typing on a keyboard", "玩游戏": "playing a video game", "拼图": "doing a puzzle", "园艺": "gardening", "钓鱼": "fishing", "修理": "fixing something", "建筑": "building something", "跳水": "diving", "体操": "gymnastics pose", "武术姿势": "martial arts pose", "溜冰": "ice skating", "轮滑": "roller skating", "荡秋千": "swinging on a swing", "放风筝": "flying a kite", "吹泡泡": "blowing bubbles", "闻花香": "smelling a flower", "躲雨": "sheltering from rain", "晒太阳": "sunbathing", "颤抖": "shivering from cold", "擦汗": "wiping sweat", "思考": "thinking, chin in hand", "胜利姿势": "victory pose", "失败姿势": "defeated pose", "投降姿势": "surrendering, hands up", "被逮捕姿势": "being arrested, hands behind back", "芭蕾舞阿拉贝斯克": "ballet arabesque", "瑜伽下犬式": "yoga downward-facing dog", "瑜伽树式": "yoga tree pose", "太极拳姿势": "Tai Chi pose",
}

# --- 新增Kontext官方预设 ---
KONTEX_PRESETS_PROMPTS = {
    # 基础编辑
    "基础-传送": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将主体传送到随机的地点、场景和/或风格中。在各种完全出乎意料的场景中对其进行重新情境化。不要指示替换或转换主体，只改变背景/场景/风格/服装/配饰/背景等。",
    "基础-移动相机": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n移动相机以展示场景的新面貌。根据场景提供截然不同的相机移动方式（例如：相机现在呈现房间的俯视图；人物的侧面肖像视图等）。",
    "基础-重新打光": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n为图像建议新的照明设置。提出各种照明场景和设置，重点关注专业的工作室照明。建议应包含戏剧性的色彩变化、不同的一天中的时间、去除或加入一些新的自然光等。",
    "基础-缩放": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n缩放图像的{{SUBJECT}}。如果提供了主体，就对其进行缩放。否则，对图像的主要主体进行缩放。提供不同程度的缩放。",
    "基础-上色": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n为图像上色。提供不同的色彩风格/修复指导。",
    "基础-移除文字": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n从图像中移除所有文字。",
    "基础-移除家具": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n从图像中移除所有家具和所有电器。如果存在灯光、地毯、窗帘等，明确提及要移除它们。",

    # 人像摄影
    "人像-企业商务照": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物转换为专业的企业商务头像。采用蝴蝶光或伦勃朗光，使面部光线均匀柔和且富有立体感。背景应为纯灰色、白色或模糊的现代办公环境。人物表情应显得自信、友好。",
    "人像-复古胶片肖像": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为复古胶片风格的肖像照。模仿一种特定的胶片风格，如Kodak Portra 400的暖色调和细腻颗粒感，或Ilford HP5的高对比度黑白效果。光线应柔和，如窗边的自然光，营造出怀旧氛围。",
    "人像-时尚大片": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物打造成高端时尚杂志的内页大片。采用戏剧性的高对比度光线（如分割光），让人物摆出充满张力与表现力的姿态。服装和妆容应随机选择一种前卫且有设计感的风格。",
    "人像-新生儿艺术照": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的婴儿转换为温馨的新生儿艺术照。例如将婴儿被柔软的羊毛毯子包裹，或放置在可爱的道具中。采用非常柔和、均匀的散射自然光，色调温暖、纯净。",
    "人像-孕妇摄影": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为唯美的孕妇摄影作品。使用侧光或逆光来勾勒出孕妇的身体轮廓。光线应柔和，背景简洁（如纯色背景或逆光的窗户），整体氛围应宁静而充满母性光辉。",
    "人像-运动员肖像": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物塑造为充满力量感的运动员肖像。使用硬质的、高对比度的灯光（如边缘光）来凸显肌肉线条和汗水。背景可以是体育场馆或带有动态模糊的竞技背景，以增强动感。",
    "人像-音乐家宣传照": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物塑造为音乐家宣传照。让人物手持乐器，并使用聚焦的舞台聚光灯或有氛围的色光（如蓝色或紫色）。背景可以是黑暗的舞台或充满设备的录音棚，营造专业氛围。",
    "人像-Cosplay角色照": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物转换为专业的Cosplay角色照片。根据角色设定，使用戏剧性的光效（如魔法光芒、火焰光）和符合世界观的背景（如奇幻森林、赛博城市），重点突出服装和道具的细节与质感。",
    "人像-毕业照精修": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将一张普通的毕业照精修为专业肖像。优化肤色，增加眼神光，并将背景替换为简洁的书架或校园风景。可以考虑添加柔和的丁达尔效应光线，营造出明亮、积极的氛围。",
    "人像-情侣写真": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为浪漫的情侣写真风格。使用黄金时刻的暖色调光线，让人物姿态亲密自然。背景可以是海滩、公园或城市夜景等浪漫场景，并加入美丽的散景效果。",

    # 产品摄影
    "产品-珠宝微距": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的物品转换为高端珠宝的微距特写。使用微距镜头，将焦点精确对在宝石的刻面上。用多点布光来突出其火彩和金属的光泽。背景可随机选择深色天鹅绒或纯黑/白亚克力板等，以突显主体。",
    "产品-美食俯拍": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的食物转换为流行的美食俯拍（Flat Lay）照片。相机应垂直向下，所有食材和餐具都经过精心摆盘，色彩鲜艳。光线需明亮均匀，无明显阴影，营造出干净、诱人的视觉效果。",
    "产品-汽车广告": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的汽车转换为动感的汽车广告大片。让车身呈现流动的光影，背景带有运动模糊，地面有水的反射。整体应充满速度感和高级感。",
    "产品-护肤品静物": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为护肤品静物广告。例如让瓶身带有凝结的水珠，周围随机搭配相关的植物成分（如绿茶、芦荟）。背景纯净，光线干净明亮，营造出清新、自然、科学的感觉。",
    "产品-电子产品": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为富有科技感的电子产品宣传图。将产品置于简洁的几何背景上，可以有电路或数据流动的光效环绕。使用冷色调灯光和高光来凸显产品的现代设计感。",
    "产品-奢侈品手表": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为奢侈品手表的广告特写。聚焦于表盘的精细工艺，完美呈现金属和皮革的质感。光影对比应强烈，营造出尊贵和永恒的感觉。",
    "产品-运动鞋广告": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的鞋子转换为充满活力的运动鞋广告。让鞋子处于运动状态（如跳跃、奔跑），周围可以有飞溅的水花或尘土等动态元素。光线应硬朗，色彩饱和度高，充满活力。",
    "产品-香水广告": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为富有想象力的香水广告。让瓶身周围环绕着与其香调相关的随机抽象元素（如花瓣、水果、木质纹理）。光线应梦幻，色彩浪漫，引人遐想。",
    "产品-家具展示": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的家具放置在一个精心设计的室内场景中进行展示。模拟自然光从窗户射入，照亮家具的材质和细节。整体家居风格应协调统一，可随机选择一种（如北欧、日式、工业风）。",

    # 创意与艺术
    "创意-电影海报": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将此图像制作成以图像中的主体为主要角色的电影海报。选择一个随机类型（动作、喜剧、恐怖等），使其看起来像电影海报。如果用户提供了标题 {{TITLE}}，请使用它，否则根据图像编造一个。确保标题有风格，并添加一些宣传语、引语等电影海报常见文字。",
    "创意-卡通化": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将此图像卡通化。包含一个独特的风格、文化或时代的参考（例如：90年代的漫画、粗线条、皮克斯3D风格等）。",
    "创意-专辑封面": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转变为一张专辑封面。构思一个随机的音乐流派（如独立摇滚、电子、民谣、嘻哈），并设计一个符合该流派的专辑封面。你需要添加虚构的艺术家名字和专辑标题，并采用独特的排版和布局。",
    "创意-游戏角色卡": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的人物设计成一个游戏角色选择卡。为其设定一个随机的职业（如法师、战士、盗贼、工程师），并添加角色名称、等级、关键属性（如力量、智力、敏捷）和一句标志性口号。整体设计需要有游戏UI的质感。",
    "创意-像素艺术化": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像转换为像素艺术风格。生成一个独特的像素艺术版本，可以参考特定游戏时代（如8位、16位）或特定风格（如《星露谷物语》）。",
    "创意-蒸汽波风格": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the image into a vaporwave aesthetic. Blend retro elements from the 80s and 90s with surreal imagery, neon colors, grid patterns, palm trees, and glitch effects, creating a dreamy, nostalgic visual experience.",
    "创意-双重曝光": "你是一名富有创意的提示工程师。你的任务是分析提供的图像，并生成恰好1条独特的图像转换指令。\n\n简要说明：\n将图像中的主体与一个随机的自然景观（如森林、星空、海洋、山脉）进行双重曝光融合。使主体的轮廓与景观的纹理和形状巧妙结合，创造出诗意和超现实的视觉效果。",
    "创意-低多边形(Low-Poly)": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nConvert the image into a low-polygon (Low-Poly) art style. Simplify the shapes and colors in the image into a network of geometric polygons, creating a modern, abstract, and sculptural visual effect.",
    "创意-水彩飞溅": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the image into a vibrant watercolor painting style with randomly colored splashes and ink effects. The subject should blend naturally with the background, with soft edges, flowing colors, full of artistic sense.",
    "创意-霓虹化": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the outline of the subject in the image or key elements into glowing neon tubes. The background should be dark to highlight the vibrant neon colors and glow.",
    "创意-科幻角色": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the person in the image into a sci-fi character. Add random sci-fi elements to them, such as cybernetic enhancements, glowing outfits or holographic interfaces. The background should be a futuristic city or spaceship interior.",
    "创意-奇幻生物": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the animal or person in the image into a fantasy creature. Add random fantasy features to them, such as dragon scales, elven ears, glowing runes or magic effects.",
    "创意-技术蓝图": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the object or building in the image into a technical blueprint style. Lines should be white or blue, the background deep blue, and add random dimensions and technical annotations to create a professional design feel.",
    "创意-复古海报": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the image into a 1950s style vintage advertisement poster. Use faded warm tones, paired with handwritten artistic fonts and a random nostalgic slogan.",
    "创意-剪纸艺术": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the image into traditional Chinese paper-cut art style. The subject and background should consist of intricate red or colorful paper-cut patterns with elaborate hollow-out effects.",
    "创意-涂鸦艺术": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransform the image into graffiti art style. Add bold, vibrant spray-paint-like textures and random urban street art elements to the subject and background.",
    
    "创意-姿势克隆": ("你是一位顶级的多模态提示工程师，你的任务是根据用户的意图，为图像编辑模型生成一条【极其精确且详细】的指令。\n\n"
                 "### 核心任务：姿势克隆\n\n"
                 "**输入图像的角色定义 (重要！)**\n"
                 "你将按固定顺序收到两张图片：\n"
                 "1.  **第一张图 (来自`视觉提示图像`接口)**: 这是【姿势参考图】。它【唯一】的作用是提供一个精确的姿势。\n"
                 "2.  **第二张图 (来自`kontext预设模式参考图`接口)**: 这是【源图】。这是需要被编辑的图像，图中的人物是我们的【目标人物】。\n\n"
                 "**你的思考与执行流程 (必须严格遵守):**\n\n"
                 "**第一步：【深度姿势分析】**\n"
                 "-   **彻底观察第一张图 (姿势参考图)**。\n"
                 "-   在你的内部思考中，用【极其详细】的自然语言，像一个专业的动画师或人体工学专家一样，分解并描述这个姿势。不要遗漏任何细节。\n"
                 "-   **分析要点**: \n"
                 "    -   **重心和站姿**: 身体重心在哪条腿上？双腿是并拢、分开，还是前后站立？膝盖是弯曲还是伸直？\n"
                 "    -   **躯干**: 脊柱是笔直、弯曲，还是S形扭转？肩膀是否水平？\n"
                 "    -   **手臂和手**: 每只手臂的位置和角度？手肘的弯曲程度？手在做什么（叉腰、下垂、上举）？手掌和手指的形态是怎样的（张开、握拳、放松）？\n"
                 "    -   **头部和视线**: 头的朝向？是倾斜、旋转，还是正直？视线看向哪里？\n\n"
                 "**第二步：【指令合成】**\n"
                 "-   现在，将你在第一步中分析出的【详细姿势描述】转化为一条给图像模型的最终指令。\n"
                 "-   这条指令的【核心目的】是：让【第二张图 (源图)】中的【目标人物】，完美复刻这个姿势。\n"
                 "-   **最重要的约束**: 指令必须【强制要求】保留【源图】中人物的所有其他特征，包括但不限于：**脸部样貌、身份、发型、服装、配饰、以及图像的整体背景、光线和风格**。唯一要改变的就是姿势。\n\n"
                 "**最终输出格式:**\n"
                 "你的最终输出【必须】是一个无其他文本的、格式正确的 JSON 对象，包含 'zh' 和 'en' 两个键。\n\n"
                 "**高质量输出示例:**\n"
                 "```json\n"
                 "{\n"
                 '  "zh": "保持源图中人物的所有特征（样貌、服装、背景）不变，将她的姿势精确地修改为：身体重心完全落在笔直的右腿上，左腿放松地向前弯曲；左手手背有力地叉在腰部，手肘向外；右臂则完全放松地自然垂于身体右侧；上半身保持正直，头部和视线都直接朝向正前方。",\n'
                 '  "en": "Keep all features of the person in the source image (appearance, clothing, background) unchanged, but precisely modify her pose to: body weight fully on the straight right leg, left leg relaxed and bent forward; left hand is firmly on the hip with the back of the hand, elbow pointing outwards; right arm hangs naturally and relaxed at her side; the torso remains upright, with both head and gaze directed straight ahead."\n'
                 "}\n"
                 "```\n\n"
                 "现在，请严格按照以上逻辑和格式要求，处理用户提供的两张图片."),

    # 生活与娱乐
    "生活-更换发型": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nChange the subject's hairstyle. Suggest a random but suitable new hairstyle, style or color that looks natural and coordinated.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-变身健身达人": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nDramatically increase the muscle mass of the subject while maintaining the same pose and background. Visually exaggerate the subject's biceps, abs, triceps, etc. The clothing can be changed to better showcase this excessively developed, exaggerated physique.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-室内设计": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nYou are an interior designer. Redesign the interior decoration of this image. Imagine a brand new design style (such as Nordic minimalism, industrial style, bohemian, etc.) and lighting setup that matches the room structure, but ensure the room's structure (windows, doors, walls, etc.) remains unchanged.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-更换服装": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nChange the outfit of the person in the image to a completely new one. According to the person's temperament and scene, randomly select a style of clothing (such as casual, formal, sporty, vintage) and describe in detail its style, color and material.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-添加宠物": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nAdd a cute pet to the image. Randomly select a pet (such as a kitten, puppy, rabbit), and let it interact naturally with the scene and person, for example curling up on the person's lap, or curiously looking at some object.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-季节变换": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nChange the season in the image. For example, turn a summer park scene into a snow-covered winter landscape, or transform an autumn street into a spring scene blooming with flowers. The vegetation, lighting and weather effects need to be changed accordingly.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-时间旅行": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTransport the person and scene to another era. For example, transport a person on a modern street to the 1920s jazz age, or to a cyberpunk world full of futuristic technology. The person's clothing and surrounding environment need to be creatively changed accordingly.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-添加纹身": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nAdd a uniquely styled tattoo to the person in the image. Randomly select a tattoo style (such as Japanese traditional, tribal totems, realistic, watercolor), and apply it naturally to a designated body part of the person.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "生活-制作表情包": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nTurn the image into a fun meme. Analyze the person's expression and movements, and pair it with a random, humorous and fitting text. The text should use prominent font and colors, placed at the top or bottom of the image.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",

    # 专业工具与修复
    "修复-老照片修复": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nRestore a faded, scratched or stained old photo. Remove all flaws, restore its original contrast and clarity, but keep its retro tone and texture, making it look renewed but not losing its age.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "修复-提高分辨率": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nIncrease the overall resolution and clarity of the image. Sharpen details, reduce noise and blur, making the image look clearer and more delicate, as if shot with a higher quality camera.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "修复-色彩校正": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nPerform professional color correction on the image. Adjust white balance to make colors look more natural and balanced. Correct color cast issues and enhance color vibrancy without changing the original color scheme.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "修复-移除指定物体": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nRemove {{SUBJECT}} from the image. Remove the designated object and seamlessly fill the area with the surrounding environment, making it look as if it never existed. If no subject is specified, remove a secondary, distracting object.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "修复-改变景深": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nChange the depth of field in the image. Blur the background or foreground to highlight the subject, creating a shallow depth of field effect similar to a large aperture lens, and randomly specify a bokeh style (such as circular, swirled).\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
    "修复-光线均衡": "你是一名富有创意的提示工程师。你的任务 is to analyze the provided image, and generate precisely 1 unique image transformation instruction.\n\nBrief Instructions:\nBalance the lighting in the image. Brighten overly dark shadow areas while restoring details in overexposed highlights, making the light distribution across the entire photo more even and natural, enhancing overall dynamic range.\n\nYour response must be a single, complete, concise instruction directly usable by an AI image editor. Do not add any conversational text, explanations, or content deviation; only include this 1 instruction.",
}

# --------------------------------------------------------------------------------
# 节点 1: NakuNode 专业摄影参数
# --------------------------------------------------------------------------------
class PhotographyParametersNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "相机视角": (["-- 无 --", "随机"] + list(CAMERA_ANGLES.keys()),),
                "镜头与光圈": (["-- 无 --", "随机"] + list(LENS_AND_APERTURE.keys()),),
                "胶片与风格": (["-- 无 --", "随机"] + list(FILM_TYPES.keys()),),
                "色彩与色调": (["-- 无 --", "随机"] + list(COLOR_PALETTES.keys()),),
                "构图方式": (["-- 无 --", "随机"] + list(COMPOSITIONS.keys()),),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("摄影参数",)
    FUNCTION = "generate_params"
    CATEGORY = "NakuNode/参数化"

    def generate_params(self, **kwargs):
        params = []
        data_map = {
            "相机视角": CAMERA_ANGLES, "镜头与光圈": LENS_AND_APERTURE,
            "胶片与风格": FILM_TYPES, "色彩与色调": COLOR_PALETTES,
            "构图方式": COMPOSITIONS
        }
        for key, value in kwargs.items():
            if value == "随机":
                params.append(get_random_value(data_map[key], ["-- 无 --", "随机"]))
            elif value != "-- 无 --":
                params.append(data_map[key].get(value, ""))
        return (", ".join(filter(None, params)),)

# --------------------------------------------------------------------------------
# 节点 2: NakuNode 人像参数
# --------------------------------------------------------------------------------
class PortraitParametersNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "国籍": (["-- 无 --", "随机"] + list(NATIONALITY_PRESETS.keys()),),
                "肤色": (["-- 无 --", "随机"] + list(SKIN_COLOR_PRESETS.keys()),),
                "性别": (["-- 无 --", "随机"] + list(GENDER_PRESETS.keys()),),
                "年龄": (["-- 无 --", "随机"] + list(AGE_PRESETS.keys()),),
                "体型": (["-- 无 --", "随机"] + list(BODY_TYPE_PRESETS.keys()),),
                "服饰": (["-- 无 --", "随机"] + list(CLOTHING_PRESETS.keys()),),
                "面部轮廓": (["-- 无 --", "随机"] + list(FACE_SHAPES.keys()),),
                "眼型": (["-- 无 --", "随机"] + list(EYE_TYPES.keys()),),
                "眼球颜色": (["-- 无 --", "随机"] + list(EYE_COLORS.keys()),),
                "表情": (["-- 无 --", "随机"] + list(EXPRESSIONS.keys()),),
                "鼻型": (["-- 无 --", "随机"] + list(NOSE_TYPES.keys()),),
                "唇形": (["-- 无 --", "随机"] + list(LIP_SHAPES.keys()),),
                "发型": (["-- 无 --", "随机"] + list(HAIR_STYLES.keys()),),
                "发色": (["-- 无 --", "随机"] + list(HAIR_COLORS.keys()),),
                "皮肤质感": (["-- 无 --", "随机"] + list(SKIN_TEXTURES.keys()),),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("人像参数",)
    FUNCTION = "generate_params"
    CATEGORY = "NakuNode/参数化"

    def generate_params(self, **kwargs):
        params = []
        data_map = {
            "国籍": NATIONALITY_PRESETS, "肤色": SKIN_COLOR_PRESETS,
            "性别": GENDER_PRESETS, "年龄": AGE_PRESETS, "体型": BODY_TYPE_PRESETS, "服饰": CLOTHING_PRESETS,
            "面部轮廓": FACE_SHAPES, "眼型": EYE_TYPES, "眼球颜色": EYE_COLORS,
            "表情": EXPRESSIONS, "鼻型": NOSE_TYPES, "唇形": LIP_SHAPES,
            "发型": HAIR_STYLES, "发色": HAIR_COLORS, "皮肤质感": SKIN_TEXTURES
        }
        for key, value in kwargs.items():
            if value == "随机":
                params.append(get_random_value(data_map[key], ["-- 无 --", "随机"]))
            elif value != "-- 无 --":
                params.append(data_map[key].get(value, ""))
        return (", ".join(filter(None, params)),)

# --------------------------------------------------------------------------------
# 节点 3: NakuNode 道具预设
# --------------------------------------------------------------------------------
class PropsPresetsNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "道具预设": (["-- 无 --", "随机"] + list(PROPS_PRESETS.keys()),),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("道具提示词",)
    FUNCTION = "get_preset"
    CATEGORY = "NakuNode/参数化"

    def get_preset(self, 道具预设):
        if 道具预设 == "随机":
            return (get_random_value(PROPS_PRESETS, ["-- 无 --", "随机"]),)
        elif 道具预设 == "-- 无 --":
            return ("",)
        return (PROPS_PRESETS.get(道具预设, ""),)

# --------------------------------------------------------------------------------
# 节点 4: NakuNode Kontext/QWEN 提示词生成器 (主节点)
# --------------------------------------------------------------------------------
class KontextPromptGeneratorNode:
    @classmethod
    def INPUT_TYPES(cls):
        instructions = ("操作说明:\n"
                        "- **无**: 选择此项后，节点将不调用AI，而是从'LLM指令'端口输出完整的指令，供您连接本地LLM等使用。\n"
                        "- **内置模型**: 可用于所有模式，但会**忽略**所有图像输入，仅处理文本指令。适合纯文本任务或在预设模式下生成创意文本。\n"
                        "- **中文开关**: 可选择只生成英文提示词以节省Tokens。\n"
                        "- **工作模式**: “参数化”用于手动细节控制，“Kontext预设”用于AI半自动生成。\n"
                        "- **优先级**: 自定义输入框 > 下拉预设 > “编辑描述”。“保留”选项拥有最高优先级。")
        return {
            "required": {
                "操作说明": ("STRING", {"multiline": True, "default": instructions, "dynamicPrompts": False}),
                "生成中文提示词": ("BOOLEAN", {"default": True}),
                "工作模式": (["参数化模式", "Kontext官方预设模式"],),
                "AI服务商": (["无", "内置模型", "Gemini", "智谱AI (Zhipu)", "OpenRouter", "硅基流动 (Silicon Flow)"],),
                "Gemini_API密钥": ("STRING", {"multiline": False, "default": "在此输入您的Gemini API密钥"}),
                "智谱_API密钥": ("STRING", {"multiline": False, "default": "在此输入格式为 id.secret 的Zhipu API Key"}),
                "OpenRouter_API密钥": ("STRING", {"multiline": False, "default": "在此输入您的OpenRouter API密钥"}),
                "硅基流动_API密钥": ("STRING", {"multiline": False, "default": "在此输入您的硅基流动 API密钥"}),
                "Kontext官方预设": (list(KONTEX_PRESETS_PROMPTS.keys()),),
                "kontext预设种子": ("INT", {"default": 0, "min": -1, "max": 0xffffffffffffffff}),
                "编辑描述_可选细节": ("STRING", {"multiline": True, "default": ""}),
                "风格转换": (["-- 无 --", "随机"] + list(STYLE_TRANSFER_PRESETS.keys()), ),
                "场景预设": (["-- 无 --", "随机"] + list(SCENE_PRESETS_DATA.keys()), ),
                "姿势预设": (["-- 无 --", "随机"] + list(POSE_PRESETS_DATA.keys()), ),
                "光影预设": (["-- 无 --", "随机"] + list(LIGHTING_PRESETS_DATA.keys()), ),
                "任务类型": (["综合编辑", "文本编辑", "背景/环境编辑", "添加物体/人物", "移除物体/人物", "替换物体/人物"],),
            },
            "optional": {
                "视觉提示图像": ("IMAGE", ),
                "kontext预设模式参考图": ("IMAGE",),
                "自定义风格": ("STRING", {"multiline": False, "default": ""}),
                "自定义场景": ("STRING", {"multiline": False, "default": ""}),
                "自定义姿势": ("STRING", {"multiline": False, "default": ""}),
                "自定义光影": ("STRING", {"multiline": False, "default": ""}),
                "补充提示词 (可选)": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "自定义人像参数": ("STRING", {"forceInput": True}),
                "自定义摄影参数": ("STRING", {"forceInput": True}),
                "道具_可选": ("STRING", {"forceInput": True}),
                "保留脸部和身份": ("BOOLEAN", {"default": True}), "保留姿势和体态": ("BOOLEAN", {"default": True}),
                "保留服装和配饰": ("BOOLEAN", {"default": True}), "保留表情": ("BOOLEAN", {"default": True}),
                "保留光线和构图": ("BOOLEAN", {"default": True}), "保留背景": ("BOOLEAN", {"default": True}),
                "保留相机角度": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("提示词 (中文)", "prompt (english)", "LLM指令")
    FUNCTION = "generate_prompt"
    CATEGORY = "NakuNode"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return time.time()

    def tensor_to_base64(self, image_tensor):
        if image_tensor is None: return None
        i = 255. * image_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8).squeeze())

        MAX_DIMENSION = 1024
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
            print(f"[NakuNode Kontext] Image resized to {img.width}x{img.height} to prevent API errors.")

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def generate_zhipu_token(self, apikey_with_secret):
        try:
            id, secret = apikey_with_secret.split('.')
            payload = {"api_key": id, "exp": int(time.time() * 1000) + 3600000, "timestamp": int(time.time() * 1000)}
            return jwt.encode(payload, secret, algorithm="HS256", headers={"alg": "HS256", "sign_type": "SIGN"})
        except Exception as e:
            raise Exception(f"生成Zhipu Token失败: {e}。请检查API密钥格式。")

    def get_output_format_instruction(self, generate_chinese):
        if generate_chinese:
            return "\n\n你的最终输出【必须】是一个无其他文本的、格式正确的 JSON 对象。该对象必须包含两个键： 'zh' (生成的中文指令) 和 'en' (对应的、流畅准确的英文翻译)。"
        else:
            return "\n\n你的最终输出【必须】是一个无其他文本的、格式正确的 JSON 对象。该对象必须【只】包含一个键： 'en' (生成的英文指令)。"

    def generate_prompt(self, 工作模式, AI服务商, Gemini_API密钥, 智谱_API密钥, OpenRouter_API密钥, 硅基流动_API密钥, Kontext官方预设, kontext预设种子, 编辑描述_可选细节, 风格转换, 场景预设, 姿势预设, 光影预设, 任务类型, 生成中文提示词, **kwargs):
        parts = []

        has_visual_prompt = kwargs.get("视觉提示图像") is not None
        has_kontext_ref = kwargs.get("kontext预设模式参考图") is not None
        is_vision_task = has_visual_prompt or has_kontext_ref

        if AI服务商 == "无" and is_vision_task:
            raise ValueError("错误：“无”AI服务商模式不支持图像输入。请连接一个能够处理图像的AI服务商（如Gemini, OpenRouter等），或移除图像输入以生成LLM指令。")

        if kontext预设种子 == -1:
            seed = random.randint(0, 0xffffffffffffffff)
        else:
            seed = kontext预设种子

        def get_final_value(custom_key, preset_key, preset_dict, preset_value):
            custom_value = kwargs.get(custom_key, "").strip()
            if custom_value:
                return custom_value
            if preset_value == "随机":
                return get_random_value(preset_dict, ["-- 无 --", "随机"])
            elif preset_value != "-- 无 --":
                return preset_dict.get(preset_value, "")
            return ""

        output_format_instruction = self.get_output_format_instruction(生成中文提示词)

        full_prompt = ""
        if 工作模式 == "Kontext官方预设模式":
            if Kontext官方预设 == "创意-姿势克隆":
                pose_ref_b64 = self.tensor_to_base64(kwargs.get("视觉提示图像"))
                source_image_b64 = self.tensor_to_base64(kwargs.get("kontext预设模式参考图"))
                if not pose_ref_b64 or not source_image_b64: raise ValueError("错误：“创意-姿势克隆”预设需要同时连接“视觉提示图像”（姿势来源）和“kontext预设模式参考图”（源人物）。")
                system_prompt = KONTEX_PRESETS_PROMPTS.get(Kontext官方预设)
                system_prompt = re.sub(r'你的最终输出【必须】.*', '', system_prompt, flags=re.DOTALL).strip()
                full_prompt = system_prompt + output_format_instruction
                parts = [{"text": full_prompt}, {"inline_data": {"mime_type": "image/png", "data": pose_ref_b64}}, {"inline_data": {"mime_type": "image/png", "data": source_image_b64}}]
            else:
                kontext_ref_image = self.tensor_to_base64(kwargs.get("kontext预设模式参考图"))
                active_params = {}
                if 编辑描述_可选细节.strip(): active_params["核心细节"] = 编辑描述_可选细节.strip()
                param_map = {"风格": ("自定义风格", "风格转换", STYLE_TRANSFER_PRESETS, 风格转换), "场景": ("自定义场景", "场景预设", SCENE_PRESETS_DATA, 场景预设), "姿势": ("自定义姿势", "姿势预设", POSE_PRESETS_DATA, 姿势预设), "光影": ("自定义光影", "光影预设", LIGHTING_PRESETS_DATA, 光影预设)}
                for name, (custom_key, preset_key, preset_dict, preset_value) in param_map.items():
                    value = get_final_value(custom_key, preset_key, preset_dict, preset_value)
                    if value: active_params[name] = value
                if kwargs.get("自定义人像参数"): active_params["人像细节"] = kwargs.get("自定义人像参数")
                if kwargs.get("自定义摄影参数"): active_params["摄影参数"] = kwargs.get("自定义摄影参数")
                if kwargs.get("道具_可选"): active_params["道具"] = kwargs.get("道具_可选")
                if kwargs.get("补充提示词 (可选)"): active_params["补充说明"] = kwargs.get("补充提示词 (可选)")
                original_template = KONTEX_PRESETS_PROMPTS.get(Kontext官方预设, "")
                brief_match = re.search(r'简要说明：\n(.*?)(?=\n\n|$)', original_template, re.DOTALL)
                brief = brief_match.group(1).strip() if brief_match else "根据用户选择的预设和参数生成一条创意指令。"
                brief = brief.replace("{{SUBJECT}}", "指定的主体").replace("{{TITLE}}", "指定的标题")
                system_prompt_start = "你是一名顶级的创意提示工程师，为先进的图像编辑模型生成指令。你的任务是基于用户选择的核心预设、可选的附加参数以及可能提供的参考图，生成一条独特、具体且富有创意的图像编辑指令。\n\n**重要规则：**\n1. **拒绝重复**：你必须发挥创造力，即使输入完全相同，每次生成的指令也必须在措辞和细节上有所不同。严禁输出任何模板化的、一成不变的文本。\n2. **融合所有信息**：将下面的【核心创意简报】和【附加具体要求】无缝地融合成一条连贯的指令。\n3. **分析图像（如果提供）**：如果看到一张图片，请将其内容（人物、物体、环境）作为生成指令的基础。\n\n---\n\n"
                creative_brief_section = f"**【核心创意简报：{Kontext官方预设}】**\n{brief}\n\n"
                additional_reqs_section = ""
                if active_params:
                    additional_reqs_section = "**【附加具体要求】**\n"
                    for key, value in active_params.items(): additional_reqs_section += f"- **{key}**: {value}\n"
                    additional_reqs_section += "\n"
                system_prompt_end = f"(内部种子: {seed})\n\n请根据以上所有信息，生成你的最终指令。{output_format_instruction}"
                full_prompt = system_prompt_start + creative_brief_section + additional_reqs_section + system_prompt_end
                parts.append({"text": full_prompt})
                if kontext_ref_image: parts.append({"inline_data": {"mime_type": "image/png", "data": kontext_ref_image}})
        else:
            visual_prompt_image = self.tensor_to_base64(kwargs.get("视觉提示图像"))
            if visual_prompt_image:
                system_prompt = "你是一位顶级的视觉提示词工程师。你的任务是分析用户提供的带标注框的图像和文本描述，并生成一个精确的、基于视觉位置的指令。\n\n**核心规则**:\n1. **分析输入**: 你会收到一张可能包含方框的图像，以及一段文本描述。\n2. **构建指令**: 你的指令必须基于方框位置。你的回答必须以 'in the [颜色] box, ...' 或 'on the [颜色] box, ...' 开头。例如，用户描述是“添加一顶帽子”，且图中有个红框，你的指令应是 'in the red box, add a hat'。"
                full_prompt = f"{system_prompt}\n\n用户的文本描述: '{编辑描述_可选细节}'\n{output_format_instruction}"
                parts.append({"text": full_prompt})
                parts.append({"inline_data": {"mime_type": "image/png", "data": visual_prompt_image}})
            else:
                system_prompt = f"你是一个高性能的JSON生成引擎。你的唯一任务是将用户的结构化请求转换为一个JSON对象。不要输出任何其他文字、解释或Markdown代码标记。\n\n**最高优先级规则**:\n分析以下请求。`consistency`列表拥有绝对优先权。如果任何其他参数（如`description`或`pose_preset`）与`consistency`中的项目冲突，你必须忽略那个冲突的参数。你生成的最终提示词必须体现这一优先级。\n\n现在，处理以下用户请求并立即生成JSON：\n\n"
                final_style = get_final_value("自定义风格", "风格转换", STYLE_TRANSFER_PRESETS, 风格转换)
                final_scene = get_final_value("自定义场景", "场景预设", SCENE_PRESETS_DATA, 场景预设)
                final_pose = get_final_value("自定义姿势", "姿势预设", POSE_PRESETS_DATA, 姿势预设)
                final_lighting = get_final_value("自定义光影", "光影预设", LIGHTING_PRESETS_DATA, 光影预设)
                consistency_keys = {"保留脸部和身份": "保留脸部和身份", "保留姿势和体态": "保留姿势和体态", "保留服装和配饰": "保留服装和配饰", "保留表情": "保留表情", "保留光线和构图": "保留光线和构图", "保留背景": "保留背景", "保留相机角度": "保留相机角度"}
                consistency = [label for key, label in consistency_keys.items() if kwargs.get(key)]
                structured_request = {"task": 任务类型, "description": 编辑描述_可选细节, "style_transfer": final_style, "scene_preset": final_scene, "pose_preset": final_pose, "lighting_preset": final_lighting, "supplementary_prompt": kwargs.get("补充提示词 (可选)", ""), "consistency": consistency, "custom_portrait_params": kwargs.get("自定义人像参数", ""), "custom_photo_params": kwargs.get("自定义摄影参数", "")}
                full_prompt = f"{system_prompt}{json.dumps(structured_request, ensure_ascii=False, indent=2)}{output_format_instruction}"
                parts.append({"text": full_prompt})

        if AI服务商 == "无":
            return ("", "", full_prompt)

        try:
            response = None
            # --- API 调用逻辑 ---
            if AI服务商 == "内置模型":
                api_messages = [{"role": "user", "content": full_prompt}]
                api_url = "https://api.algion.dev/v1/chat/completions"
                headers = {"Content-Type": "application/json", "Authorization": "Bearer 123123"}
                payload = {"model": "gpt-4.1", "messages": api_messages, "stream": False}
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=180, verify=False)

            elif AI服务商 == "Gemini":
                if not Gemini_API密钥 or "在此输入" in Gemini_API密钥: raise ValueError("错误：请输入您的Gemini API密钥。")
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={Gemini_API密钥}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.8, "response_mime_type": "application/json"}}
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            elif AI服务商 == "智谱AI (Zhipu)":
                if not 智谱_API密钥 or "在此输入" in 智谱_API密钥: raise ValueError("错误：请输入您的Zhipu API密钥。")
                token = self.generate_zhipu_token(智谱_API密钥)
                model = "glm-4v-flash" if is_vision_task else "glm-4-flash"
                zhipu_messages = [{"role": "user", "content": []}]
                prompt_content = []
                for part in parts:
                    if "text" in part: prompt_content.append({"type": "text", "text": part["text"]})
                    elif "inline_data" in part: prompt_content.append({"type": "image_url", "image_url": {"url": f"data:{part['inline_data']['mime_type']};base64,{part['inline_data']['data']}"}})
                zhipu_messages[0]["content"] = prompt_content if len(prompt_content) > 1 else prompt_content[0].get('text', '')
                payload = {"model": model, "messages": zhipu_messages, "temperature": 0.8, "response_format": {"type": "json_object"}}
                api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            elif AI服务商 == "OpenRouter":
                if not OpenRouter_API密钥 or "在此输入" in OpenRouter_API密钥: raise ValueError("错误：请输入您的OpenRouter API密钥。")
                model_id = "qwen/qwen2.5-vl-72b-instruct:free" if is_vision_task else "deepseek/deepseek-r1-0528:free"
                open_ai_messages = [{"role": "user", "content": []}]
                content_list = []
                for part in parts:
                    if "text" in part: content_list.append({"type": "text", "text": part["text"]})
                    elif "inline_data" in part: content_list.append({"type": "image_url", "image_url": {"url": f"data:{part['inline_data']['mime_type']};base64,{part['inline_data']['data']}"}})
                open_ai_messages[0]["content"] = content_list if len(content_list) > 1 else content_list[0].get('text', '')
                headers = {"Authorization": f"Bearer {OpenRouter_API密钥}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/dax-ab/ComfyUI-NakuNode-Kontext", "X-Title": "NakuNode Prompter"}
                payload = {"model": model_id, "messages": open_ai_messages, "temperature": 0.8, "response_format": {"type": "json_object"}}
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            elif AI服务商 == "硅基流动 (Silicon Flow)":
                if not 硅基流动_API密钥 or "在此输入" in 硅基流动_API密钥: raise ValueError("错误：请输入您的硅基流动 API密钥。")
                model_id = "THUDM/GLM-4.1V-9B-Thinking" if is_vision_task else "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
                sf_messages = [{"role": "user", "content": []}]
                content_list = []
                for part in parts:
                    if "text" in part: content_list.append({"type": "text", "text": part["text"]})
                    elif "inline_data" in part: content_list.append({"type": "image_url", "image_url": {"url": f"data:{part['inline_data']['mime_type']};base64,{part['inline_data']['data']}"}})
                sf_messages[0]["content"] = content_list if len(content_list) > 1 else content_list[0].get('text', '')
                headers = {"Authorization": f"Bearer {硅基流动_API密钥}", "Content-Type": "application/json"}
                payload = {"model": model_id, "messages": sf_messages, "temperature": 0.8}
                if not is_vision_task:
                    payload["response_format"] = {"type": "json_object"}
                api_url = "https://api.siliconflow.cn/v1/chat/completions"
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            if response is None: raise ConnectionError("未能发送API请求。")
            response.raise_for_status()
            result = response.json()

            content_text = ""
            if AI服务商 == "Gemini":
                if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
                    content_text = result['candidates'][0]['content']['parts'][0]['text']
                else:
                    if 'promptFeedback' in result and 'blockReason' in result['promptFeedback']:
                        raise Exception(f"请求被Gemini阻止。原因: {result['promptFeedback']['blockReason']}.")
                    raise KeyError(f"从Gemini响应中解析内容失败: {json.dumps(result, ensure_ascii=False)}")
            else:
                if 'choices' in result and result['choices'] and 'message' in result['choices'][0] and 'content' in result['choices'][0]['message']:
                    content_text = result['choices'][0]['message']['content']
                else:
                    raise KeyError(f"从{AI服务商}响应中解析内容失败: {json.dumps(result, ensure_ascii=False)}")

            try:
                cleaned_text = re.sub(r'```json\n?|```', '', content_text).strip()
                prompts = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"AI返回的JSON格式无效。错误: {e}\n收到的原始文本: '{content_text}'")

            final_prompt_en = prompts.get("en", "未能生成英文提示词。")
            final_prompt_zh = prompts.get("zh", "未能生成中文提示词。") if 生成中文提示词 else ""

            if final_prompt_en.startswith(("你是一名", "你是一位", "你是一个")):
                return ("(AI返回了指令模板，而不是生成的提示词。请重试或调整参数。)", "(AI returned the instruction template. Please retry or adjust parameters.)", "")

            return (final_prompt_zh, final_prompt_en, "")

        except requests.exceptions.RequestException as e:
            error_msg = f"API 请求失败: {e}"
            if e.response is not None:
                if e.response.status_code == 429: error_msg = f"API请求过于频繁 (429): 您已超出该模型的速率限制。请等待一分钟或更换AI服务商后重试。\n原始响应: {e.response.text}"
                elif e.response.status_code >= 500: error_msg = f"API 服务端错误 ({e.response.status_code}): AI服务商服务器暂时不可用或过载。请稍后重试。\n原始响应: {e.response.text}"
                else: error_msg = f"API 请求失败 | 状态码: {e.response.status_code} | 响应: {e.response.text}"
            raise Exception(error_msg)
        except Exception as e:
            error_content = "N/A"
            if 'response' in locals() and response is not None:
                 try: error_content = response.text
                 except: error_content = str(response)
            raise Exception(f"处理时发生错误: {type(e).__name__}: {e}\n收到的API响应内容: {error_content}")


# --------------------------------------------------------------------------------
# 节点映射
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "FLUX2EditPromptGenerator": KontextPromptGeneratorNode,
    "FLUX2EditPortraitParameters": PortraitParametersNode,
    "FLUX2EditPhotographyParameters": PhotographyParametersNode,
    "FLUX2EditPropsPresets": PropsPresetsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FLUX2EditPromptGenerator": "NakuNode FLUX2 Edit 提示词生成器",
    "FLUX2EditPortraitParameters": "NakuNode FLUX2 Edit 人像参数",
    "FLUX2EditPhotographyParameters": "NakuNode FLUX2 Edit 专业摄影参数",
    "FLUX2EditPropsPresets": "NakuNode FLUX2 Edit 道具预设",
}