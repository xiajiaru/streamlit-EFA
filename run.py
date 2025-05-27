import os
import sys
import subprocess

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, 'app.py')
    
    # 启动Streamlit应用
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path])

if __name__ == '__main__':
    main() 