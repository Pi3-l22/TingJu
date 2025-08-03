// 点击按钮时触发文件选择
document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileName = document.getElementById('file-name');
    const manualBtn = document.getElementById('manual-btn');

    if (browseBtn) {
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // 文件选择后显示文件名并启用上传按钮
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileName.textContent = `已选择文件: ${fileInput.files[0].name}`;
                if (uploadBtn) uploadBtn.disabled = false;
            } else {
                fileName.textContent = '';
                if (uploadBtn) uploadBtn.disabled = true;
            }
        });
    }

    // 拖拽上传功能
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropArea.classList.add('highlight');
        }

        function unhighlight() {
            dropArea.classList.remove('highlight');
        }

        // 处理文件拖拽放置
        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            if (files.length > 0 && fileInput) {
                // 设置文件到input元素
                fileInput.files = files;
                fileName.textContent = `已选择文件: ${files[0].name}`;
                if (uploadBtn) uploadBtn.disabled = false;
            }
        }
    }
    
    // 手动填写按钮点击事件
    if (manualBtn) {
        manualBtn.addEventListener('click', () => {
            window.location.href = '/manual';
        });
    }
});