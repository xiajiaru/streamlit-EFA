from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集所有数据文件
datas = collect_data_files('streamlit')

# 收集所有子模块
hiddenimports = collect_submodules('streamlit')

# 添加版本信息
import streamlit
import os
import site

# 查找 streamlit 的 dist-info 目录
for site_dir in site.getsitepackages():
    dist_info = os.path.join(site_dir, 'streamlit-*.dist-info')
    if os.path.exists(dist_info):
        datas.append((dist_info, 'streamlit-*.dist-info')) 