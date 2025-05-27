import streamlit as st
import sys
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from math import factorial
import matplotlib
from matplotlib.font_manager import FontProperties
from main import taylor_poly, chebyshev_best_approx, chebyshev_optimized_taylor, equidistant_optimized_taylor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

try:
    # 设置matplotlib中文字体和数学公式
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['mathtext.fontset'] = 'cm'  # 使用Computer Modern字体
    plt.rcParams['mathtext.rm'] = 'serif'    # 使用serif字体
    plt.rcParams['mathtext.it'] = 'serif:italic'  # 使用斜体
    plt.rcParams['mathtext.bf'] = 'serif:bold'    # 使用粗体

    # 设置页面标题
    st.set_page_config(
        page_title="函数逼近误差分析",
        page_icon="📊",
        layout="wide"
    )
    
    # 添加标题
    st.title("函数逼近误差分析")

    # 侧边栏控制面板
    st.sidebar.header("参数设置")

    # 选择函数
    func_type = st.sidebar.selectbox(
        "选择被逼近函数",
        ["exp", "exp_neg"],
        format_func=lambda x: "e^x" if x == "exp" else "e^(-x)"
    )

    # 选择阶数
    n = st.sidebar.slider("选择多项式阶数", min_value=1, max_value=10, value=4)

    # 选择要显示的方法
    methods = {
        "Taylor": (taylor_poly, 'r-', '#D62728'),
        "Chebyshev优化Taylor": (chebyshev_optimized_taylor, 'g--', '#2CA02C'),
        "Chebyshev最佳平方": (chebyshev_best_approx, 'b-.', '#1F77B4'),
        "等距节点插值Taylor": (equidistant_optimized_taylor, 'm:', '#9467bd')
    }

    # 添加坐标轴类型选择
    use_log_scale = st.sidebar.checkbox("使用对数坐标", value=False)

    selected_methods = st.sidebar.multiselect(
        "选择逼近方法",
        list(methods.keys()),
        default=list(methods.keys())
    )

    # 定义真实函数
    true_func = lambda x: np.exp(x) if func_type == "exp" else np.exp(-x)
    func_name = r'$y = e^{x}$' if func_type == "exp" else r'$y = e^{-x}$'

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 7))

    # 计算并绘制误差曲线
    x = np.linspace(-1, 1, 1000)
    y_true = true_func(x)

    max_error = 0
    for method_name in selected_methods:
        method_func, style, color = methods[method_name]
        approx_func = method_func(func_type, n)
        y_approx = approx_func(x)
        error = y_true - y_approx
        max_error = max(max_error, np.max(np.abs(error)))
        ax.plot(x, error, style, label=method_name, linewidth=2.5)

    # 设置图形属性
    ax.set_title(f'{func_name}，阶数 $n={n}$ 的误差曲线', fontsize=18)
    ax.set_xlabel('x', fontsize=16)  # 移除LaTeX格式
    ax.set_ylabel('f(x)-P_n(x)', fontsize=16)  # 移除LaTeX格式

    # 设置y轴范围和对数坐标
    if use_log_scale:
        ax.set_yscale('symlog')
        ax.set_ylim(-max_error*1.2, max_error*1.2)
    else:
        ax.set_ylim(-max_error*1.2, max_error*1.2)

    ax.grid(True, which='both', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.legend(fontsize=14, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    ax.tick_params(labelsize=14)

    # 调整布局以适应图例
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])

    # 显示图形
    st.pyplot(fig)

    # 添加说明文本
    st.markdown("""
    ### 说明
    - 本应用展示了不同方法对指数函数的逼近误差
    - 可以通过侧边栏选择：
      - 被逼近函数（e^x 或 e^(-x)）
      - 多项式阶数（1-10）
      - 逼近方法（可多选）
      - 是否使用对数坐标
    - 误差曲线显示了真实函数与逼近多项式之间的差值
    - 使用对数坐标可以更好地观察不同数量级的误差
    """)

except Exception as e:
    logging.error(f"发生错误: {str(e)}", exc_info=True)
    st.error(f"程序发生错误: {str(e)}")
    st.stop() 