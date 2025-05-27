import os
import sys
import subprocess
import time
import signal
import webbrowser
import socket
import psutil
import traceback
import logging
import netifaces  # 添加网络接口检查

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_app_path():
    """获取应用路径，支持开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 如果是开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(base_path, 'app.py')
    logger.info(f"应用路径: {app_path}")
    return app_path

def is_port_in_use(port):
    """检查端口是否被占用，并确认是否是 Streamlit 进程"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            if result == 0:
                # 检查占用端口的进程
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'streamlit' in ' '.join(proc.info['cmdline'] or []).lower():
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            return False
    except Exception as e:
        logger.error(f"检查端口时出错: {str(e)}")
        return False

def kill_streamlit_processes():
    """终止所有 Streamlit 进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'streamlit' in ' '.join(proc.info['cmdline'] or []).lower():
                    proc.terminate()
                    logger.info(f"已终止Streamlit进程: {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f"终止进程时出错: {str(e)}")

def get_streamlit_cmd():
    """获取streamlit命令路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        streamlit_cmd = os.path.join(sys._MEIPASS, 'streamlit.exe')
        if not os.path.exists(streamlit_cmd):
            streamlit_cmd = 'streamlit'
    else:
        # 如果是开发环境
        streamlit_cmd = os.path.join(os.path.dirname(sys.executable), 'streamlit')
        if not os.path.exists(streamlit_cmd):
            streamlit_cmd = 'streamlit'
    
    logger.info(f"Streamlit命令路径: {streamlit_cmd}")
    return streamlit_cmd

def check_network_config():
    """检查网络配置"""
    try:
        # 获取所有网络接口
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    logger.info(f"网络接口 {iface}: {addr['addr']}")
        
        # 检查端口是否可访问
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('0.0.0.0', 8501))
        if result == 0:
            logger.info("端口8501可以访问")
        else:
            logger.warning("端口8501可能被阻止")
        sock.close()
        
    except Exception as e:
        logger.error(f"网络配置检查失败: {str(e)}")

def check_firewall():
    """检查防火墙配置"""
    try:
        if sys.platform == 'win32':
            # Windows防火墙检查
            import subprocess
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'currentprofile'], 
                                 capture_output=True, text=True)
            logger.info(f"Windows防火墙状态:\n{result.stdout}")
            
            # 检查端口规则
            result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                                 capture_output=True, text=True)
            if '8501' in result.stdout:
                logger.info("找到端口8501的防火墙规则")
            else:
                logger.warning("未找到端口8501的防火墙规则")
                
        elif sys.platform == 'linux':
            # Linux防火墙检查
            import subprocess
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            logger.info(f"Linux防火墙状态:\n{result.stdout}")
            
            # 检查端口规则
            result = subprocess.run(['ufw', 'status', 'numbered'], capture_output=True, text=True)
            if '8501' in result.stdout:
                logger.info("找到端口8501的防火墙规则")
            else:
                logger.warning("未找到端口8501的防火墙规则")
                
    except Exception as e:
        logger.error(f"防火墙检查失败: {str(e)}")

def main():
    try:
        # 检查网络配置
        check_network_config()
        
        # 检查防火墙配置
        check_firewall()
        
        # 获取应用路径
        app_path = get_app_path()
        
        # 检查app.py是否存在
        if not os.path.exists(app_path):
            logger.error(f"Error: app.py not found at {app_path}")
            input("按回车键退出...")
            sys.exit(1)
        
        # 检查端口8501是否已经被占用
        if is_port_in_use(8501):
            logger.info("Streamlit已经在运行，正在打开浏览器...")
            webbrowser.open("http://localhost:8501")
            sys.exit(0)
        
        # 确保没有遗留的Streamlit进程
        kill_streamlit_processes()
        
        # 获取streamlit命令
        streamlit_cmd = get_streamlit_cmd()
        
        # 构建启动命令
        cmd = [
            streamlit_cmd,
            "run",
            app_path,
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--logger.level=debug"
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 等待服务器启动
        max_wait = 20  # 最多等待20秒
        start_time = time.time()
        server_started = False
        
        logger.info("正在启动Streamlit服务器...")
        while time.time() - start_time < max_wait:
            if is_port_in_use(8501):
                server_started = True
                break
            # 检查进程是否还在运行
            if process.poll() is not None:
                error_output = process.stderr.read()
                logger.error(f"Streamlit进程异常退出: {error_output}")
                break
            time.sleep(0.5)
        
        if not server_started:
            logger.error("Streamlit服务器启动失败")
            process.terminate()
            input("按回车键退出...")
            sys.exit(1)
        
        logger.info("Streamlit服务器已启动，正在打开浏览器...")
        # 打开浏览器
        webbrowser.open("http://localhost:8501")
        
        # 等待进程结束
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
    except KeyboardInterrupt:
        logger.info("\n正在关闭应用...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        kill_streamlit_processes()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error("详细错误信息:")
        logger.error(traceback.format_exc())
        kill_streamlit_processes()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 