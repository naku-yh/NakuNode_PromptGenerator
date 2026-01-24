#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 NakuNodePromptEVO 节点的功能
"""

from nodes.NakuNode_PromptEVO import NakuNodePromptEVO

def test_node():
    # 创建节点实例
    node = NakuNodePromptEVO()
    
    # 测试参数
    文字需求 = "一只可爱的小猫在阳光下玩耍"
    AI模型选择 = "QwenImage"
    随机种子 = 42
    
    # 摄影参数
    相机视角 = "正面视角"
    镜头与光圈 = "标准镜头(50mm)"
    胶片与风格 = "柯达Portra 400"
    色彩与色调 = "暖色调"
    构图方式 = "三分法"
    
    # 调用生成函数
    result = node.generate_prompt(文字需求, AI模型选择, 随机种子,
                                相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式)
    
    print("生成的提示词:")
    print(result[0])
    print("\n" + "-"*30 + " 关键部分 " + "-"*30)
    # 提取用户需求部分来展示参数是如何附加的
    lines = result[0].split('\n')
    for line in lines:
        if '用户需求：' in line:
            print(line)
            break

    # 测试随机参数
    print("\n" + "="*50)
    print("测试随机参数:")
    result_random = node.generate_prompt(文字需求, AI模型选择, 随机种子,
                                       "随机", "随机", "随机", "随机", "随机")

    print("生成的提示词 (随机参数):")
    print(result_random[0])
    print("\n" + "-"*30 + " 关键部分 " + "-"*30)
    # 提取用户需求部分来展示参数是如何附加的
    lines = result_random[0].split('\n')
    for line in lines:
        if '用户需求：' in line:
            print(line)
            break

if __name__ == "__main__":
    test_node()