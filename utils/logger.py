import logging
from pathlib import Path

# 日志目录
LOG_DIR = "logs"

def setup_logger(name: str = "TingJu", log_level: int = logging.INFO) -> logging.Logger:
    """设置并返回一个日志记录器"""
    # 创建日志目录
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建文件处理器
        log_file = log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # 创建格式器并添加到处理器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s:     %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# 创建全局日志记录器实例
logger = setup_logger()