/**
 * 述格 (ScriptGrid) - 主应用模块
 * 负责应用初始化、事件绑定和核心业务逻辑
 */

// 全局变量
let languageManager;
let taskStateManager;
let pageCloseHandler;
let supportedLanguages = {};

// DOM元素
let fileInput, conversionTypeSelect, convertButton, form, messageArea, loadingIndicator;
let languageSelectionContainer, targetLanguageSelect;
let fileExtension = '';

/**
 * 初始化应用
 */
function initializeApp() {
    // 获取DOM元素
    fileInput = document.getElementById('subtitleFile');
    conversionTypeSelect = document.getElementById('conversionType');
    convertButton = document.getElementById('convertBtn');
    form = document.getElementById('converterForm');
    messageArea = document.getElementById('messageArea');
    loadingIndicator = document.getElementById('loadingIndicator');
    languageSelectionContainer = document.getElementById('languageSelectionContainer');
    targetLanguageSelect = document.getElementById('targetLanguage');
    
    // 初始化语言管理器
    languageManager = new LanguageManager();
    
    // 初始化任务状态管理器
    taskStateManager = new TaskStateManager();
    
    // 初始化页面关闭确认处理器
    pageCloseHandler = new PageCloseHandler(taskStateManager, languageManager);
    pageCloseHandler.initialize();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 加载支持的语言列表
    loadSupportedLanguages();
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 文件选择事件监听器
    fileInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const fileName = file.name;
            fileExtension = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();

            // 重置并更新转换类型下拉框
            conversionTypeSelect.innerHTML = `<option value="" selected>${languageManager.getText('selectFile')}</option>`;
            conversionTypeSelect.disabled = false;

            const options = getConversionOptions()[fileExtension];
            if (options && options.length > 0) {
                options.forEach(option => {
                    const opt = document.createElement('option');
                    opt.value = option.value;
                    opt.textContent = option.getText();
                    conversionTypeSelect.appendChild(opt);
                });
                convertButton.disabled = false;
                hideMessage();
                
                // 检查是否为SUP文件
                if (fileExtension === '.sup') {
                    languageSelectionContainer.style.display = 'block';
                } else {
                    languageSelectionContainer.style.display = 'none';
                }
            } else {
                conversionTypeSelect.disabled = true;
                convertButton.disabled = true;
                languageSelectionContainer.style.display = 'none';
                showMessage(languageManager.getText('unsupportedFile'), 'warning');
            }
        } else {
            // 如果没有选择文件，重置状态
            conversionTypeSelect.innerHTML = `<option value="" selected>${languageManager.getText('selectFile')}</option>`;
            conversionTypeSelect.disabled = true;
            convertButton.disabled = true;
            languageSelectionContainer.style.display = 'none';
            hideMessage();
        }
    });

    // 表单提交事件监听器
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const file = fileInput.files[0];
        const conversionType = conversionTypeSelect.value;

        if (!file) {
            showMessage(languageManager.getText('selectFileWarning'), 'warning');
            return;
        }

        if (!conversionType) {
            showMessage(languageManager.getText('selectTypeWarning'), 'warning');
            return;
        }

        // 启动任务状态管理
        const isSupConversion = conversionType.startsWith('sup_') || 
                               (fileExtension === '.sup' && conversionType === 'auto_narration_timing');
        const taskType = isSupConversion ? 'sup_conversion' : 'general_conversion';
        taskStateManager.startTask(taskType);
        console.log('开始转换任务:', taskType);

        // 准备FormData用于文件上传
        const formData = new FormData();
        formData.append('file', file);
        formData.append('conversion_type', conversionType);
        
        // 如果是SUP转换，添加语言参数
        if (isSupConversion) {
            const targetLanguage = targetLanguageSelect.value || 'auto';
            formData.append('target_language', targetLanguage);
        }
        
        // 当转换类型为 auto_narration_timing 时，传递占位符文本
        if (conversionType === 'auto_narration_timing') {
            formData.append('placeholder_text', languages[languageManager.currentLang].narration_placeholder);
        }

        // 显示加载指示器，禁用表单控件
        showLoading(true);
        fileInput.disabled = true;
        conversionTypeSelect.disabled = true;
        convertButton.disabled = true;

        // 检查是否为SUP转换
        if (isSupConversion) {
            showSupProgress(true);
            taskStateManager.updatePhase('file_upload');
        }

        try {
            // 发送POST请求到后端API
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json') && isSupConversion) {
                    // SUP转换：异步模式
                    const result = await response.json();
                    const taskId = result.task_id;
                    
                    console.log('获取到SUP转换任务ID:', taskId);
                    
                    if (taskId) {
                        console.log('开始监听任务进度:', taskId);
                        taskStateManager.updatePhase('ocr_processing');
                        startProgressMonitoring(taskId);
                    } else {
                        throw new Error('未获取到任务ID');
                    }
                } else {
                    // 其他转换：同步模式
                    taskStateManager.updatePhase('download');
                    
                    // 转换成功，处理文件下载
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    
                    // 根据转换类型设置默认文件名后缀
                    let fileExt = '.xlsx';
                    if (conversionType === 'ass_to_srt' || conversionType === 'xlsx_to_srt' || 
                        conversionType === 'sup_to_srt' || conversionType === 'auto_narration_timing') {
                        fileExt = '.srt';
                    }
                    link.download = file.name.substring(0, file.name.lastIndexOf('.')) + fileExt;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(downloadUrl);

                    showMessage(languageManager.getText('conversionComplete'), 'success');
                    taskStateManager.endTask();
                }
            } else {
                const errorText = await response.text();
                console.error('转换失败:', response.status, errorText);
                showMessage(`${languageManager.getText('conversionFailed')}: ${errorText || '服务器错误'}`, 'danger');
                taskStateManager.endTask();
            }
        } catch (error) {
            console.error('请求失败:', error);
            showMessage(`${languageManager.getText('conversionFailed')}: ${error.message}`, 'danger');
            taskStateManager.endTask();
        } finally {
            // 只有非-SUP转换才立即恢复控件
            if (!isSupConversion) {
                showLoading(false);
                showSupProgress(false);
                fileInput.disabled = false;
                conversionTypeSelect.disabled = false;
                convertButton.disabled = false;
            }
        }
    });
}

/**
 * 加载支持的语言列表
 */
async function loadSupportedLanguages() {
    try {
        const response = await fetch('/api/supported-languages');
        const data = await response.json();
        if (data.success) {
            supportedLanguages = data.languages;
            updateLanguageOptions();
        } else {
            console.error('获取语言列表失败:', data.error);
            supportedLanguages = data.languages;
            updateLanguageOptions();
        }
    } catch (error) {
        console.error('加载语言列表失败:', error);
        // 使用默认语言列表
        supportedLanguages = {
            'zh-CN': {
                'auto': '自动检测',
                'ch_sim': '简体中文',
                'en': '英语'
            },
            'en': {
                'auto': 'Auto Detect',
                'ch_sim': 'Simplified Chinese',
                'en': 'English'
            }
        };
        updateLanguageOptions();
    }
}

/**
 * 更新语言选择框的选项
 */
function updateLanguageOptions() {
    if (!languageManager || !targetLanguageSelect) return;
    
    const currentLang = languageManager.currentLang;
    const langs = supportedLanguages[currentLang] || supportedLanguages['zh-CN'] || {};
    
    const currentValue = targetLanguageSelect.value;
    targetLanguageSelect.innerHTML = '';
    
    Object.entries(langs).forEach(([code, name]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        if (code === currentValue || (code === 'auto' && !currentValue)) {
            option.selected = true;
        }
        targetLanguageSelect.appendChild(option);
    });
}

/**
 * 定义转换类型选项
 */
function getConversionOptions() {
    return {
        '.ass': [
            { value: 'ass_to_srt', getText: () => languageManager.getText('assToSrt') },
            { value: 'subtitle_to_excel', getText: () => languageManager.getText('subtitleToExcel') },
            { value: 'auto_narration_timing', getText: () => languageManager.getText('auto_narration_timing') }
        ],
        '.srt': [
            { value: 'subtitle_to_excel', getText: () => languageManager.getText('srtToExcel') },
            { value: 'auto_narration_timing', getText: () => languageManager.getText('auto_narration_timing') }
        ],
        '.xlsx': [
            { value: 'xlsx_to_srt', getText: () => languageManager.getText('xlsxToSrt') }
        ],
        '.sup': [
            { value: 'sup_to_srt', getText: () => languageManager.getText('supToSrt') },
            { value: 'sup_to_excel', getText: () => languageManager.getText('supToExcel') },
            { value: 'auto_narration_timing', getText: () => languageManager.getText('auto_narration_timing') }
        ]
    };
}

/**
 * 显示消息的辅助函数
 */
function showMessage(message, type = 'info') {
    messageArea.textContent = message;
    messageArea.className = `alert alert-${type}`;
    messageArea.style.display = 'block';
    
    if (type === 'success' || type === 'danger') {
        messageArea.setAttribute('aria-live', 'assertive');
        setTimeout(() => {
            messageArea.removeAttribute('aria-live');
        }, 2000);
    }
    
    if (type === 'success') {
        setTimeout(() => {
            hideMessage();
        }, 10000);
    }
}

/**
 * 隐藏消息的辅助函数
 */
function hideMessage() {
    messageArea.style.display = 'none';
}

/**
 * 控制加载指示器显示
 */
function showLoading(isLoading) {
    if (isLoading) {
        loadingIndicator.style.display = 'block';
    } else {
        loadingIndicator.style.display = 'none';
    }
}

// ==================== 调试工具函数 ====================

// 为开发者提供的全局调试接口
window.ScriptGridDebug = {
    getTaskStatus: () => {
        if (taskStateManager) {
            return taskStateManager.getStatusInfo();
        }
        return { error: 'TaskStateManager 未初始化' };
    },
    
    startTestTask: (type = 'test') => {
        if (taskStateManager) {
            taskStateManager.startTask(type);
            console.log('测试任务已启动:', type);
            return true;
        }
        return false;
    },
    
    endTestTask: () => {
        if (taskStateManager) {
            taskStateManager.endTask();
            console.log('测试任务已结束');
            return true;
        }
        return false;
    },
    
    testConfirm: () => {
        if (pageCloseHandler) {
            return pageCloseHandler.testConfirm();
        }
        return false;
    },
    
    getConfirmMessage: () => {
        if (taskStateManager) {
            return taskStateManager.getConfirmMessage();
        }
        return null;
    }
};

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});
