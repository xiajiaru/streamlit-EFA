import PyInstaller.__main__
import os
import sys

def build():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用 spec 文件进行构建
    spec_path = os.path.join(current_dir, '函数逼近误差分析.spec')
    
    # PyInstaller 参数
    PyInstaller.__main__.run([
        spec_path,
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不询问确认
        '--log-level=DEBUG',  # 显示详细日志
    ])

if __name__ == '__main__':
    build() 