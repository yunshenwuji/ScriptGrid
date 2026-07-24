/**
 * 述格 (ScriptGrid) - 使用说明模块
 * 负责使用说明的懒加载、渲染与语言切换重渲染
 * 结构对称于 ChangelogViewer，复用现有模态框与国际化基础设施
 */

class UsageGuideViewer {
    constructor(languageManager) {
        this.languageManager = languageManager;
        this.usageData = null;
        this.dataLoaded = false;
        this._loading = false;
        this.modalInstance = null;
        this.triggerBtn = null;
        this.modalBody = null;
    }

    /**
     * 初始化模块
     */
    init() {
        this.triggerBtn = document.getElementById('usageGuideBtn');
        this.modalBody = document.getElementById('usageModalBody');

        // 初始化 Bootstrap Modal 实例（防御 Bootstrap 未加载的情况）
        const modalEl = document.getElementById('usageModal');
        if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            this.modalInstance = new bootstrap.Modal(modalEl);
        }

        // 绑定帮助按钮点击事件
        if (this.triggerBtn) {
            this.triggerBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal();
            });
        }
    }

    /**
     * 懒加载使用说明数据
     */
    async loadData() {
        if (this.dataLoaded || this._loading) return;
        this._loading = true;

        try {
            const response = await fetch('/static/data/usage.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.usageData = await response.json();
            this.dataLoaded = true;
        } catch (error) {
            console.error('加载使用说明失败:', error);
            this.usageData = null;
        } finally {
            this._loading = false;
        }
    }

    /**
     * 打开模态框
     */
    async openModal() {
        if (!this.modalInstance) return;

        // 显示加载状态
        this.showLoading();

        // 打开模态框
        this.modalInstance.show();

        // 懒加载数据
        if (!this.dataLoaded) {
            await this.loadData();
        }

        // 渲染内容
        this.render();
    }

    /**
     * 渲染使用说明内容（手风琴布局）
     */
    render() {
        if (!this.modalBody || !this.languageManager) return;

        const lang = this.languageManager.currentLang;

        // 数据加载失败
        if (!this.usageData) {
            this.showError();
            return;
        }

        const sections = this.usageData.sections || [];
        if (sections.length === 0) {
            this.modalBody.innerHTML = `<p class="text-center text-muted">${this.escapeHtml(this.languageManager.getText('usageError'))}</p>`;
            return;
        }

        let html = '<div class="accordion usage-accordion" id="usageAccordion">';
        sections.forEach((section, index) => {
            const title = (section.title && (section.title[lang] || section.title['zh-CN'])) || '';
            const blocks = (section.body && (section.body[lang] || section.body['zh-CN'])) || [];
            const collapseId = `usageCollapse${index}`;
            const headingId = `usageHeading${index}`;
            const expanded = index === 0; // 默认展开第一节

            html += '<div class="accordion-item">';
            html += `   <h2 class="accordion-header" id="${headingId}">`;
            html += `       <button class="accordion-button${expanded ? '' : ' collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="${expanded}" aria-controls="${collapseId}">${this.escapeHtml(title)}</button>`;
            html += '   </h2>';
            html += `   <div id="${collapseId}" class="accordion-collapse collapse${expanded ? ' show' : ''}" aria-labelledby="${headingId}" data-bs-parent="#usageAccordion">`;
            html += '       <div class="accordion-body">';
            blocks.forEach(block => {
                html += this.renderBlock(block);
            });
            html += '       </div>';
            html += '   </div>';
            html += '</div>';
        });
        html += '</div>';

        this.modalBody.innerHTML = html;
    }

    /**
     * 渲染单个内容块（支持 p / list / table）
     */
    renderBlock(block) {
        if (!block || !block.type) return '';

        switch (block.type) {
            case 'p':
                return `<p class="usage-p">${this.escapeHtml(block.text || '')}</p>`;

            case 'list': {
                const items = block.items || [];
                let h = '<ul class="usage-list">';
                items.forEach(item => {
                    h += `<li>${this.escapeHtml(item)}</li>`;
                });
                h += '</ul>';
                return h;
            }

            case 'table': {
                const headers = block.headers || [];
                const rows = block.rows || [];
                let h = '<div class="table-responsive"><table class="table table-sm usage-table">';
                if (headers.length) {
                    h += '<thead><tr>';
                    headers.forEach(hd => {
                        h += `<th scope="col">${this.escapeHtml(hd)}</th>`;
                    });
                    h += '</tr></thead>';
                }
                h += '<tbody>';
                rows.forEach(row => {
                    h += '<tr>';
                    (row || []).forEach((cell, ci) => {
                        if (ci === 0) {
                            h += `<th scope="row">${this.escapeHtml(cell)}</th>`;
                        } else {
                            h += `<td>${this.escapeHtml(cell)}</td>`;
                        }
                    });
                    h += '</tr>';
                });
                h += '</tbody></table></div>';
                return h;
            }

            default:
                return '';
        }
    }

    /**
     * 显示加载中状态
     */
    showLoading() {
        if (this.modalBody) {
            this.modalBody.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">${this.languageManager.getText('usageLoading')}</p>
                </div>
            `;
        }
    }

    /**
     * 显示错误状态
     */
    showError() {
        if (this.modalBody) {
            this.modalBody.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-danger">${this.languageManager.getText('usageError')}</p>
                </div>
            `;
        }
    }

    /**
     * HTML 转义，防止 XSS
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * 语言切换时重新渲染（如果模态框已打开）
     */
    onLanguageChange() {
        const modalEl = document.getElementById('usageModal');
        if (modalEl && modalEl.classList.contains('show')) {
            this.render();
        }
    }
}
