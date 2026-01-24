#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 NakuNodePromptEVO 节点的API调用功能
"""

def test_api_logic():
    print("测试NakuNodePromptEVO节点的API调用逻辑:")
    print("1. 用户选择AI模型 -> 获取对应的内置prompt")
    print("2. 结合用户选择的内容（构图、景别等）和用户输入的文本")
    print("3. 传送到用户选择的API和对应的API模型进行重写")
    print("4. 回传到节点后输出文字")
    
    print("\nAPI调用格式（硅基流动）:")
    print("from openai import OpenAI")
    print("")
    print("client = OpenAI(")
    print("    api_key=\"YOUR_API_KEY\",")
    print("    base_url=\"https://api.siliconflow.cn/v1\"")
    print(")")
    print("")
    print("response = client.chat.completions.create(")
    print("    model=\"Pro/zai-org/GLM-4.7\",")
    print("    messages=[")
    print("        {\"role\": \"system\", \"content\": \"你是一名图片生成专家...\"},")
    print("        {\"role\": \"user\", \"content\": \"一个名为NAKU 的男人站在山顶, front view, diagonal composition\"}")
    print("    ]")
    print(")")
    print("print(response.choices[0].message.content)")

if __name__ == "__main__":
    test_api_logic()