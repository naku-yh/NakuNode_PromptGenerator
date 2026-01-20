import json
import os

# 定义节点类
class NakuNodeTextEditor:
    def __init__(self):
        self.current_text = ""
        # 创建一个临时存储编辑文本的文件路径
        self.storage_file = self.get_storage_file()
    
    def get_storage_file(self):
        # 获取ComfyUI的临时目录或当前目录下的存储文件
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
            return os.path.join(temp_dir, "naku_text_editor_storage.json")
        except:
            # 如果folder_paths不可用，使用当前目录
            return os.path.join(os.path.dirname(__file__), "naku_text_editor_storage.json")
    
    def load_edited_text(self, node_id):
        """从存储中加载编辑过的文本"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(str(node_id), None)
        except:
            pass
        return None

    def save_edited_text(self, node_id, text):
        """保存编辑过的文本到存储"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            
            data = {}
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            data[str(node_id)] = text
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存编辑文本时出错: {e}")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {"forceInput": True, "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_output",)
    FUNCTION = "process_text"
    OUTPUT_NODE = True
    CATEGORY = "NakuNode/文本处理"

    def process_text(self, text_input):
        # 这个节点只是传递文本，实际编辑在前端完成
        # 返回UI元素以触发前端界面
        return {"ui": {"current_text": text_input}, "result": (text_input,)}

# 节点映射
NODE_CLASS_MAPPINGS = {
    "NakuNodeTextEditor": NakuNodeTextEditor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodeTextEditor": "NakuNode-文本修改节点"
}

# 只有在ComfyUI环境中才注册API端点
try:
    import server
    from aiohttp import web

    # 注册API端点以接收从前端编辑器发送的文本
    @server.PromptServer.instance.routes.post("/naku_text_editor/update_text")
    async def update_text_handler(request):
        json_data = await request.json()
        node_id = json_data.get("node_id")
        edited_text = json_data.get("edited_text")
        
        # 获取存储文件路径
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
            storage_file = os.path.join(temp_dir, "naku_text_editor_storage.json")
        except:
            # 如果folder_paths不可用，使用当前目录
            storage_file = os.path.join(os.path.dirname(__file__), "naku_text_editor_storage.json")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        # 读取现有的数据
        data = {}
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        
        # 更新数据
        data[str(node_id)] = edited_text
        
        # 写入文件
        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return web.json_response({"status": "success"})
    
    # 添加一个获取编辑文本的API端点
    @server.PromptServer.instance.routes.get("/naku_text_editor/get_text/{node_id}")
    async def get_text_handler(request):
        node_id = request.match_info["node_id"]
        
        # 获取存储文件路径
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
            storage_file = os.path.join(temp_dir, "naku_text_editor_storage.json")
        except:
            # 如果folder_paths不可用，使用当前目录
            storage_file = os.path.join(os.path.dirname(__file__), "naku_text_editor_storage.json")
        
        # 读取数据
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    edited_text = data.get(node_id, None)
                    if edited_text is not None:
                        return web.json_response({"text": edited_text})
            except:
                pass
        
        return web.json_response({"text": None})
except ImportError:
    # 在非ComfyUI环境中，跳过API端点注册
    pass