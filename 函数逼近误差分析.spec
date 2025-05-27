# -*- mode: python ; coding: utf-8 -*-

import os
import streamlit
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import glob
import site
import sys
import webbrowser

block_cipher = None

# 获取 streamlit 包路径
streamlit_path = os.path.dirname(streamlit.__file__)

# 收集所有 streamlit 相关的数据文件
streamlit_datas = collect_data_files('streamlit')
streamlit_hidden_imports = collect_submodules('streamlit')

# 查找 streamlit 的 dist-info 目录
dist_info_paths = []
for site_dir in site.getsitepackages():
    dist_info = glob.glob(os.path.join(site_dir, 'streamlit-*.dist-info'))
    if dist_info:
        dist_info_paths.extend(dist_info)

dist_info_datas = [(path, os.path.basename(path)) for path in dist_info_paths] if dist_info_paths else []

# 查找 streamlit 命令行工具
streamlit_scripts = []
for site_dir in site.getsitepackages():
    scripts_dir = os.path.join(site_dir, 'Scripts')
    if os.path.exists(scripts_dir):
        streamlit_script = os.path.join(scripts_dir, 'streamlit.exe')
        if os.path.exists(streamlit_script):
            streamlit_scripts.append((streamlit_script, '.'))

# 添加其他必要的依赖
hidden_imports = [
    'streamlit',
    'streamlit.web',
    'streamlit.web.cli',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.caching',
    'streamlit.runtime.stats',
    'streamlit.runtime.media_file_manager',
    'streamlit.runtime.media_file_storage',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.scriptrunner.script_run_context',
    'streamlit.runtime.scriptrunner.script_run_context_impl',
    'streamlit.runtime.scriptrunner.script_run_context_impl_util',
    'streamlit.runtime.scriptrunner.script_run_context_impl_util_script_run_context_impl_util',
    'numpy',
    'matplotlib',
    'subprocess',
    'os',
    'sys',
    'time',
    'signal',
    'webbrowser',
    'socket',
    'psutil',
    'logging',
    'traceback'
]

# 添加其他必要的数据文件
datas = [
    ('app.py', '.'),
    ('start_app.py', '.'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
    ('assets', 'assets'),
    ('static', 'static'),
    ('templates', 'templates')
]

a = Analysis(
    ['start_app.py'],
    pathex=[],
    binaries=[],
    datas=datas + streamlit_datas + dist_info_datas + streamlit_scripts,
    hiddenimports=hidden_imports + streamlit_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='函数逼近误差分析',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)

webbrowser.open("http://localhost:8501")
