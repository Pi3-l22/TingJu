// 页面加载时就异步获取音色列表
let voicesPromise = fetchVoices();

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
async function fetchVoices() {
    try {
        const response = await fetch('/voices');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取音色列表时出错:', error);
        return { error: error.message };
    }
}

// 页面加载完成后填充音色列表
document.addEventListener('DOMContentLoaded', function () {
    populateVoices();
});

async function populateVoices() {
    const voiceSelect = document.getElementById('voice-select');
    const voiceStatus = document.getElementById('voice-status');

    if (!voiceSelect || !voiceStatus) return;

    try {
        voiceStatus.innerHTML = '<span class="loading">正在加载音色列表...</span>';

        // 等待音色列表获取完成
        const data = await voicesPromise;

        if (data.error) {
            voiceStatus.innerHTML = '<span class="error">加载音色列表失败: ' + data.error + '</span>';
            return;
        }

        // 清空选项
        voiceSelect.innerHTML = '';

        // 添加默认选项
        const defaultOption = document.createElement('option');
        defaultOption.value = 'en-US-ChristopherNeural';
        defaultOption.textContent = '默认 - ChristopherNeural (男)';
        voiceSelect.appendChild(defaultOption);

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
            console.log(voice.style);
            // 获取风格信息
            let style = '无';
            if (voice.style && voice.style.length > 0) {
                style = voice.style.join(', ');
            }

            // 使用处理后的音色名称显示
            const displayName = getVoiceDisplayName(voice.name);
            option.textContent = `${displayName}${gender}- 风格: ${style}`;
            voiceSelect.appendChild(option);
        });

        voiceStatus.innerHTML = '';
    } catch (error) {
        voiceStatus.innerHTML = '<span class="error">加载音色列表时出错: ' + error.message + '</span>';
        voiceSelect.innerHTML = '<option value="en-US-ChristopherNeural">默认 - ChristopherNeural (男)</option>';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('confirm-form');
    const textArea = document.getElementById('text-content');
    const errorDiv = document.getElementById('text-warning');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (form && textArea && errorDiv) {
        form.addEventListener('submit', function (e) {
            const text = textArea.value.trim();

            // 清除之前的错误信息
            errorDiv.textContent = '';

            // 检查文本是否为空
            if (!text) {
                errorDiv.textContent = '文本内容不能为空';
                e.preventDefault();
                return false;
            }

            // 检查文本长度是否足够
            if (text.length < 10) {
                errorDiv.textContent = '文本内容至少需要10个字符';
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
});