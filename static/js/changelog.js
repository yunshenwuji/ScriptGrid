/**
 * 述格 (ScriptGrid) - 更新日志模块
 * 负责更新日志的懒加载、渲染、语言切换和"NEW"提醒
 */

class ChangelogViewer {
    constructor(languageManager) {
        this.languageManager = languageManager;
        this.changelogData = null;
        this.dataLoaded = false;
        this._loading = false;
        this.modalInstance = null;
        this.versionBadge = null;
        this.modalBody = null;
        this.storageKey = 'scriptgrid-changelog-viewed-version';
    }

    /**
     * 初始化模块
     */
    init() {
        this.versionBadge = document.getElementById('versionBadge');
        this.modalBody = document.getElementById('changelogModalBody');

        // 初始化 Bootstrap Modal 实例（防御 Bootstrap 未加载的情况）
        const modalEl = document.getElementById('changelogModal');
        if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            this.modalInstance = new bootstrap.Modal(modalEl);

            // 模态框打开后标记为已查看
            modalEl.addEventListener('shown.bs.modal', () => {
                try { this.markAsViewed(); } catch (e) { /* 静默 */ }
                this.hideNewBadge();
            });
        }

        // 绑定版本徽章点击事件
        if (this.versionBadge) {
            this.versionBadge.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal();
            });
        }

        // 从 HTML data-version 属性检查 NEW 标记（避免提前 fetch）
        const htmlVersion = this.versionBadge?.dataset.version;
        if (htmlVersion) {
            const viewedVersion = this._safeGetStorage(this.storageKey);
            if (!viewedVersion || this.compareVersions(htmlVersion, viewedVersion) > 0) {
                this.showNewBadge();
            }
        }
    }

    /**
     * 懒加载更新日志数据
     */
    async loadData() {
        if (this.dataLoaded || this._loading) return;
        this._loading = true;

        try {
            const response = await fetch('/static/data/changelog.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.changelogData = await response.json();
            this.dataLoaded = true;
            // 加载成功后同步更新版本徽章文字
            if (this.versionBadge && this.changelogData.current_version) {
                this.versionBadge.textContent = `v${this.changelogData.current_version}`;
            }
        } catch (error) {
            console.error('加载更新日志失败:', error);
            this.changelogData = null;
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
     * 渲染更新日志内容
     */
    render() {
        if (!this.modalBody || !this.languageManager) return;

        const lang = this.languageManager.currentLang;

        // 数据加载失败
        if (!this.changelogData) {
            this.showError();
            return;
        }

        const releases = this.changelogData.releases || [];
        if (releases.length === 0) {
            this.modalBody.innerHTML = `<p class="text-center text-muted">${this.escapeHtml(this.languageManager.getText('changelogEmpty'))}</p>`;
            return;
        }

        // 构建 HTML
        let html = '';
        releases.forEach((release, index) => {
            const changes = release.changes[lang] || release.changes['zh-CN'] || {};
            const isLatest = index === 0;

            html += '<div class="changelog-release">';
            html += '   <div class="changelog-release-header">';
            html += `       <span class="changelog-version">v${this.escapeHtml(String(release.version || ''))}</span>`;
            html += `       <span class="changelog-date">${this.escapeHtml(String(release.date || ''))}</span>`;
            if (isLatest) {
                html += `       <span class="badge bg-success changelog-latest-badge">${this.escapeHtml(this.languageManager.getText('changelogLatest'))}</span>`;
            }
            html += '   </div>';
            html += '   <div class="changelog-release-body">';

            // 新增
            if (changes.new && changes.new.length > 0) {
                html += this.renderSection('new', changes.new);
            }
            // 优化
            if (changes.improved && changes.improved.length > 0) {
                html += this.renderSection('improved', changes.improved);
            }
            // 修复
            if (changes.fixed && changes.fixed.length > 0) {
                html += this.renderSection('fixed', changes.fixed);
            }

            html += '   </div>';
            html += '</div>';
        });

        this.modalBody.innerHTML = html;
    }

    /**
     * 渲染单个分类区块
     */
    renderSection(type, items) {
        const labels = {
            new: this.languageManager.getText('changelogNew'),
            improved: this.languageManager.getText('changelogImproved'),
            fixed: this.languageManager.getText('changelogFixed')
        };

        // 使用内联 SVG 图标（含 aria-hidden 避免屏幕阅读器朗读路径数据）
        const svgs = {
            new: '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-circle-fill text-success" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3v-3z"/></svg>',
            improved: '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-lightning-charge-fill text-warning" viewBox="0 0 16 16"><path d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z"/></svg>',
            fixed: '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-bug-fill text-danger" viewBox="0 0 16 16"><path d="M4.978.855a.5.5 0 1 0-.956.29l.41 1.352A4.985 4.985 0 0 0 3 3.3c-.6 0-1.164.166-1.657.459L.706 1.293a.5.5 0 1 0-.707.707l.71.71A2.99 2.99 0 0 0 0 6.5v1A1.5 1.5 0 0 0 1.5 9H2v2.5a.5.5 0 0 0 .146.354l.854.853V13.5a.5.5 0 0 0 1 0V12h6v1.5a.5.5 0 0 0 1 0v-1.293l.854-.853A.5.5 0 0 0 12 11.5V9h.5A1.5 1.5 0 0 0 14 7.5v-1a2.99 2.99 0 0 0-.709-1.96l.71-.71a.5.5 0 1 0-.707-.707l-.71.71A3.49 3.49 0 0 0 11 3.3c-.337 0-.66.066-.962.187l.41-1.352a.5.5 0 1 0-.956-.29l-.472 1.557A3.73 3.73 0 0 0 8 3.5c-.555 0-1.078.121-1.55.337L5.978.855z"/></svg>'
        };

        let html = '<div class="changelog-section">';
        html += `    <h6 class="changelog-section-title">${svgs[type]} <span>${labels[type]}</span></h6>`;
        html += '    <ul class="changelog-item-list">';
        items.forEach(item => {
            html += `    <li>${this.escapeHtml(item)}</li>`;
        });
        html += '    </ul>';
        html += '</div>';

        return html;
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
                    <p class="mt-2 text-muted">${this.languageManager.getText('changelogLoading')}</p>
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
                    <p class="text-danger">${this.languageManager.getText('changelogError')}</p>
                </div>
            `;
        }
    }

    /**
     * 显示 NEW 标记
     */
    showNewBadge() {
        if (this.versionBadge) {
            this.versionBadge.classList.add('has-update');
        }
    }

    /**
     * 隐藏 NEW 标记
     */
    hideNewBadge() {
        if (this.versionBadge) {
            this.versionBadge.classList.remove('has-update');
        }
    }

    /**
     * 标记当前版本为已查看
     */
    markAsViewed() {
        if (this.changelogData && this.changelogData.current_version) {
            this._safeSetStorage(this.storageKey, this.changelogData.current_version);
        }
    }

    /**
     * 比较版本号 (返回: 1=v1>v2, 0=相等, -1=v1<v2)
     */
    compareVersions(v1, v2) {
        if (!v1 || !v2) return 0;
        const parts1 = v1.split('.').map(Number);
        const parts2 = v2.split('.').map(Number);
        const maxLen = Math.max(parts1.length, parts2.length);

        for (let i = 0; i < maxLen; i++) {
            const p1 = parts1[i] || 0;
            const p2 = parts2[i] || 0;
            if (p1 > p2) return 1;
            if (p1 < p2) return -1;
        }
        return 0;
    }

    /**
     * 安全的 localStorage 读取
     */
    _safeGetStorage(key) {
        try { return localStorage.getItem(key); } catch (e) { return null; }
    }

    /**
     * 安全的 localStorage 写入
     */
    _safeSetStorage(key, value) {
        try { localStorage.setItem(key, value); } catch (e) { /* 静默失败 */ }
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
        // 如果模态框正在显示，重新渲染内容
        const modalEl = document.getElementById('changelogModal');
        if (modalEl && modalEl.classList.contains('show')) {
            this.render();
        }
    }
}
