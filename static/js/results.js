// results.html页面的JavaScript功能
document.addEventListener('DOMContentLoaded', function () {
    // 获取所有音频元素
    const audioPlayers = document.querySelectorAll('.audio-player');

    // 为每个音频元素添加播放事件监听器
    audioPlayers.forEach(audio => {
        audio.addEventListener('play', function () {
            // 暂停其他所有音频
            pauseOtherAudios(this);
        });
    });

    // 暂停除当前音频外的其他音频
    function pauseOtherAudios(currentAudio) {
        audioPlayers.forEach(audio => {
            if (audio !== currentAudio && !audio.paused) {
                audio.pause();
            }
        });
    }

    // 主题选择功能
    const themeBtn = document.getElementById('theme-btn');
    const themeDropdown = themeBtn.nextElementSibling
    const themeOptions = themeDropdown.querySelectorAll('.option');

    // 点击主题按钮显示/隐藏下拉菜单
    if (themeBtn && themeDropdown) {
        themeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            themeDropdown.classList.toggle('show');
        });

        // 点击页面其他地方隐藏下拉菜单
        document.addEventListener('click', function (e) {
            if (!themeBtn.contains(e.target) && themeDropdown.classList.contains('show')) {
                themeDropdown.classList.remove('show');
            }
        });
    }

    // 为每个主题选项添加点击事件
    themeOptions.forEach(option => {
        option.addEventListener('click', function () {
            const theme = this.getAttribute('id');
            document.documentElement.setAttribute('data-theme', theme);
            // 保存用户选择到localStorage
            localStorage.setItem('theme', theme);
            // 隐藏下拉菜单
            if (themeDropdown) {
                themeDropdown.classList.remove('show');
            }
        });
    });

    // 页面加载时应用保存的主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // 字体选择功能
    const fontBtn = document.getElementById('font-btn');
    const fontDropdown = fontBtn.nextElementSibling;
    const fontOptions = fontDropdown.querySelectorAll('.option');

    // 点击字体按钮显示/隐藏下拉菜单
    if (fontBtn && fontDropdown) {
        fontBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            fontDropdown.classList.toggle('show');
        });

        // 点击页面其他地方隐藏下拉菜单
        document.addEventListener('click', function (e) {
            if (!fontBtn.contains(e.target) && fontDropdown.classList.contains('show')) {
                fontDropdown.classList.remove('show');
            }
        });
    }

    // 为每个主题选项添加点击事件
    fontOptions.forEach(option => {
        option.addEventListener('click', function () {
            const theme = this.getAttribute('id');
            document.documentElement.setAttribute('font-theme', theme);
            // 保存用户选择到localStorage
            localStorage.setItem('font-theme', theme);
            // 隐藏下拉菜单
            if (themeDropdown) {
                themeDropdown.classList.remove('show');
            }
        });
    });

    // 页面加载时应用保存的字体主题
    const savedFontTheme = localStorage.getItem('font-theme');
    if (savedFontTheme) {
        document.documentElement.setAttribute('font-theme', savedFontTheme);
    }


    // 听写模式功能
    const dictationBtn = document.querySelector('.dictation-btn');
    if (dictationBtn) {
        dictationBtn.addEventListener('click', function () {
            const inputElements = document.querySelectorAll('.user-input');
            const sentenceElements = document.querySelectorAll('.sentence');
            const translationElements = document.querySelectorAll('.translation');
            const clearBtn = document.querySelector('.clear-btn');
            const readBtn = document.querySelector('.read-btn');

            // 显示所有输入框
            inputElements.forEach(input => {
                input.style.display = 'block';
            });

            // 玻璃模糊句子和翻译
            sentenceElements.forEach(sentence => {
                sentence.classList.add('blurry')
            });

            translationElements.forEach(translation => {
                translation.classList.add('blurry')
            });

            // 显示清空按钮，听写模式变为听读模式
            clearBtn.style.display = 'block';
            readBtn.style.display = 'block';
            dictationBtn.style.display = 'none';

            // 滚动到页面顶部
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

            // 为每个输入框添加事件监听器
            inputElements.forEach(input => {
                // 获取对应的句子
                const resultItem = input.closest('.result-item');
                const sentenceElement = resultItem.querySelector('.sentence');
                const translationElement = resultItem.querySelector('.translation');
                const originalSentence = sentenceElement.textContent.trim().replace(/^\d+\.\s*/, '');

                input.addEventListener('input', function () {
                    const userInput = this.value.trim();
                    if (userInput === originalSentence) {
                        this.style.backgroundColor = 'var(--success-bg-color)';
                        this.style.borderColor = 'var(--success-color)';
                        this.style.outlineColor = 'var(--success-color)';
                        sentenceElement.classList.remove('blurry');
                        translationElement.classList.remove('blurry');
                    } else {
                        // 输入不正确，恢复默认样式
                        this.style.backgroundColor = '';
                        this.style.borderColor = '';
                        this.style.outlineColor = 'var(--primary-color)';
                        sentenceElement.classList.add('blurry');
                        translationElement.classList.add('blurry');
                    }
                });
            });
        });
    }

    // 清空输入框按钮功能
    const clearBtn = document.querySelector('.clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            const inputElements = document.querySelectorAll('.user-input');

            // 清空所有输入框的内容
            inputElements.forEach(input => {
                // 获取对应的句子和翻译元素
                const resultItem = input.closest('.result-item');
                const sentenceElement = resultItem.querySelector('.sentence');
                const translationElement = resultItem.querySelector('.translation');

                // 恢复默认样式
                input.value = '';
                input.style.backgroundColor = '';
                input.style.borderColor = '';
                input.style.outlineColor = 'var(--primary-color)';
                input.style.height = '55px';

                // 添加模糊效果
                sentenceElement.classList.add('blurry');
                translationElement.classList.add('blurry');
            });

            // 滚动到页面顶部
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // 听读模式按钮功能
    const readBtn = document.querySelector('.read-btn');
    if (readBtn) {
        readBtn.addEventListener('click', function () {
            const inputElements = document.querySelectorAll('.user-input');
            const sentenceElements = document.querySelectorAll('.sentence');
            const translationElements = document.querySelectorAll('.translation');
            const clearBtn = document.querySelector('.clear-btn');

            // 隐藏所有输入框
            inputElements.forEach(input => {
                input.style.display = 'none';
                // 清空输入框内容并恢复默认样式
                input.value = '';
                input.style.backgroundColor = '';
                input.style.borderColor = '';
                input.style.outlineColor = 'var(--primary-color)';
            });

            // 清除句子和翻译的模糊效果
            sentenceElements.forEach(sentence => {
                sentence.classList.remove('blurry');
            });

            translationElements.forEach(translation => {
                translation.classList.remove('blurry');
            });

            // 隐藏清空按钮和听读模式按钮，显示听写模式按钮
            clearBtn.style.display = 'none';
            readBtn.style.display = 'none';
            dictationBtn.style.display = 'block';

            // 滚动到页面顶部
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // 导出功能
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', async function () {
            const infoDiv = document.getElementById('status-info');
            try {
                const response = await fetch('/export');
                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'success') {
                        infoDiv.innerHTML = '<span class="success">✅ 导出成功！文件已保存到运行目录下: ' + result.path + '</span>';
                    } else {
                        infoDiv.innerHTML = '<span class="error">‼ 导出失败: ' + result.message + '</span>';
                    }
                } else {
                    infoDiv.innerHTML = '<span class="error">‼ 导出请求失败: ' + response.status + ' ' + response.statusText + '</span>';
                }
            } catch (error) {
                infoDiv.innerHTML = '<span class="error">‼ 导出过程出错: ' + error.message + '</span>';
            }

            // 10秒后自动清除提示信息
            setTimeout(() => {
                infoDiv.innerHTML = '';
            }, 10000); // 10000毫秒 = 10秒
        });
    }
});