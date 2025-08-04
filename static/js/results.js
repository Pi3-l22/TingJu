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
                input.value = '';
                // 恢复默认样式
                input.style.backgroundColor = '';
                input.style.borderColor = '';
                input.style.outlineColor = 'var(--primary-color)';
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
    const exportBtn = document.querySelector('.export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', async function () {
            try {
                const response = await fetch('/export');
                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('✅导出成功！文件已保存到: ' + result.path);
                    } else {
                        alert('❌导出失败: ' + result.message);
                    }
                } else {
                    alert('❌导出请求失败');
                }
            } catch (error) {
                alert('❌导出过程中出错: ' + error.message);
            }
        });
    }
});