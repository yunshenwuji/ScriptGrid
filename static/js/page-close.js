/**
 * 述格 (ScriptGrid) - 页面关闭确认处理器
 * 管理页面关闭时的确认逻辑
 */

/**
 * 页面关闭确认处理器类
 */
class PageCloseHandler {
    constructor(taskManager, languageManager) {
        this.taskManager = taskManager;
        this.languageManager = languageManager;
        this.isInitialized = false;
    }
    
    // 初始化处理器
    initialize() {
        if (this.isInitialized) {
            console.log('PageCloseHandler: 已初始化，跳过重复初始化');
            return;
        }
        
        console.log('PageCloseHandler: 初始化页面关闭确认处理器');
        this.bindEvents();
        this.isInitialized = true;
    }
    
    // 绑定事件监听
    bindEvents() {
        // 绑定 beforeunload 事件
        window.addEventListener('beforeunload', (event) => {
            return this.handleBeforeUnload(event);
        });
        
        // 绑定 unload 事件（清理）
        window.addEventListener('unload', () => {
            this.cleanup();
        });
        
        console.log('PageCloseHandler: 事件监听器已绑定');
    }
    
    // 处理页面关闭前事件
    handleBeforeUnload(event) {
        if (this.taskManager.shouldConfirmLeave()) {
            const confirmMessage = this.taskManager.getConfirmMessage();
            console.log('PageCloseHandler: 显示关闭确认 -', confirmMessage);
            
            // 标准做法：设置 returnValue 并返回字符串
            event.preventDefault();
            event.returnValue = confirmMessage;
            return confirmMessage;
        }
        
        console.log('PageCloseHandler: 允许正常关闭页面');
        // 任务未运行，允许正常关闭
        return undefined;
    }
    
    // 清理资源
    cleanup() {
        console.log('PageCloseHandler: 清理资源');
        // 页面卸载时清理任务状态
        if (this.taskManager) {
            this.taskManager.endTask();
        }
    }
    
    // 手动触发确认（用于调试）
    testConfirm() {
        if (this.taskManager.shouldConfirmLeave()) {
            const message = this.taskManager.getConfirmMessage();
            return confirm(message);
        }
        return true;
    }
}
