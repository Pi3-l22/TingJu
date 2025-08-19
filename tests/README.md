# 测试文档

## 目录结构

```
tests/
├── README.md                 # 测试说明文档
├── test_app.py               # 应用程序集成测试
├── test_audio_generator.py   # 音频生成功能测试
├── test_file_processor.py    # 文件处理功能测试
├── test_language_detector.py # 语言类型检测测试
├── test_performance.py       # 性能测试
├── test_text_processor.py    # 文本处理功能测试
├── test_text_translator.py   # 文本翻译功能测试
└── test.txt                  # 用于测试文本的文件
```

## 测试模块说明

### 1. test_app.py - 应用程序集成测试
测试应用程序的主要API端点和功能：
- 根路径访问测试
- 手动输入页面测试
- 音色列表获取测试
- 文件上传功能测试（支持和不支持的文件类型）
- 音频和翻译生成功能测试
- 导出功能测试

### 2. test_audio_generator.py - 音频生成功能测试
测试音频相关的功能：
- 音色列表获取功能
- 音频生成功能

### 3. test_file_processor.py - 文件处理功能测试
测试从不同格式文件中提取文本的功能：
- 不支持的文件类型处理
- TXT文件内容提取
- 大文件处理性能

### 4. test_text_processor.py - 文本处理功能测试
测试文本处理相关功能：
- 文本规范化处理
- 句子分割功能
- 大文本分句处理

### 5. test_text_translator.py - 文本翻译功能测试
测试文本翻译相关功能：
- 文本翻译功能
- 所有翻译器的可用性测试

### 6. test_performance.py - 性能测试
测试各模块的性能表现：
- 句子分割性能测试
- 文件处理性能测试
- 翻译性能测试
- 音频生成性能测试

### 7. test_language_detector.py - 语言类型检测测试
测试语言类型检测功能：
- 语言类型检测功能
- 不支持的语言类型的判断

## 运行测试

在项目根目录下，使用以下两种方式均可运行测试。

### 使用unittest手动运行测试

```bash
# 运行所有测试
python -m unittest discover tests

# 运行单个测试文件
python -m unittest tests.test_app
python -m unittest tests.test_audio_generator
python -m unittest tests.test_file_processor
python -m unittest tests.test_language_detector
python -m unittest tests.test_performance
python -m unittest tests.test_text_processor
python -m unittest tests.test_text_translator
```

### 使用run_tests.py脚本运行测试

```bash
python run_tests.py all          # 运行所有测试
python run_tests.py <module>     # 运行特定模块测试
python run_tests.py --list       # 列出所有测试模块
python run_tests.py --help       # 显示帮助信息
```

