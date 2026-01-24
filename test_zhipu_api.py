#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 NakuNodePromptEVO 节点的智谱AI API调用功能
"""

def test_zhipu_api_format():
    print("智谱AI API调用格式测试:")
    print("")
    print("from zhipuai import ZhipuAiClient")
    print("")
    print("client = ZhipuAiClient(api_key=\"your-api-key\")  # 请填写您自己的 API Key")
    print("")
    print("response = client.chat.completions.create(")
    print("    model=\"glm-4.7\",")
    print("    messages=[")
    print("        {\"role\": \"user\", \"content\": \"你是一名图片生成专家，通过分析用户输入的文字需求，最终以[主体描述] + [细节修饰] + [艺术风格] + [画面构图] + [光照/色彩] + [画质参数]这样的格式输出一段客观描述的自然语句，不要有废话, 不要分行。不要带有主观情绪的词句例如'兼具典雅传统与时尚活力''既增添神秘感与优雅气质''增添了时尚活力与异域奇幻感'等等。示例：'一位身穿未来科技感银色战甲的女战士，站在火星红色荒漠上，背景是巨大的地球和星空，赛博朋克风格，电影级光影，超高清8K，细节丰富，景深强烈'。需要避免以下问题：1.模糊不清的描述（如'好看的东西'）2.自相矛盾的元素（如'白天的满天繁星'）3.过于冗长或堆砌无关词汇。\\n\\n一个名为NAKU 的男人站在山顶, front view, diagonal composition\"}")
    print("    ],")
    print("    thinking={")
    print("        \"type\": \"enabled\",    # 启用深度思考模式")
    print("    },")
    print("    max_tokens=65536,          # 最大输出 tokens")
    print("    temperature=1.0           # 控制输出的随机性")
    print(")")
    print("")
    print("# 获取完整回复")
    print("print(response.choices[0].message)")

if __name__ == "__main__":
    test_zhipu_api_format()