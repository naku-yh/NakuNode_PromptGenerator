/**
 * NakuNode API Setting Frontend
 * API 设置前端界面 - 用于安全配置和管理 API 密钥
 */

import { app } from "../../scripts/app.js";
import { ComfyDialog, $el } from "../../scripts/ui.js";

// API 设置对话框
class APISettingDialog extends ComfyDialog {
    constructor() {
        super();
        this.nodeId = null;
        this.element.classList.add("naku-api-dialog");
    }

    createButtons() {
        // 不创建默认按钮，使用自定义按钮
        return [];
    }

    show(nodeId) {
        this.nodeId = "default";  // 使用固定 ID
        this.loadSettings();
        super.show("API 设置 - NakuNode");
    }

    loadSettings() {
        // 从服务器加载当前节点的 API 设置
        fetch(`/naku_api_setting/get_api/${this.nodeId}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success" && data.data) {
                    this.siliconflowApiKey = data.data.siliconflow_api_key || "";
                    this.customApiKey = data.data.custom_api_key || "";
                    this.customApiUrl = data.data.custom_api_url || "https://api.siliconflow.cn/v1";
                } else {
                    this.siliconflowApiKey = "";
                    this.customApiKey = "";
                    this.customApiUrl = "https://api.siliconflow.cn/v1";
                }
                this.renderContent();
            })
            .catch(err => {
                console.error("[NakuNode API] 加载设置失败:", err);
                this.siliconflowApiKey = "";
                this.customApiKey = "";
                this.customApiUrl = "https://api.siliconflow.cn/v1";
                this.renderContent();
            });
    }

    renderContent() {
        this.element.innerHTML = `
            <div class="naku-api-content">
                <h3 style="margin: 0 0 20px 0; color: #fff; font-size: 18px;">🔐 NakuNode API 设置</h3>
                
                <div class="naku-api-section">
                    <label style="display: block; margin-bottom: 8px; color: #ccc; font-weight: bold; font-size: 14px;">
                        SiliconFlow API Key
                    </label>
                    <input 
                        type="password" 
                        id="siliconflow_api_key" 
                        value="${this.siliconflowApiKey || ''}"
                        placeholder="请输入 SiliconFlow API Key"
                        style="width: 100%; padding: 10px; border: 1px solid #444; border-radius: 4px; background: #222; color: #fff; font-size: 14px; box-sizing: border-box;"
                    />
                    <p style="margin: 5px 0 15px 0; font-size: 12px; color: #888;">
                        SiliconFlow 平台 API 密钥，用于访问 Qwen、KIMI、GLM 等模型
                    </p>
                </div>

                <div class="naku-api-section">
                    <label style="display: block; margin-bottom: 8px; color: #ccc; font-weight: bold; font-size: 14px;">
                        Custom API Key
                    </label>
                    <input 
                        type="password" 
                        id="custom_api_key" 
                        value="${this.customApiKey || ''}"
                        placeholder="请输入自定义 API Key"
                        style="width: 100%; padding: 10px; border: 1px solid #444; border-radius: 4px; background: #222; color: #fff; font-size: 14px; box-sizing: border-box;"
                    />
                    <p style="margin: 5px 0 15px 0; font-size: 12px; color: #888;">
                        自定义 API 服务的密钥
                    </p>
                </div>

                <div class="naku-api-section">
                    <label style="display: block; margin-bottom: 8px; color: #ccc; font-weight: bold; font-size: 14px;">
                        Custom API URL
                    </label>
                    <input 
                        type="text" 
                        id="custom_api_url" 
                        value="${this.customApiUrl || 'https://api.siliconflow.cn/v1'}"
                        placeholder="https://api.siliconflow.cn/v1"
                        style="width: 100%; padding: 10px; border: 1px solid #444; border-radius: 4px; background: #222; color: #fff; font-size: 14px; box-sizing: border-box;"
                    />
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #888;">
                        自定义 API 服务地址，默认使用 SiliconFlow
                    </p>
                </div>

                <div class="naku-api-info" style="margin-top: 20px; padding: 15px; background: #2a2a2a; border-radius: 4px; border-left: 3px solid #4CAF50;">
                    <h4 style="margin: 0 0 10px 0; color: #4CAF50; font-size: 14px;">💡 使用说明</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 12px; color: #aaa; line-height: 1.8;">
                        <li>点击"确认保存"后，API 密钥会加密存储并生成 API String</li>
                        <li>将 API Setting 节点的输出连接到其他 API 节点的 api_string 输入</li>
                        <li>分享工作流时，API Key 不会明文暴露</li>
                        <li>点击"重置"会清除当前节点的 API 设置</li>
                    </ul>
                </div>

                <div class="naku-api-buttons" style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                    <button id="naku-api-cancel" style="padding: 10px 20px; border: 1px solid #666; border-radius: 4px; background: #333; color: #ccc; cursor: pointer; font-size: 14px;">
                        取消
                    </button>
                    <button id="naku-api-reset" style="padding: 10px 20px; border: 1px solid #f44336; border-radius: 4px; background: #f44336; color: #fff; cursor: pointer; font-size: 14px;">
                        🔄 重置
                    </button>
                    <button id="naku-api-save" style="padding: 10px 20px; border: 1px solid #4CAF50; border-radius: 4px; background: #4CAF50; color: #fff; cursor: pointer; font-size: 14px; font-weight: bold;">
                        ✅ 确认保存
                    </button>
                </div>
            </div>
        `;

        // 绑定按钮事件
        this.element.querySelector("#naku-api-save").onclick = () => this.saveSettings();
        this.element.querySelector("#naku-api-reset").onclick = () => this.resetSettings();
        this.element.querySelector("#naku-api-cancel").onclick = () => this.close();
    }

    saveSettings() {
        const siliconflowApiKey = this.element.querySelector("#siliconflow_api_key")?.value || "";
        const customApiKey = this.element.querySelector("#custom_api_key")?.value || "";
        const customApiUrl = this.element.querySelector("#custom_api_url")?.value || "https://api.siliconflow.cn/v1";

        // 保存到服务器（使用固定 ID）
        fetch("/naku_api_setting/save_api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                node_id: "default",  // 使用固定 ID，所有节点共享配置
                data: {
                    siliconflow_api_key: siliconflowApiKey,
                    custom_api_key: customApiKey,
                    custom_api_url: customApiUrl
                }
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                // 查找并更新节点显示（使用固定 ID）
                const node = app.graph._nodes.find(n => n.type === "NakuNode_APISetting");
                if (node && node.apiStringWidget) {
                    // 立即更新 widget 显示
                    const jsonStr = JSON.stringify({
                        siliconflow_api_key: siliconflowApiKey,
                        custom_api_key: customApiKey,
                        custom_api_url: customApiUrl
                    });
                    const encrypted = "NAKU_API_V1:" + btoa(unescape(encodeURIComponent(jsonStr)));
                    node.apiStringWidget.value = "✅ API 设置已完成\n\n" + encrypted;
                    node.apiStringWidget.bgcolor = "#1a331a";
                    node.setDirtyCanvas(true);
                }
                alert("✅ API 设置已保存！\n\n加密的 API String 已显示在节点文本框中。\n\n将 api_string 输出连接到其他 API 节点即可使用。");
                this.close();
            } else {
                alert("保存失败：" + (data.message || "未知错误"));
            }
        })
        .catch(err => {
            console.error("[NakuNode API] 保存失败:", err);
            alert("保存失败：" + err.message);
        });
    }

    resetSettings() {
        if (!confirm("⚠️ 确定要重置当前节点的 API 设置吗？\n\n这将清除所有已保存的 API 密钥！")) {
            return;
        }

        fetch("/naku_api_setting/reset_api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                node_id: this.nodeId
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                // 触发节点更新
                if (this.nodeId) {
                    const node = app.graph.getNodeById(parseInt(this.nodeId));
                    if (node) {
                        if (node.onExecute) {
                            node.onExecute();
                        }
                        node.setDirtyCanvas(true);
                    }
                }
                alert("✅ API 设置已重置！");
                this.siliconflowApiKey = "";
                this.customApiKey = "";
                this.customApiUrl = "https://api.siliconflow.cn/v1";
                this.renderContent();
            } else {
                alert("重置失败：" + (data.message || "未知错误"));
            }
        })
        .catch(err => {
            console.error("[NakuNode API] 重置失败:", err);
            alert("重置失败：" + err.message);
        });
    }
}

// 注册节点扩展
app.registerExtension({
    name: "NakuNode.APISetting",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "NakuNode_APISetting") {
            // 添加设置按钮
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = originalOnNodeCreated?.apply(this, arguments);
                
                // 添加一个文本框来显示 api_string 输出
                const apiStringWidget = this.addWidget("text", "api_string", "点击运行队列提示...", () => {}, {});
                apiStringWidget.options = { readonly: true, multiline: true, height: 80 };
                
                // 保存 widget 引用以便后续更新
                this.apiStringWidget = apiStringWidget;
                
                // 添加定时器，定期从 API 获取数据更新显示（使用固定 ID "default"）
                this.apiPollInterval = setInterval(() => {
                    fetch(`/naku_api_setting/get_api/default`)
                        .then(res => res.json())
                        .then(data => {
                            if (this.apiStringWidget) {
                                if (data.status === "success" && data.data) {
                                    const hasSfKey = data.data.siliconflow_api_key && data.data.siliconflow_api_key.trim();
                                    const hasCustomKey = data.data.custom_api_key && data.data.custom_api_key.trim();
                                    
                                    if (hasSfKey || hasCustomKey) {
                                        // 已配置 API，生成加密字符串
                                        const jsonStr = JSON.stringify(data.data);
                                        const encrypted = "NAKU_API_V1:" + btoa(unescape(encodeURIComponent(jsonStr)));
                                        this.apiStringWidget.value = "✅ API 设置已完成\n\n" + encrypted.substring(0, 60) + "...";
                                        this.apiStringWidget.bgcolor = "#1a331a";
                                    } else {
                                        this.apiStringWidget.value = "⚠️ 未配置 API\n请点击上方按钮设置";
                                        this.apiStringWidget.bgcolor = "#331a1a";
                                    }
                                    this.setDirtyCanvas(true);
                                } else {
                                    this.apiStringWidget.value = "⚠️ 未配置 API\n请点击上方按钮设置";
                                    this.apiStringWidget.bgcolor = "#331a1a";
                                }
                            }
                        })
                        .catch(err => {
                            console.error("[NakuNode API] 轮询失败:", err);
                        });
                }, 2000); // 每 2 秒轮询一次
                
                // 添加 Setting 按钮
                const settingBtn = this.addWidget("button", "⚙️ API 设置", "setting", () => {
                    const dialog = new APISettingDialog();
                    dialog.show(this.id + "");
                });
                settingBtn.label = "⚙️ API 设置";
                
                // 添加 Reset 按钮
                const resetBtn = this.addWidget("button", "🔄 重置设置", "reset", () => {
                    if (confirm("⚠️ 确定要重置当前节点的 API 设置吗？\n\n这将清除所有已保存的 API 密钥！")) {
                        fetch("/naku_api_setting/reset_api", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                node_id: this.id + ""
                            })
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                if (this.onExecute) {
                                    this.onExecute();
                                }
                                this.setDirtyCanvas(true);
                                alert("✅ API 设置已重置！");
                            } else {
                                alert("重置失败：" + (data.message || "未知错误"));
                            }
                        })
                        .catch(err => {
                            console.error("[NakuNode API] 重置失败:", err);
                            alert("重置失败：" + err.message);
                        });
                    }
                });
                resetBtn.label = "🔄 重置设置";
                
                // 节点被移除时清理定时器
                const originalOnRemoved = this.onRemoved;
                this.onRemoved = function() {
                    if (this.apiPollInterval) {
                        clearInterval(this.apiPollInterval);
                    }
                    return originalOnRemoved?.apply(this, arguments);
                };
                
                return result;
            };

            // 节点执行时更新 UI - 显示 api_string 输出值
            const originalOnExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                const result = originalOnExecuted?.apply(this, arguments);
                
                console.log("[NakuNode API] onExecuted message:", JSON.stringify(message));
                
                // 执行后从 API 获取最新的加密字符串
                if (this.id !== undefined && this.apiStringWidget) {
                    fetch(`/naku_api_setting/get_api/${this.id}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success" && data.data) {
                                // 生成加密字符串并显示
                                const apiData = data.data;
                                const jsonStr = JSON.stringify(apiData);
                                const encrypted = "NAKU_API_V1:" + btoa(unescape(encodeURIComponent(jsonStr)));
                                
                                if (this.apiStringWidget) {
                                    this.apiStringWidget.value = encrypted;
                                    this.apiStringWidget.bgcolor = "#1a331a";
                                    console.log("[NakuNode API] api_string 输出:", encrypted.substring(0, 50) + "...");
                                }
                            }
                        })
                        .catch(err => {
                            console.error("[NakuNode API] 获取 API 数据失败:", err);
                        });
                }
                
                return result;
            };
            
            // 添加自定义绘制，在节点上显示状态
            const originalOnDraw = nodeType.prototype.onDraw;
            nodeType.prototype.onDraw = function(ctx, node) {
                const result = originalOnDraw?.apply(this, arguments);
                
                // 在节点上绘制状态信息
                const nodeId = this.id + "";
                fetch(`/naku_api_setting/get_api/${nodeId}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === "success" && data.data && data.data.siliconflow_api_key) {
                            // 已配置 API Key，显示绿色状态
                            ctx.fillStyle = "#4CAF50";
                            ctx.font = "12px Arial";
                            ctx.fillText("● API 已配置", 10, -10);
                        } else {
                            // 未配置 API Key，显示黄色状态
                            ctx.fillStyle = "#FFC107";
                            ctx.font = "12px Arial";
                            ctx.fillText("● 点击设置 API", 10, -10);
                        }
                    })
                    .catch(() => {});
                
                return result;
            };
        }
    }
});

// 导出对话框类供其他模块使用
export { APISettingDialog };
