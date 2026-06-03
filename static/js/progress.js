/**
 * 述格 (ScriptGrid) - 进度显示模块
 * 处理SUP转换进度显示和监听
 */

/**
 * 显示/隐藏SUP进度面板
 */
function showSupProgress(show) {
    const supProgress = document.getElementById('supProgress');
    if (supProgress) {
        supProgress.style.display = show ? 'block' : 'none';
    }
}

/**
 * 更新SUP进度显示
 */
function updateSupProgress(current, total, message, percentage, data = {}) {
    const progressBar = document.getElementById('progressBar');
    const progressMessage = document.getElementById('progressMessage');
    const phaseTitle = document.getElementById('phaseTitle');
    const frameProgress = document.getElementById('frameProgress');
    const subtitleCount = document.getElementById('subtitleCount');
    
    // 更新进度条
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = percentage + '%';
    }
    
    // 更新阶段标题
    if (phaseTitle && data.phase) {
        const currentLang = languageManager.currentLang;
        const phaseText = languages[currentLang].phases[data.phase] || message;
        phaseTitle.textContent = phaseText;
    }
    
    // 更新帧进度
    if (frameProgress && data.current_frame && data.total_frames) {
        frameProgress.textContent = `${data.current_frame} / ${data.total_frames}`;
    }
    
    // 更新字幕数量
    if (subtitleCount) {
        const count = data.subtitle_count || 0;
        console.log('更新字幕数量:', count, '来源数据:', data);
        const currentLang = languageManager.currentLang;
        const countText = currentLang === 'zh-CN' ? `${count} 条` : `${count} items`;
        subtitleCount.textContent = countText;
        console.log('字幕数量显示文本:', countText);
    }
    
    // 更新详细消息（对后端消息进行国际化处理）
    if (progressMessage) {
        let localizedMessage = message;
        
        // 检查是否包含"正在处理第"文本，如果包含则替换为本地化文本
        if (message.includes('正在处理第') && data.current_frame && data.total_frames) {
            const currentLang = languageManager.currentLang;
            const template = languages[currentLang].supProgress;
            localizedMessage = template.replace('{current}', data.current_frame).replace('{total}', data.total_frames);
        }
        // 检查是否包含"解析完成！共提取到"文本，如果包含则替换为本地化文本
        else if (message.includes('解析完成！共提取到') && data.subtitle_count !== undefined) {
            const currentLang = languageManager.currentLang;
            const template = languages[currentLang].supComplete;
            localizedMessage = template.replace('{count}', data.subtitle_count);
        }
        
        progressMessage.textContent = localizedMessage;
    }
}

/**
 * 启动进度监听（Server-Sent Events）
 */
function startProgressMonitoring(taskId) {
    console.log('开始监听进度, 任务ID:', taskId);
    
    // 使用 Server-Sent Events 监听进度
    const eventSource = new EventSource(`/api/progress/${taskId}`);
    
    eventSource.onopen = function(event) {
        console.log('SSE连接已建立');
    };
    
    eventSource.onmessage = function(event) {
        try {
            console.log('收到进度数据:', event.data);
            const data = JSON.parse(event.data);
            
            if (data.status === 'processing' || data.status === 'starting') {
                console.log('更新进度:', data.percentage + '%', data.message);
                // 更新任务阶段
                if (data.phase && taskStateManager) {
                    taskStateManager.updatePhase(data.phase);
                }
                updateSupProgress(data.current, data.total, data.message, data.percentage, data);
            } else if (data.status === 'complete') {
                console.log('转换完成');
                // 更新最终阶段
                if (taskStateManager) {
                    taskStateManager.updatePhase('complete');
                }
                updateSupProgress(data.current, data.total, data.message, 100, data);
                eventSource.close();
                
                // 转换完成，自动下载文件
                setTimeout(async () => {
                    try {
                        const downloadResponse = await fetch(`/api/download/${taskId}`);
                        if (downloadResponse.ok) {
                            const blob = await downloadResponse.blob();
                            const downloadUrl = window.URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = downloadUrl;
                            
                            // 从后端进度事件中获取输出文件名（后端统一负责命名）
                            const filename = data.output_filename || 'output';
                            
                            link.download = filename;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            window.URL.revokeObjectURL(downloadUrl);
                            
                            showMessage(languageManager.getText('conversionComplete'), 'success');
                        } else {
                            throw new Error('下载文件失败');
                        }
                    } catch (error) {
                        console.error('下载错误:', error);
                        showMessage(`${languageManager.getText('conversionFailed')}: ${error.message}`, 'danger');
                    } finally {
                        // SUP转换完成，结束任务并恢复控件状态
                        if (taskStateManager) {
                            taskStateManager.endTask();
                        }
                        showLoading(false);
                        showSupProgress(false);
                        fileInput.disabled = false;
                        conversionTypeSelect.disabled = false;
                        convertButton.disabled = false;
                    }
                }, 500); // 等待500ms确保进度显示完成
                
            } else if (data.status === 'error') {
                console.error('Conversion error:', data.message);
                showMessage(`${languageManager.getText('conversionFailed')}: ${data.message}`, 'danger');
                eventSource.close();
                
                // SUP转换失败，结束任务并恢复控件状态
                if (taskStateManager) {
                    taskStateManager.endTask();
                }
                showLoading(false);
                showSupProgress(false);
                fileInput.disabled = false;
                conversionTypeSelect.disabled = false;
                convertButton.disabled = false;
            } else if (data.status === 'waiting') {
                console.log('等待任务开始...');
                // 更新任务阶段为等待
                if (taskStateManager) {
                    taskStateManager.updatePhase('waiting');
                }
            }
        } catch (e) {
            console.error('Error parsing progress data:', e);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('Progress monitoring error:', event);
        eventSource.close();
        
        // 进度监听失败，结束任务并恢复控件状态
        if (taskStateManager) {
            taskStateManager.endTask();
        }
        showMessage(`${languageManager.getText('conversionFailed')}: 进度监听失败`, 'danger');
        showLoading(false);
        showSupProgress(false);
        fileInput.disabled = false;
        conversionTypeSelect.disabled = false;
        convertButton.disabled = false;
    };
}
