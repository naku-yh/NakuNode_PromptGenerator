# -*- coding: utf-8 -*-
"""
NakuNode - API Utils
API 工具函数 - 提供 API 字符串解密和参数提取功能
"""
import base64
import json


def decrypt_api_string(api_string):
    """
    解密 API 字符串
    Args:
        api_string: 加密的 API 字符串，格式为 "NAKU_API_V1:{base64_encoded_json}"
    Returns:
        dict: 包含 siliconflow_api_key, custom_api_key, custom_api_url 的字典，失败返回 None
    """
    if not api_string or not api_string.startswith("NAKU_API_V1:"):
        return None
    
    try:
        encoded = api_string.replace("NAKU_API_V1:", "")
        decoded = base64.b64decode(encoded).decode('utf-8')
        data = json.loads(decoded)
        return {
            'siliconflow_api_key': data.get('siliconflow_api_key', ''),
            'custom_api_key': data.get('custom_api_key', ''),
            'custom_api_url': data.get('custom_api_url', 'https://api.siliconflow.cn/v1')
        }
    except Exception as e:
        print(f"[NakuNode API Utils] 解密失败：{e}")
        return None


def get_api_credentials(api_string, siliconflow_api_key="", custom_api_key="", custom_url="https://api.siliconflow.cn/v1", preferred_provider="SiliconFlow"):
    """
    获取 API 凭证 - 优先使用 API String，如果为空则使用独立参数

    优先级逻辑：
    1. 如果指定了 preferred_provider 且对应 API Key 有效，优先使用 preferred_provider
    2. 如果只有 SiliconFlow API Key，使用 SiliconFlow
    3. 如果只有 Custom API Key，使用 Custom
    4. 如果两者都有，优先使用 preferred_provider（如果有效）

    Args:
        api_string: 加密的 API 字符串（可选）
        siliconflow_api_key: SiliconFlow API Key（可选）
        custom_api_key: Custom API Key（可选）
        custom_url: Custom API URL（可选）
        preferred_provider: 优先使用的 API 提供商（可选，默认 "SiliconFlow"）
    Returns:
        tuple: (api_provider, api_key, api_url, siliconflow_api_key, custom_api_key, custom_url)
    """
    # 尝试解密 API String
    decrypted = None
    if api_string and api_string.strip():
        decrypted = decrypt_api_string(api_string.strip())

    # 如果解密成功，使用解密后的值
    if decrypted:
        sf_key = decrypted.get('siliconflow_api_key', '')
        c_key = decrypted.get('custom_api_key', '')
        c_url = decrypted.get('custom_api_url', 'https://api.siliconflow.cn/v1')

        # 清理空白字符
        sf_key = sf_key.strip() if sf_key else ""
        c_key = c_key.strip() if c_key else ""
        c_url = c_url.strip() if c_url else "https://api.siliconflow.cn/v1"

        # 无效 key 列表
        invalid_sf = ["Please enter SiliconFlow API Key", "请填写 SiliconFlow API Key", ""]
        invalid_custom = ["Please enter your API Key", "请填写您的 API Key", ""]

        # 根据 preferred_provider 决定优先级
        if preferred_provider == "Custom":
            # 优先使用 Custom
            if c_key and c_key not in invalid_custom:
                # 确保 URL 不以 /v1 结尾，后面会添加 /v1/chat/completions
                base_url = c_url.rstrip('/')
                if base_url.endswith('/v1'):
                    base_url = base_url[:-3]
                return ("Custom", c_key, base_url, sf_key, c_key, c_url)
            elif sf_key and sf_key not in invalid_sf:
                return ("SiliconFlow", sf_key, "https://api.siliconflow.cn/v1", sf_key, c_key, c_url)
        else:
            # 优先使用 SiliconFlow
            if sf_key and sf_key not in invalid_sf:
                return ("SiliconFlow", sf_key, "https://api.siliconflow.cn/v1", sf_key, c_key, c_url)
            elif c_key and c_key not in invalid_custom:
                # 确保 URL 不以 /v1 结尾
                base_url = c_url.rstrip('/')
                if base_url.endswith('/v1'):
                    base_url = base_url[:-3]
                return ("Custom", c_key, base_url, sf_key, c_key, c_url)

    # 如果 API String 无效，回退到独立参数
    # 清理空白字符
    siliconflow_api_key = siliconflow_api_key.strip() if siliconflow_api_key else ""
    custom_api_key = custom_api_key.strip() if custom_api_key else ""
    custom_url = custom_url.strip() if custom_url else "https://api.siliconflow.cn/v1"

    # 无效 key 列表
    invalid_sf = ["Please enter SiliconFlow API Key", "请填写 SiliconFlow API Key", ""]
    invalid_custom = ["Please enter your API Key", "请填写您的 API Key", ""]

    # 根据 preferred_provider 决定优先级
    if preferred_provider == "Custom":
        # 优先使用 Custom
        if custom_api_key and custom_api_key not in invalid_custom:
            # 确保 URL 不以 /v1 结尾
            base_url = custom_url.rstrip('/')
            if base_url.endswith('/v1'):
                base_url = base_url[:-3]
            return ("Custom", custom_api_key, base_url, siliconflow_api_key, custom_api_key, custom_url)
        elif siliconflow_api_key and siliconflow_api_key not in invalid_sf:
            return ("SiliconFlow", siliconflow_api_key, "https://api.siliconflow.cn/v1", siliconflow_api_key, custom_api_key, custom_url)
    else:
        # 优先使用 SiliconFlow
        if siliconflow_api_key and siliconflow_api_key not in invalid_sf:
            return ("SiliconFlow", siliconflow_api_key, "https://api.siliconflow.cn/v1", siliconflow_api_key, custom_api_key, custom_url)
        elif custom_api_key and custom_api_key not in invalid_custom:
            # 确保 URL 不以 /v1 结尾
            base_url = custom_url.rstrip('/')
            if base_url.endswith('/v1'):
                base_url = base_url[:-3]
            return ("Custom", custom_api_key, base_url, siliconflow_api_key, custom_api_key, custom_url)

    # 都没有则返回 SiliconFlow（会在节点中检查并提示）
    return ("SiliconFlow", siliconflow_api_key, "https://api.siliconflow.cn/v1", siliconflow_api_key, custom_api_key, custom_url)


def parse_api_string_for_node(api_string, node_name="API Node"):
    """
    为节点解析 API 字符串，输出调试信息
    Args:
        api_string: 加密的 API 字符串
        node_name: 节点名称，用于日志输出
    Returns:
        bool: 是否成功解析
    """
    if not api_string or not api_string.strip():
        print(f"[{node_name}] 未提供 API String，将使用独立 API 参数")
        return False
    
    decrypted = decrypt_api_string(api_string.strip())
    if decrypted:
        sf_key = decrypted.get('siliconflow_api_key', '')
        c_key = decrypted.get('custom_api_key', '')
        c_url = decrypted.get('custom_api_url', '')
        
        print(f"[{node_name}] API String 解析成功")
        print(f"[{node_name}] SiliconFlow API Key: {'已设置' if sf_key else '未设置'}")
        print(f"[{node_name}] Custom API Key: {'已设置' if c_key else '未设置'}")
        print(f"[{node_name}] Custom API URL: {c_url}")
        return True
    else:
        print(f"[{node_name}] API String 解析失败，将使用独立 API 参数")
        return False
