# NakuNode API 加密存储功能使用说明

## 功能概述

为了防止 API Key 明文泄露，NakuNode 新增了 API 加密存储功能。通过 `NakuNode-API 设置` 节点，可以安全地管理和存储 API 密钥，分享工作流时不会暴露明文 API Key。

## 新增节点

### 1. NakuNode-API 设置 (NakuNode_APISetting)

**功能**：API 密钥加密存储和管理节点

**节点界面**：
- **⚙️ API 设置** 按钮：打开前端配置界面
- **🔄 重置设置** 按钮：清除当前节点的 API 设置
- **输出**：`api_string` - 加密的 API 字符串

**注意**：节点上没有输入框，所有 API Key 都通过前端界面输入，确保安全！

**操作步骤**：
1. 点击 **⚙️ API 设置** 按钮
2. 在前端界面输入 API Key 和 URL
3. 点击 **✅ 确认保存**
4. 节点自动生成加密的 `api_string` 输出

### 2. 更新的 API 节点

以下 8 个节点已更新支持 `api_string` 输入：

1. **NakuNode-单图视频提示词生成器** (ImageVideoPromptOptimizer)
2. **NakuNode-专业视频提示词润色器** (ProfessionalVideoPromptGenerator)
3. **NakuNode-首尾帧视频提示词生成器** (DualImageVideoScriptGenerator)
4. **NakuNode-分镜图片生成器** (NakuNode_分镜图片生成)
5. **NakuNode-图片描述生成器** (NakuNodeImagePrompter)
6. **NakuNode-提示词进化器** (NakuNodePromptEVO)
7. **NakuNode-LTX 视频提示词生成器** (NakuNodeLTXPrompter)
8. **NakuNode-LTX 首尾帧提示词生成器** (NakuNode_LTX_FTE_Prompter)

**新增输入**：
- `api_string` (STRING): 加密的 API 字符串，连接 API Setting 节点或留空使用独立参数

**变更**：
- `api_provider` 移动到 optional（可选）
- `SiliconFlow_API_KEY`、`User_API_KEY`、`custom_url` 改为可选，默认值为空

## 使用方法

### 配置 API 密钥（推荐）

1. **添加 API Setting 节点**
   - 在 ComfyUI 中添加 `NakuNode-API 设置` 节点

2. **配置 API 密钥**
   - 点击节点上的 **⚙️ API 设置** 按钮
   - 在弹出的前端界面中输入：
     - SiliconFlow API Key
     - Custom API Key（可选）
     - Custom API URL（可选）
   - 点击 **✅ 确认保存**

3. **连接 API 节点**
   - 将 API Setting 节点的 `api_string` 输出连接到任意 API 节点的 `api_string` 输入
   - API 节点会自动识别并使用加密的 API 密钥

4. **分享工作流**
   - 分享工作流时，API Key 以加密形式存储在工作流中
   - 其他人无法直接查看明文 API Key

### 节点特点

- ✅ **无输入框**：节点上没有任何输入框，避免明文泄露
- ✅ **前端配置**：所有敏感信息通过前端界面输入
- ✅ **加密存储**：API Key 加密存储在本地
- ✅ **一键重置**：可随时清除 API 设置

## API 字符串格式

加密的 API 字符串格式：
```
NAKU_API_V1:{base64_encoded_json}
```

其中 JSON 结构：
```json
{
  "siliconflow_api_key": "your_sf_api_key",
  "custom_api_key": "your_custom_api_key",
  "custom_api_url": "https://api.siliconflow.cn/v1"
}
```

## 优先级规则

API 节点按以下优先级使用 API 凭证：

1. **API String**（如果提供且有效）
   - 优先使用解密后的 SiliconFlow API Key
   - 如果为空，使用解密后的 Custom API Key

2. **独立参数**（如果 API String 无效）
   - 优先使用 `SiliconFlow_API_KEY`
   - 如果为空，使用 `User_API_KEY`

## 安全说明

⚠️ **重要提示**：

1. **加密强度**：当前使用 Base64 编码，这不是强加密，仅用于防止明文泄露
2. **本地存储**：API 密钥会加密存储在本地临时文件中
3. **分享安全**：分享工作流时，API Key 不会以明文形式暴露
4. **重置功能**：可以通过 **🔄 重置设置** 按钮清除 API 设置

## 故障排除

### 问题：API 节点提示 "API key not provided"

**解决方案**：
1. 检查 API Setting 节点是否已配置并保存
2. 确认 `api_string` 已正确连接
3. 或者在 API 节点中直接输入独立 API Key

### 问题：API String 解析失败

**解决方案**：
1. 检查 API String 格式是否正确（应以 `NAKU_API_V1:` 开头）
2. 重新配置 API Setting 节点
3. 使用 **🔄 重置设置** 后重新保存

### 问题：前端界面无法打开

**解决方案**：
1. 刷新浏览器页面
2. 检查 ComfyUI 是否为最新版本
3. 清除浏览器缓存

## 技术细节

### 文件结构

```
NakuNode_PromptGenerator/
├── nodes/
│   ├── NakuNode_APISetting.py      # API 设置节点
│   ├── api_utils.py                 # API 工具函数
│   └── [其他 API 节点].py
├── web/
│   └── API.js                       # 前端界面
├── locales/zh/
│   └── nodeDefs.json                # 中文翻译
└── __init__.py                      # 节点注册
```

### API 端点

- `GET /naku_api_setting/get_api/{node_id}`: 获取 API 数据
- `POST /naku_api_setting/save_api`: 保存 API 数据
- `POST /naku_api_setting/reset_api`: 重置 API 数据

## 版本历史

- **V1.1**: API 加密存储功能
  - 新增 NakuNode-API 设置节点
  - 8 个 API 节点支持 api_string 输入
  - 新增前端配置界面
  - 新增 API 加密/解密工具函数
  - 支持手动选择 API 提供商（SiliconFlow/Custom）

---

**开发者**: Naku  
**版本**: V1.1  
**更新日期**: 2026-02-27
