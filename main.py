import numpy as np
import matplotlib.pyplot as plt
from math import factorial
import matplotlib
from matplotlib.font_manager import FontProperties

# 设置全局字体，保证负号、数学公式和部分中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['mathtext.fontset'] = 'stix'

# 设置中文字体（用于标题和图例）
font_zh = FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=16)  # 路径可换为你电脑上的中文字体

# 1. 泰勒多项式逼近
# 在x=0处展开的泰勒多项式，幂函数为基底
# func_type: 'exp' 或 'exp_neg'，n为多项式阶数
# 返回一个多项式函数poly(x)
def taylor_poly(func_type, n, x0=0):
    def poly(x):
        s = 0
        for k in range(n+1):
            if func_type == 'exp':
                deriv = np.exp(x0)  # e^x的k阶导数仍为e^x
            elif func_type == 'exp_neg':
                deriv = (-1)**k * np.exp(-x0)  # e^{-x}的k阶导数
            s += deriv / factorial(k) * (x - x0)**k
        return s
    return poly

# 2. Chebyshev最佳平方逼近
# 用Chebyshev多项式为基底，利用正交性最小化平方误差
# 返回一个多项式函数poly(x)
def chebyshev_best_approx(func_type, n):
    N = 1000  # 采样点数
    x = np.cos(np.pi * (np.arange(N) + 0.5) / N)  # Chebyshev节点
    if func_type == 'exp':
        y = np.exp(x)
    elif func_type == 'exp_neg':
        y = np.exp(-x)
    coeffs = []  # Chebyshev多项式系数
    for k in range(n+1):
        Tk = np.cos(k * np.arccos(x))  # T_k(x)
        c = (2/N) * np.sum(y * Tk)     # 系数公式
        if k == 0:
            c /= 2
        coeffs.append(c)
    def poly(x_):
        s = np.zeros_like(x_)
        for k, c in enumerate(coeffs):
            s += c * np.cos(k * np.arccos(x_))
        return s
    return poly

# 3. Chebyshev优化的Taylor逼近
# 用幂函数为基底，在Chebyshev节点上用最小二乘法拟合
# 这样得到的多项式在整个区间[-1,1]上误差分布更均匀
# 返回一个多项式函数poly(x)
def chebyshev_optimized_taylor(func_type, n):
    N = n + 1  # 只用n+1个Chebyshev节点
    x_nodes = np.cos(np.pi * (np.arange(N) + 0.5) / N)
    if func_type == 'exp':
        y_nodes = np.exp(x_nodes)
    elif func_type == 'exp_neg':
        y_nodes = np.exp(-x_nodes)
    # 构造Vandermonde矩阵
    X = np.vstack([x_nodes**k for k in range(n+1)]).T
    # 直接解线性方程组，得到插值多项式系数
    coeffs = np.linalg.solve(X, y_nodes)
    def poly(x_):
        s = np.zeros_like(x_)
        for k, c in enumerate(coeffs):
            s += c * x_**k
        return s
    return poly

# 新增等距节点插值Taylor
def equidistant_optimized_taylor(func_type, n):
    N = n + 1
    x_nodes = np.linspace(-1, 1, N)
    if func_type == 'exp':
        y_nodes = np.exp(x_nodes)
    elif func_type == 'exp_neg':
        y_nodes = np.exp(-x_nodes)
    X = np.vstack([x_nodes**k for k in range(n+1)]).T
    coeffs = np.linalg.solve(X, y_nodes)
    def poly(x_):
        s = np.zeros_like(x_)
        for k, c in enumerate(coeffs):
            s += c * x_**k
        return s
    return poly

# 4. 误差曲线绘制
# 画出f(x)与多项式逼近Pn(x)的误差曲线
# label为图例名称，style为线型，lw为线宽
def plot_error(true_func, approx_func, label, style, lw=2):
    x = np.linspace(-1, 1, 1000)  # 增加采样点
    y_true = true_func(x)
    y_approx = approx_func(x)
    error = y_true - y_approx  # 不取绝对值，显示正负误差
    plt.plot(x, error, style, label=label, linewidth=lw)
    plt.ylabel(r'$f(x)-P_n(x)$', fontsize=16)
    # 不再在曲线末端加标注

# 5. 主程序
# 对每个函数、每个阶数、每种方法，画出误差曲线
def main():
    funcs = {
        'exp': (lambda x: np.exp(x), r'$y = e^{x}$'),
        'exp_neg': (lambda x: np.exp(-x), r'$y = e^{-x}$')
    }
    # methods字典：方法名 -> (函数, 线型, 颜色)
    methods = {
        r'Taylor': (taylor_poly, 'r-', '#D62728'),              # 红色
        r'Chebyshev优化Taylor': (chebyshev_optimized_taylor, 'g--', '#2CA02C'),  # 绿色
        r'Chebyshev最佳平方': (chebyshev_best_approx, 'b-.', '#1F77B4'),         # 蓝色
        r'等距节点插值Taylor': (equidistant_optimized_taylor, 'm:', '#9467bd')
    }
    ns = [3, 4, 5, 6]  # 多项式阶数
    for func_type, (true_func, func_name) in funcs.items():
        for n in ns:
            plt.figure(figsize=(12, 7))
            for method_name, (method_func, style, color) in methods.items():
                approx_func = method_func(func_type, n)
                plot_error(true_func, approx_func, method_name, style, lw=2.5)
            # 标题含中文和LaTeX公式
            plt.title(f'{func_name}，阶数 $n={n}$ 的三种方法误差曲线', fontproperties=font_zh, fontsize=18)
            plt.xlabel(r'$x$', fontsize=16)
            plt.ylabel(r'$f(x)-P_n(x)$', fontsize=16)
            plt.yscale('linear')  # 普通坐标
            plt.tick_params(labelsize=14)
            plt.legend(fontsize=14, loc='upper center', ncol=3, prop=font_zh, frameon=True, fancybox=True, shadow=True)
            plt.grid(True, which='both', linestyle='--', linewidth=0.8, alpha=0.7)
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()
            plt.close()

if __name__ == '__main__':
    main()

