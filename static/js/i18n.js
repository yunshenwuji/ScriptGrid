/**
 * 述格 (ScriptGrid) - 国际化模块
 * 管理多语言数据包和语言切换功能
 */

// 语言数据包
const languages = {
    'zh-CN': {
        // 页面标题和主要内容
        pageTitle: '述格 (ScriptGrid)',
        mainHeading: '述格 (ScriptGrid)',
        
        // 表单相关
        fileLabel: '选择字幕文件',
        fileHelp: '支持 .ass, .srt, .xlsx, .sup 格式。',
        conversionLabel: '转换类型',
        selectFile: '请先选择文件',
        selectConversion: '请选择转换类型',
        convertButton: '开始处理',
        
        // 转换选项
        assToSrt: 'ASS 转 SRT (.ass -> .srt)',
        subtitleToExcel: '字幕转表格 (.ass -> .xlsx)',
        srtToExcel: '字幕转表格 (.srt -> .xlsx)',
        xlsxToSrt: '表格转字幕 (.xlsx -> .srt)',
        supToSrt: 'SUP 转 SRT (.sup -> .srt)',
        supToExcel: 'SUP 转表格 (.sup -> .xlsx)',
        
        // 语言选择
        languageLabel: '字幕语言',
        autoDetect: '自动检测',
        languageHelp: '如果自动检测不准确，可手动选择字幕语言。',
        languageAriaLabel: '选择字幕语言',
        
        // 状态消息
        processing: '处理中...',
        processingMessage: '处理中，请稍候...',
        conversionComplete: '转换完成，文件已开始下载。',
        conversionFailed: '转换失败',
        unsupportedFile: '不支持的文件类型。',
        selectFileWarning: '请选择一个文件。',
        selectTypeWarning: '请选择转换类型。',
        
        // 页脚内容
        footerDescription: '是一个专为口述影像创作者设计的便捷工具，支持口述稿在 Excel 格式和字幕格式之间的灵活转换。',
        feedbackText: '如果您在使用过程中遇到任何问题或有改进建议，欢迎在',
        githubProject: 'GitHub 项目',
        feedbackSuffix: '中提交 Issue，我们将积极响应并努力解决。',
        donationTitle: '如果喜欢述格，欢迎捐赠',
        donationText: '支付宝或微信扫码请我喝杯咖啡',
        teamWebsiteIntro: '想了解更多无障碍电影相关信息？',
        teamWebsiteFollow: '欢迎关注',
        teamWebsiteLink: '共感无障碍团队官网',
        
        // 语言切换
        langSwitchToEn: 'English',
        conversionAriaLabel: '选择转换类型',
        paymentQrAlt: '支付宝微信收款二维码',
        
        // SUP 转换进度提示
        supProcessing: 'SUP 文件转换中，请耐心等待...',
        supProgress: '正在处理第 {current} / {total} 帧...',
        supComplete: '转换完成！共处理 {count} 条字幕',
        
        // 口述稿自动打轴
        auto_narration_timing: '空白口述稿自动打轴',
        narration_placeholder: '请填写口述文本',
        
        // SUP 转换阶段
        phases: {
            file_parsing: '正在解析SUP文件...',
            language_detection: '正在检测字幕语言...',
            ocr_init: '正在初始化OCR引擎...',
            ocr_processing: '正在识别字幕内容...',
            timeline_parsing: '正在解析字幕时间轴...',
            complete: '转换完成！'
        },
        
        // 进度显示标签
        frameProgressLabel: '当前进度',
        subtitleCountLabel: '已识别字幕',
        
        // 页面关闭确认消息
        pageCloseConfirm: '正在进行文件转换，离开页面将中断任务。确定要离开吗？'
    },
    
    'en': {
        // 页面标题和主要内容
        pageTitle: 'ScriptGrid',
        mainHeading: 'ScriptGrid',
        
        // 表单相关
        fileLabel: 'Select Subtitle File',
        fileHelp: 'Supports .ass, .srt, .xlsx, .sup formats.',
        conversionLabel: 'Conversion Type',
        selectFile: 'Please select a file first',
        selectConversion: 'Please select conversion type',
        convertButton: 'Start Processing',
        
        // 转换选项
        assToSrt: 'ASS to SRT (.ass -> .srt)',
        subtitleToExcel: 'Subtitle to Excel (.ass -> .xlsx)',
        srtToExcel: 'Subtitle to Excel (.srt -> .xlsx)',
        xlsxToSrt: 'Excel to Subtitle (.xlsx -> .srt)',
        supToSrt: 'SUP to SRT (.sup -> .srt)',
        supToExcel: 'SUP to Excel (.sup -> .xlsx)',
        
        // 语言选择
        languageLabel: 'Subtitle Language',
        autoDetect: 'Auto Detect',
        languageHelp: 'If auto detection is inaccurate, you can manually select the subtitle language.',
        languageAriaLabel: 'Select Subtitle Language',
        
        // 状态消息
        processing: 'Processing...',
        processingMessage: 'Processing, please wait...',
        conversionComplete: 'Conversion completed, file download started.',
        conversionFailed: 'Conversion failed',
        unsupportedFile: 'Unsupported file type.',
        selectFileWarning: 'Please select a file.',
        selectTypeWarning: 'Please select conversion type.',
        
        // 页脚内容
        footerDescription: 'is a convenient tool designed for audio description creators, supporting flexible conversion between Excel format and subtitle format for descriptive scripts.',
        feedbackText: 'If you encounter any issues or have suggestions for improvement, please submit an Issue in the',
        githubProject: 'GitHub project',
        feedbackSuffix: ', and we will respond actively and work to resolve them.',
        donationTitle: 'If you like ScriptGrid, donations are welcome',
        donationText: 'Scan with Alipay or WeChat to buy me a coffee',
        teamWebsiteIntro: 'Want to learn more about accessible cinema?',
        teamWebsiteFollow: 'Visit the',
        teamWebsiteLink: 'Gonggan Accessibility Team Official Website',
        
        // 语言切换
        langSwitchToCn: '中文',
        conversionAriaLabel: 'Select Conversion Type',
        paymentQrAlt: 'Alipay and WeChat Payment QR Code',
        
        // SUP 转换进度提示
        supProcessing: 'Converting SUP file, please wait...',
        supProgress: 'Processing frame {current} / {total}...',
        supComplete: 'Conversion complete! Processed {count} subtitles',
        
        // Auto narration timing
        auto_narration_timing: 'Auto Narration Timing',
        narration_placeholder: 'Please enter narration text',
        
        // SUP 转换阶段
        phases: {
            file_parsing: 'Parsing SUP file...',
            language_detection: 'Detecting subtitle language...',
            ocr_init: 'Initializing OCR engine...',
            ocr_processing: 'Recognizing subtitle content...',
            timeline_parsing: 'Parsing subtitle timeline...',
            complete: 'Conversion complete!'
        },
        
        // 进度显示标签
        frameProgressLabel: 'Current Progress',
        subtitleCountLabel: 'Recognized Subtitles',
        
        // 页面关闭确认消息
        pageCloseConfirm: 'File conversion is in progress. Leaving the page will interrupt the task. Are you sure you want to leave?'
    }
};

/**
 * 语言管理类
 */
class LanguageManager {
    constructor() {
        this.currentLang = this.getStoredLanguage() || 'zh-CN';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateLanguage(this.currentLang);
        // 确保在初始化后更新语言选项
        setTimeout(() => {
            if (typeof updateLanguageOptions === 'function') {
                updateLanguageOptions();
            }
        }, 100);
    }
    
    getStoredLanguage() {
        return localStorage.getItem('scriptgrid-language');
    }
    
    setStoredLanguage(lang) {
        localStorage.setItem('scriptgrid-language', lang);
    }
    
    bindEvents() {
        const langSwitchBtn = document.getElementById('langSwitchBtn');
        if (langSwitchBtn) {
            langSwitchBtn.addEventListener('click', () => {
                this.switchLanguage();
            });
        }
    }
    
    switchLanguage() {
        const newLang = this.currentLang === 'zh-CN' ? 'en' : 'zh-CN';
        this.updateLanguage(newLang);
    }
    
    updateLanguage(lang) {
        this.currentLang = lang;
        this.setStoredLanguage(lang);
        
        // 更新HTML lang属性
        document.documentElement.lang = lang;
        
        // 更新页面标题
        document.title = languages[lang].pageTitle;
        
        // 更新所有带有data-i18n属性的元素
        this.updateElements();
        
        // 更新转换选项（如果有文件已选择）
        this.updateConversionOptionsText();
        
        // 更新语言切换按钮
        this.updateSwitchButton();
        
        // 更新语言选择框选项
        if (typeof updateLanguageOptions === 'function') {
            updateLanguageOptions();
        }
    }
    
    updateElements() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (languages[this.currentLang][key]) {
                element.textContent = languages[this.currentLang][key];
            }
        });
        
        // 更新aria-label属性
        const ariaElements = document.querySelectorAll('[data-i18n-aria]');
        ariaElements.forEach(element => {
            const key = element.getAttribute('data-i18n-aria');
            if (languages[this.currentLang][key]) {
                element.setAttribute('aria-label', languages[this.currentLang][key]);
            }
        });
        
        // 更新title属性
        const titleElements = document.querySelectorAll('[data-i18n-title]');
        titleElements.forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            if (languages[this.currentLang][key]) {
                element.setAttribute('title', languages[this.currentLang][key]);
            }
        });
        
        // 更新alt属性
        const altElements = document.querySelectorAll('[data-i18n-alt]');
        altElements.forEach(element => {
            const key = element.getAttribute('data-i18n-alt');
            if (languages[this.currentLang][key]) {
                element.setAttribute('alt', languages[this.currentLang][key]);
            }
        });
    }
    
    updateConversionOptionsText() {
        const conversionTypeSelect = document.getElementById('conversionType');
        if (conversionTypeSelect) {
            const selectedValue = conversionTypeSelect.value;
            
            // 更新默认选项文本
            const defaultOption = conversionTypeSelect.querySelector('option[value=""]');
            if (defaultOption) {
                defaultOption.textContent = selectedValue === '' ? 
                    languages[this.currentLang].selectFile : 
                    languages[this.currentLang].selectConversion;
            }
            
            // 更新其他选项的文本
            this.updateConversionOptionTexts();
        }
    }
    
    updateConversionOptionTexts() {
        const conversionTypeSelect = document.getElementById('conversionType');
        if (!conversionTypeSelect) return;
        
        const options = conversionTypeSelect.querySelectorAll('option[value]:not([value=""])');
        options.forEach(option => {
            const value = option.value;
            let textKey = '';
            
            switch(value) {
                case 'ass_to_srt':
                    textKey = 'assToSrt';
                    break;
                case 'subtitle_to_excel':
                    textKey = option.textContent.includes('.ass') ? 'subtitleToExcel' : 'srtToExcel';
                    break;
                case 'xlsx_to_srt':
                    textKey = 'xlsxToSrt';
                    break;
                case 'sup_to_srt':
                    textKey = 'supToSrt';
                    break;
                case 'sup_to_excel':
                    textKey = 'supToExcel';
                    break;
                case 'auto_narration_timing':
                    textKey = 'auto_narration_timing';
                    break;
            }
            
            if (textKey && languages[this.currentLang][textKey]) {
                option.textContent = languages[this.currentLang][textKey];
            }
        });
    }
    
    updateSwitchButton() {
        const langSwitchBtn = document.getElementById('langSwitchBtn');
        const langSwitchText = document.getElementById('langSwitchText');
        
        if (langSwitchBtn && langSwitchText) {
            const targetLangText = this.currentLang === 'zh-CN' ? 
                languages[this.currentLang].langSwitchToEn : 
                languages[this.currentLang].langSwitchToCn;
            
            // 更新按钮文本
            langSwitchText.textContent = targetLangText;
            
            // 更新aria-label和title属性
            langSwitchBtn.setAttribute('aria-label', targetLangText);
            langSwitchBtn.setAttribute('title', targetLangText);
        }
    }
    
    // 获取当前语言的文本
    getText(key) {
        return languages[this.currentLang][key] || key;
    }
}
