/**
 * 述格 (ScriptGrid) - 任务状态管理器
 * 管理转换任务的状态和页面关闭确认
 */

/**
 * 任务状态管理器类
 */
class TaskStateManager {
    constructor() {
        this.isTaskRunning = false;
        this.confirmOnLeave = false;
        this.taskType = null; // 当前任务类型
        this.currentPhase = null; // 当前任务阶段
    }
    
    // 开始任务
    startTask(taskType = 'general') {
        console.log('TaskStateManager: 开始任务 -', taskType);
        this.isTaskRunning = true;
        this.confirmOnLeave = true;
        this.taskType = taskType;
        this.currentPhase = 'starting';
    }
    
    // 结束任务
    endTask() {
        console.log('TaskStateManager: 结束任务 -', this.taskType);
        this.isTaskRunning = false;
        this.confirmOnLeave = false;
        this.taskType = null;
        this.currentPhase = null;
    }
    
    // 检查是否应该显示关闭确认
    shouldConfirmLeave() {
        return this.confirmOnLeave && this.isTaskRunning;
    }
    
    // 获取确认消息
    getConfirmMessage() {
        // 如果语言管理器存在，使用国际化文本
        if (typeof languageManager !== 'undefined' && languageManager) {
            return languageManager.getText('pageCloseConfirm');
        }
        
        // 默认中文消息
        return '正在进行文件转换，离开页面将中断任务。确定要离开吗？';
    }
    
    // 更新任务阶段
    updatePhase(phase) {
        console.log('TaskStateManager: 更新任务阶段 -', phase);
        this.currentPhase = phase;
    }
    
    // 获取当前状态信息
    getStatusInfo() {
        return {
            isTaskRunning: this.isTaskRunning,
            confirmOnLeave: this.confirmOnLeave,
            taskType: this.taskType,
            currentPhase: this.currentPhase
        };
    }
}
