#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TingJu 测试运行脚本

此脚本提供统一的测试运行接口，支持多种运行模式:
- 运行所有测试
- 运行特定模块测试
- 运行性能测试
- 显示测试覆盖率
"""

import argparse
import sys
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def run_all_tests(verbosity=1):
    """运行所有测试"""
    print("🏃 运行所有测试...")
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_module, verbosity=1):
    """运行特定测试模块"""
    print(f"🏃 运行测试模块: {test_module}")
    try:
        # 构造测试模块路径
        if test_module.startswith('test_'):
            module_path = f'tests.{test_module}'
        else:
            module_path = f'tests.test_{test_module}'
            
        # 动态导入测试模块
        suite = unittest.TestLoader().loadTestsFromName(module_path)
        
        if suite.countTestCases() == 0:
            print(f"❌ 未找到测试用例在模块: {test_module}")
            return False
            
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except ImportError as e:
        print(f"❌ 无法导入测试模块 {test_module}: {e}")
        return False
    except Exception as e:
        print(f"❌ 运行测试模块 {test_module} 时出错: {e}")
        return False

def list_test_modules():
    """列出所有可用的测试模块"""
    print("📋 可用的测试模块:")
    test_files = Path('tests').glob('test_*.py')
    modules = [f.stem for f in test_files if f.name != 'test_performance.py']
    performance_module = 'test_performance' if Path('tests/test_performance.py').exists() else None
    
    for module in sorted(modules):
        print(f"  • {module}")
    
    if performance_module:
        print(f"  • {performance_module} (性能测试)")
    
    print("\n📝 使用方法:")
    print("  python run_tests.py all          # 运行所有测试")
    print("  python run_tests.py <module>     # 运行特定模块测试")
    print("  python run_tests.py --list       # 列出所有测试模块")

def main():
    parser = argparse.ArgumentParser(description='TingJu 测试运行器')
    parser.add_argument('test', nargs='?', default='all', 
                       help='要运行的测试: "all" 表示所有测试, 或指定模块名称 (默认: all)')
    parser.add_argument('--list', action='store_true', 
                       help='列出所有可用的测试模块')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出模式')
    
    args = parser.parse_args()
    
    # 设置输出详细程度
    verbosity = 2 if args.verbose else 1
    
    # 处理 --list 参数
    if args.list:
        list_test_modules()
        return 0
    
    # 根据参数运行测试
    success = False
    if args.test == 'all':
        success = run_all_tests(verbosity)
    else:
        success = run_specific_test(args.test, verbosity)
    
    # 根据测试结果返回退出码
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())