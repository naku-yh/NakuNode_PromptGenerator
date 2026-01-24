#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 NakuNodePromptEVO 节点的新功能
"""

from nodes.NakuNode_PromptEVO import NakuNodePromptEVO

def test_node_new_features():
    # 创建节点实例
    node = NakuNodePromptEVO()
    
    # 测试参数
    文字需求 = "一只可爱的小猫在阳光下玩耍"
    AI模型选择 = "QwenImage"
    API提供商 = "无"
    随机种子 = 42
    
    # 摄影参数
    相机视角 = "正面视角"
    镜头与光圈 = "标准镜头(50mm)"
    胶片与风格 = "柯达Portra 400"
    色彩与色调 = "暖色调"
    构图方式 = "三分法"
    
    # 调用生成函数
    result = node.generate_prompt(文字需求, AI模型选择, API提供商, 随机种子,
                                相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式)
    
    print("测试1 - API提供商='无':")
    print(result[0])
    
    # 测试智谱AI
    print("\n" + "="*50)
    print("测试2 - API提供商='智谱':")
    API提供商 = "智谱"
    result_zhipu = node.generate_prompt(文字需求, AI模型选择, API提供商, 随机种子,
                                      相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式,
                                      API密钥="your_zhipu_api_key")
    
    print(result_zhipu[0])
    
    # 测试硅基流动 - Qwen3
    print("\n" + "="*50)
    print("测试3 - API提供商='硅基流动', 模型='Qwen3':")
    API提供商 = "硅基流动"
    硅基流动模型选择 = "Qwen3"
    result_siwei_qwen = node.generate_prompt(文字需求, AI模型选择, API提供商, 随机种子,
                                           相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式,
                                           API密钥="your_siwei_api_key", 硅基流动模型选择=硅基流动模型选择)
    
    print(result_siwei_qwen[0])
    
    # 测试硅基流动 - KIMI-K2
    print("\n" + "="*50)
    print("测试4 - API提供商='硅基流动', 模型='KIMI-K2':")
    硅基流动模型选择 = "KIMI-K2"
    result_siwei_kimi = node.generate_prompt(文字需求, AI模型选择, API提供商, 随机种子,
                                           相机视角, 镜头与光圈, 胶片与风格, 色彩与色调, 构图方式,
                                           API密钥="your_siwei_api_key", 硅基流动模型选择=硅基流动模型选择)
    
    print(result_siwei_kimi[0])

if __name__ == "__main__":
    test_node_new_features()