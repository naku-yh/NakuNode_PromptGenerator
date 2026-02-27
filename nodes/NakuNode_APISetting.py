# -*- coding: utf-8 -*-
"""
NakuNode - API Setting Node
API 密钥加密存储节点，用于安全管理和分享工作流
"""
import json
import os
import base64


class NakuNode_APISetting:
    """
    API 设置节点 - 用于加密存储和管理 API 密钥
    支持 SiliconFlow API Key、Custom API Key 和 Custom API URL 的加密存储
    注意：API Key 只在前端界面输入，节点上只显示按钮和输出
    使用固定存储 ID "default" 以便所有节点共享配置
    """

    # 使用固定存储 ID，这样无论节点 ID 是多少都共享同一份配置
    STORAGE_ID = "default"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("api_string",)
    FUNCTION = "generate_api_string"
    CATEGORY = "NakuNode/API 管理"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(s, **kwargs):
        # 让节点每次都重新执行
        return float("nan")

    def encrypt_api_data(self, data_dict):
        """简单的 Base64 加密（注意：这不是强加密，仅用于防止明文泄露）"""
        json_str = json.dumps(data_dict, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return f"NAKU_API_V1:{encoded}"

    def decrypt_api_data(self, api_string):
        """解密 API 字符串"""
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
            print(f"[NakuNode APISetting] 解密失败：{e}")
            return None

    def generate_api_string(self, **kwargs):
        # 获取节点 ID（仅用于日志显示）
        node_id = kwargs.get('unique_id', 'default')
        
        # 使用固定存储 ID 读取数据
        storage_id = self.STORAGE_ID
        
        # 获取存储文件路径
        storage_file = self.get_storage_file()
        
        # 从存储文件读取 API 数据
        api_data = self.load_api_data(storage_id, storage_file)
        
        if not api_data:
            # 如果没有存储的数据，返回空字符串
            print(f"[NakuNode APISetting] 未找到 API 设置，请点击 ⚙️ API 设置 按钮进行配置")
            return {"ui": {"api_string": "", "status": "not_configured"}, "result": ("",)}
        
        # 生成加密的 API 字符串
        encrypted_string = self.encrypt_api_data(api_data)
        
        print(f"[NakuNode APISetting] API 设置已加载 (节点 ID: {node_id})")
        print(f"[NakuNode APISetting] SiliconFlow API Key: {'已设置' if api_data.get('siliconflow_api_key') else '未设置'}")
        print(f"[NakuNode APISetting] Custom API Key: {'已设置' if api_data.get('custom_api_key') else '未设置'}")
        print(f"[NakuNode APISetting] Custom API URL: {api_data.get('custom_api_url', 'https://api.siliconflow.cn/v1')}")
        print(f"[NakuNode APISetting] 加密的 API String: {encrypted_string[:50]}...")
        
        # 返回加密的 API 字符串和 UI 状态
        return {"ui": {"api_string": encrypted_string, "status": "configured"}, "result": (encrypted_string,)}

    def get_storage_file(self):
        """获取存储文件路径 - 使用统一的存储位置"""
        # 优先使用 ComfyUI 的 output 目录
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
            return os.path.join(output_dir, "naku_api_setting_storage.json")
        except:
            # 如果 folder_paths 不可用，使用用户主目录
            home_dir = os.path.expanduser("~")
            naku_dir = os.path.join(home_dir, ".naku_api")
            os.makedirs(naku_dir, exist_ok=True)
            return os.path.join(naku_dir, "naku_api_setting_storage.json")

    def load_api_data(self, node_id, storage_file):
        """从存储文件加载 API 数据"""
        try:
            if os.path.exists(storage_file):
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(str(node_id), None)
        except Exception as e:
            print(f"[NakuNode APISetting] 加载 API 数据失败：{e}")
        return None

    @staticmethod
    def decrypt_api_string(api_string):
        """静态方法，供其他节点调用解密"""
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
            print(f"[NakuNode APISetting] 静态解密失败：{e}")
            return None


# 注册节点
NODE_CLASS_MAPPINGS = {
    "NakuNode_APISetting": NakuNode_APISetting
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNode_APISetting": "NakuNode-API 设置"
}


# 注册 API 端点
try:
    import server
    from aiohttp import web

    # 获取 API 数据的端点
    @server.PromptServer.instance.routes.get("/naku_api_setting/get_api/{node_id}")
    async def get_api_handler(request):
        node_id = request.match_info["node_id"]
        
        # 使用统一的存储路径
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
            storage_file = os.path.join(output_dir, "naku_api_setting_storage.json")
        except:
            home_dir = os.path.expanduser("~")
            naku_dir = os.path.join(home_dir, ".naku_api")
            storage_file = os.path.join(naku_dir, "naku_api_setting_storage.json")

        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    api_data = data.get(node_id, None)
                    if api_data:
                        return web.json_response({
                            "status": "success",
                            "data": api_data
                        })
            except Exception as e:
                print(f"[NakuNode API] 读取存储文件失败：{e}")

        return web.json_response({"status": "not_found", "data": None})

    # 保存 API 数据的端点
    @server.PromptServer.instance.routes.post("/naku_api_setting/save_api")
    async def save_api_handler(request):
        json_data = await request.json()
        node_id = json_data.get("node_id")
        api_data = json_data.get("data")
        
        # 使用统一的存储路径
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
            storage_file = os.path.join(output_dir, "naku_api_setting_storage.json")
        except:
            home_dir = os.path.expanduser("~")
            naku_dir = os.path.join(home_dir, ".naku_api")
            storage_file = os.path.join(naku_dir, "naku_api_setting_storage.json")

        try:
            os.makedirs(os.path.dirname(storage_file), exist_ok=True)

            data = {}
            if os.path.exists(storage_file):
                try:
                    with open(storage_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = {}

            data[str(node_id)] = api_data

            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[NakuNode API] API 数据已保存到：{storage_file}")

            return web.json_response({"status": "success"})
        except Exception as e:
            print(f"[NakuNode API] 保存 API 数据失败：{e}")
            return web.json_response({"status": "error", "message": str(e)})

    # 重置 API 数据的端点
    @server.PromptServer.instance.routes.post("/naku_api_setting/reset_api")
    async def reset_api_handler(request):
        json_data = await request.json()
        node_id = json_data.get("node_id")
        
        # 使用统一的存储路径
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
            storage_file = os.path.join(output_dir, "naku_api_setting_storage.json")
        except:
            home_dir = os.path.expanduser("~")
            naku_dir = os.path.join(home_dir, ".naku_api")
            storage_file = os.path.join(naku_dir, "naku_api_setting_storage.json")

        try:
            if os.path.exists(storage_file):
                try:
                    with open(storage_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if str(node_id) in data:
                        del data[str(node_id)]
                    
                    with open(storage_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"[NakuNode API] API 设置已重置：{node_id}")
                    
                    return web.json_response({"status": "success"})
                except Exception as e:
                    print(f"[NakuNode API] 重置 API 数据失败：{e}")
            
            return web.json_response({"status": "success"})
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)})

except ImportError:
    pass
