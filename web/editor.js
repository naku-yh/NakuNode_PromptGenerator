// NakuNode-文本修改节点的前端实现

import { app } from "/scripts/app.js";

// 定义节点样式和行为
app.registerExtension({
    name: "NakuNode.TextEditor",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 检查是否是我们要扩展的节点
        if (nodeData.name === "NakuNodeTextEditor") {
            // 保存原始的onNodeCreated方法
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            // 扩展节点原型
            nodeType.prototype.onNodeCreated = function() {
                // 调用原始方法
                const result = onNodeCreated?.apply(this, arguments);
                
                // 添加按钮小部件
                this.addWidget("button", "编辑", null, this.openEditor.bind(this));
                this.addWidget("button", "完成", null, this.completeEditing.bind(this));
                
                return result;
            };
            
            // 打开编辑器方法
            nodeType.prototype.openEditor = async function() {
                // 首先尝试获取已编辑的文本
                let originalText = '';
                try {
                    const response = await fetch(`/naku_text_editor/get_text/${this.id}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.text !== null) {
                            originalText = data.text;
                        }
                    }
                } catch (error) {
                    console.warn("无法获取已编辑的文本:", error);
                }

                // 如果没有已编辑的文本，尝试从widgets获取原始文本
                if (!originalText && this.widgets) {
                    for (let i = 0; i < this.widgets.length; i++) {
                        const widget = this.widgets[i];
                        if (widget.name === "text_input") {
                            // 尝试获取widget的值，如果为空则尝试其他方法
                            originalText = widget.value || "";

                            // 如果widget.value为空，可能是由于输入连接导致的
                            if (!originalText && typeof widget.computeAsync === 'function') {
                                // 如果有异步计算函数，尝试调用它
                                try {
                                    const computedValue = widget.computeAsync();
                                    if (computedValue && typeof computedValue.then === 'function') {
                                        // 如果是Promise，等待结果
                                        computedValue.then(value => {
                                            if (value) {
                                                originalText = value.toString();
                                                // 更新编辑器中的文本
                                                if (readOnlyTextArea) {
                                                    readOnlyTextArea.value = originalText;
                                                }
                                            }
                                        }).catch(err => console.error("Error computing widget value:", err));
                                    } else if (computedValue) {
                                        originalText = computedValue.toString();
                                    }
                                } catch (err) {
                                    console.error("Error getting widget value:", err);
                                }
                            }

                            break;
                        }
                    }
                }

                // 如果仍然没有文本，尝试从节点的其他属性获取
                if (!originalText) {
                    // 检查是否有从后端传来的current_text
                    if (this.widgets && this.widgets.length > 0) {
                        for (let i = 0; i < this.widgets.length; i++) {
                            const widget = this.widgets[i];
                            // 查找可能包含输入文本的widget
                            if (widget.type === "customtext" || widget.type === "text" ||
                                (widget.name && widget.name.includes("input"))) {
                                if (widget.value) {
                                    originalText = widget.value;
                                    break;
                                }
                            }
                        }
                    }
                }

                // 最重要的修复：检查是否有最近的UI更新数据
                // ComfyUI通常会将UI数据存储在节点的properties或widgets中
                if (!originalText && this.properties && this.properties.current_text) {
                    originalText = this.properties.current_text;
                }

                // 如果还是没有找到文本，尝试从节点的其他可能来源获取
                if (!originalText) {
                    // 检查是否有历史记录或缓存的文本
                    if (this.outputs && this.outputs.length > 0) {
                        // 检查输出端口是否有文本
                        const output = this.outputs[0];
                        if (output && output.value) {
                            originalText = output.value;
                        }
                    }
                }

                // 创建编辑器弹窗，传递原始文本
                this.createEditorPopup(originalText);
            };
            
            // 完成编辑方法
            nodeType.prototype.completeEditing = function() {
                // 这里可以添加完成编辑的逻辑
                console.log("完成编辑");
            };
            
            // 创建编辑器弹窗方法
            nodeType.prototype.createEditorPopup = function(originalText) {
                // 创建遮罩层
                const overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '100%';
                overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
                overlay.style.zIndex = '9999';
                overlay.style.display = 'flex';
                overlay.style.justifyContent = 'center';
                overlay.style.alignItems = 'center';
                
                // 创建编辑器容器
                const editorContainer = document.createElement('div');
                editorContainer.style.width = '900px';  // 3倍大小 (300*3)
                editorContainer.style.height = '600px'; // 3倍大小 (200*3)
                editorContainer.style.backgroundColor = '#36393F'; // 深色主题
                editorContainer.style.borderRadius = '8px';
                editorContainer.style.padding = '15px';
                editorContainer.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
                editorContainer.style.display = 'flex';
                editorContainer.style.flexDirection = 'column';
                editorContainer.style.color = 'white'; // 白色文字
                
                // 创建标题
                const title = document.createElement('div');
                title.textContent = '文本编辑器';
                title.style.fontSize = '18px';
                title.style.fontWeight = 'bold';
                title.style.marginBottom = '10px';
                title.style.textAlign = 'center';
                
                // 创建说明文字
                const info = document.createElement('div');
                info.textContent = '上方文本框：显示原始文本（只读） | 下方文本框：编辑文本（可编辑）';
                info.style.fontSize = '14px';
                info.style.marginBottom = '10px';
                info.style.textAlign = 'center';
                info.style.color = '#AAAAAA';
                
                // 创建上方只读文本框容器
                const readOnlyContainer = document.createElement('div');
                readOnlyContainer.style.marginBottom = '10px';
                
                const readOnlyLabel = document.createElement('div');
                readOnlyLabel.textContent = '原始文本 (只读):';
                readOnlyLabel.style.marginBottom = '5px';
                readOnlyLabel.style.fontWeight = 'bold';
                
                // 上方只读文本框
                const readOnlyTextArea = document.createElement('textarea');
                readOnlyTextArea.readOnly = true;
                readOnlyTextArea.style.width = '100%';
                readOnlyTextArea.style.height = '40%';
                readOnlyTextArea.style.padding = '8px';
                readOnlyTextArea.style.border = '1px solid #40444B';
                readOnlyTextArea.style.borderRadius = '4px';
                readOnlyTextArea.style.resize = 'none';
                readOnlyTextArea.style.backgroundColor = '#2F3136'; // 更深的只读背景
                readOnlyTextArea.style.color = 'white';
                readOnlyTextArea.style.fontFamily = 'monospace';
                readOnlyTextArea.style.fontSize = '14px';
                readOnlyTextArea.style.lineHeight = '1.4';
                
                readOnlyTextArea.value = originalText || '';
                
                readOnlyContainer.appendChild(readOnlyLabel);
                readOnlyContainer.appendChild(readOnlyTextArea);
                
                // 创建下方可编辑文本框容器
                const editableContainer = document.createElement('div');
                editableContainer.style.marginBottom = '10px';
                
                const editableLabel = document.createElement('div');
                editableLabel.textContent = '编辑文本 (可编辑):';
                editableLabel.style.marginBottom = '5px';
                editableLabel.style.fontWeight = 'bold';
                
                // 下方可编辑文本框
                const editableTextArea = document.createElement('textarea');
                editableTextArea.style.width = '100%';
                editableTextArea.style.height = '40%';
                editableTextArea.style.padding = '8px';
                editableTextArea.style.border = '1px solid #40444B';
                editableTextArea.style.borderRadius = '4px';
                editableTextArea.style.resize = 'none';
                editableTextArea.style.backgroundColor = '#202225'; // 深色背景
                editableTextArea.style.color = 'white';
                editableTextArea.style.fontFamily = 'monospace';
                editableTextArea.style.fontSize = '14px';
                editableTextArea.style.lineHeight = '1.4';
                
                // 如果已经有编辑过的文本，使用编辑过的文本
                if (this.editedText !== undefined) {
                    editableTextArea.value = this.editedText;
                } else {
                    // 否则默认填入原始文本，方便用户编辑
                    editableTextArea.value = originalText || '';
                }
                
                editableContainer.appendChild(editableLabel);
                editableContainer.appendChild(editableTextArea);
                
                // 创建按钮容器
                const buttonContainer = document.createElement('div');
                buttonContainer.style.display = 'flex';
                buttonContainer.style.gap = '10px';
                buttonContainer.style.justifyContent = 'space-between';
                
                // 创建撤销按钮
                const cancelButton = document.createElement('button');
                cancelButton.textContent = '撤销';
                cancelButton.style.height = '25px';
                cancelButton.style.width = '70px';
                cancelButton.style.padding = '5px 10px';
                cancelButton.style.border = '1px solid #40444B';
                cancelButton.style.borderRadius = '4px';
                cancelButton.style.backgroundColor = '#4F545C';
                cancelButton.style.color = 'white';
                cancelButton.style.cursor = 'pointer';
                cancelButton.onmouseover = () => cancelButton.style.backgroundColor = '#5E6269';
                cancelButton.onmouseout = () => cancelButton.style.backgroundColor = '#4F545C';
                cancelButton.onclick = () => {
                    document.body.removeChild(overlay);
                };
                
                // 创建完成按钮
                const completeButton = document.createElement('button');
                completeButton.textContent = '完成';
                completeButton.style.height = '25px';
                completeButton.style.width = '70px';
                completeButton.style.padding = '5px 10px';
                completeButton.style.border = '1px solid #40444B';
                completeButton.style.borderRadius = '4px';
                completeButton.style.backgroundColor = '#43B581'; // 绿色
                completeButton.style.color = 'white';
                completeButton.style.cursor = 'pointer';
                completeButton.onmouseover = () => completeButton.style.backgroundColor = '#3CA374';
                completeButton.onmouseout = () => completeButton.style.backgroundColor = '#43B581';
                completeButton.onclick = () => {
                    // 获取下方编辑框的文本
                    const newText = editableTextArea.value;
                    
                    // 更新节点的输出
                    this.applyEditedText(newText);
                    
                    // 移除弹窗
                    document.body.removeChild(overlay);
                };
                
                // 添加按钮到容器
                buttonContainer.appendChild(cancelButton);
                buttonContainer.appendChild(completeButton);
                
                // 组装界面
                editorContainer.appendChild(title);
                editorContainer.appendChild(info);
                editorContainer.appendChild(readOnlyContainer);
                editorContainer.appendChild(editableContainer);
                editorContainer.appendChild(buttonContainer);
                overlay.appendChild(editorContainer);
                
                // 添加到页面
                document.body.appendChild(overlay);
            };
            
            // 应用编辑后的文本
            nodeType.prototype.applyEditedText = async function(editedText) {
                // 保存编辑后的文本到后端
                try {
                    const response = await fetch('/naku_text_editor/update_text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            node_id: this.id.toString(),
                            edited_text: editedText
                        })
                    });
                    
                    if (response.ok) {
                        console.log("文本已成功发送到后端:", editedText);
                        
                        // 保存到本地以便下次使用
                        this.editedText = editedText;
                        
                        // 重新执行节点以更新输出
                        app.graph.change();
                    } else {
                        console.error("发送文本到后端失败:", response.statusText);
                    }
                } catch (error) {
                    console.error("发送文本到后端时出错:", error);
                }
            };
        }
    }
});