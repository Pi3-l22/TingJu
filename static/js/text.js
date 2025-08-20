// 页面加载时就异步获取音色列表和语言列表
// let voicesPromise = fetchVoices();
let languagesPromise = fetchLanguages();

// 辅助函数：从音色名称中提取不含语言代码的部分
function getVoiceDisplayName(voiceName) {
    // 分割音色名称，例如将 "en-US-ChristopherNeural" 分割为 ["en", "US", "ChristopherNeural"]
    const parts = voiceName.split('-');

    // 如果至少有3个部分，则去除前两个部分（语言代码）
    if (parts.length >= 3) {
        return parts.slice(2).join('-');
    }

    // 否则返回原名称
    return voiceName;
}

// 异步获取音色列表的函数
async function fetchVoices(locale = 'en-US') {
    try {
        const response = await fetch(`/voices?locale=${locale}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取音色列表时出错:', error);
        return { error: error.message };
    }
}

// 异步获取语言列表的函数
async function fetchLanguages() {
    try {
        const response = await fetch('/languages');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取语言列表时出错:', error);
        return { error: error.message };
    }
}

// 页面加载完成后填充语言列表和音色列表
document.addEventListener('DOMContentLoaded', function () {
    populateLanguages().then(() => {
        // 在语言列表加载完成后，如果已选择语言则加载对应的音色列表
        const langSelect = document.getElementById('lang-select');
        const selectedIndex = langSelect.selectedIndex;
        const selectedOption = langSelect.options[selectedIndex];
        if (langSelect && selectedOption.dataset.locale) {
            populateVoices(selectedOption.dataset.locale);
        }
    });
});

async function populateLanguages() {
    const langSelect = document.getElementById('lang-select');
    const langStatus = document.getElementById('lang-status');

    if (!langSelect) return;

    try {
        // 等待语言列表获取完成
        const data = await languagesPromise;

        if (data.error) {
            if (langStatus) {
                langStatus.innerHTML = '<span class="error">‼ 加载语言列表失败: ' + data.error + '</span>';
            }
            return;
        }

        // 清空选项
        langSelect.innerHTML = '';

        // 添加其他语言选项
        data.languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = `${lang.zh_name} ${lang.name} (${lang.locale})`;
            option.dataset.locale = lang.locale;
            langSelect.appendChild(option);
        });

        // 检查是否有检测到的语言，如果有则自动选择
        const detectedLocale = window.detectedLocale;
        if (detectedLocale) {
            const optionToSelect = langSelect.querySelector(`option[data-locale="${detectedLocale}"]`);
            if (optionToSelect) {
                optionToSelect.selected = true;
                // 触发change事件以更新音色列表
                langSelect.dispatchEvent(new Event('change'));
            }
        }

        // 添加语言选择事件监听器
        langSelect.addEventListener('change', async function () {
            const selectedIndex = langSelect.selectedIndex;
            const selectedOption = langSelect.options[selectedIndex];
            const selectedLocale = selectedOption.dataset.locale;
            if (selectedLocale) {
                await populateVoices(selectedLocale);
            } else {
                // 如果选择默认选项，则使用默认的英语音色
                await populateVoices('en-US');
            }
        });
    } catch (error) {
        if (langStatus) {
            langStatus.innerHTML = '<span class="error">‼ 加载语言列表时出错: ' + error.message + '</span>';
        }
    }
}

async function populateVoices(locale = 'en-US') {
    const voiceSelect = document.getElementById('voice-select');
    const voiceStatus = document.getElementById('voice-status');

    if (!voiceSelect) return;

    try {
        if (voiceStatus) {
            voiceStatus.innerHTML = '<span class="loading">◌ 正在加载音色列表...</span>';
        }

        // 获取指定语言的音色列表
        const data = await fetchVoices(locale);

        if (data.error) {
            if (voiceStatus) {
                voiceStatus.innerHTML = '<span class="error">‼ 加载音色列表失败: ' + data.error + '</span>';
            }
            return;
        }

        // 清空选项
        voiceSelect.innerHTML = '';

        // 判断音色列表是否为空
        if (data.voices.length === 0) {
            if (voiceStatus) {
                voiceStatus.innerHTML = '<span class="error">‼ 暂无该语言的音色</span>';
            }
            return;
        }

        // 添加其他音色选项
        data.voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;

            // 确定性别显示文本
            let gender = ' (未知) ';
            if (voice.gender === 'Male') {
                gender = ' (男) ';
            } else if (voice.gender === 'Female') {
                gender = ' (女) ';
            }

            // 获取风格信息
            // let style = '无';
            // if (voice.style && voice.style.length > 0) {
            //     style = voice.style.join(', ');
            // }

            // 使用处理后的音色名称显示
            const displayName = getVoiceDisplayName(voice.name);
            option.textContent = `${displayName}${gender}`;
            voiceSelect.appendChild(option);
        });

        if (voiceStatus) {
            voiceStatus.innerHTML = '';
        }
    } catch (error) {
        if (voiceStatus) {
            voiceStatus.innerHTML = '<span class="error">‼ 加载音色列表时出错: ' + error.message + '</span>';
        }
    }
}

// 在页面加载时设置检测到的语言
window.addEventListener('DOMContentLoaded', function () {
    // 从页面中获取检测到的语言代码
    const langStatus = document.getElementById('lang-status');
    const successStatus = langStatus ? langStatus.querySelector('.success') : null;
    if (langStatus && successStatus) {
        const locale = successStatus.getAttribute('data-locale');
        if (locale && locale !== 'None') {
            window.detectedLocale = locale;
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('confirm-form');
    const textArea = document.getElementById('text-content');
    const errorDiv = document.getElementById('text-status');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (form && textArea && errorDiv) {
        form.addEventListener('submit', function (e) {
            const text = textArea.value.trim();

            // 清除之前的错误信息
            errorDiv.textContent = '';

            // 检查文本是否为空
            if (!text) {
                errorDiv.innerHTML = '<span class="warning">⚠ 文本内容不能为空</span>';
                e.preventDefault();
                return false;
            }

            // 检查文本长度是否足够
            if (text.length < 5) {
                errorDiv.innerHTML = '<span class="warning">⚠ 文本内容至少需要 5 个字符</span>';
                e.preventDefault();
                return false;
            }

            // 显示加载动画
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }

            return true;
        });
    }

    // 页面加载时应用保存的主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // 页面加载时应用保存的字体主题
    const savedFontTheme = localStorage.getItem('font-theme');
    if (savedFontTheme) {
        document.documentElement.setAttribute('font-theme', savedFontTheme);
    }
});