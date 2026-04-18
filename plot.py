import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

def ncar_precip_cmap():
    """
    NCAR 标准降水色标（常用业务版）
    从弱到强：浅蓝 → 蓝 → 绿 → 黄 → 橙 → 红 → 洋红 → 紫
    """
    colors = [
        "#FFFFFF",      # 无降水
        "#C7E9FF", "#9DD4FF", "#6FBCFF",
        "#3AA8FF", "#0580FF", "#00F4FF",
        "#00DCA8", "#01A801", "#00F600",
        "#80FF00", "#FFFF00", "#FFD200",
        "#FFAA00", "#FF7D00", "#FF5400",
        "#FF0000", "#D40000", "#AA0000",
        "#D40080", "#B400D4", "#9600D4"
    ]
    
    cmap = mcolors.LinearSegmentedColormap.from_list("ncar_precip", colors)
    return cmap

def ncar_precip_levels():
    """
    NCAR 降水分级（mm）
    """
    import numpy as np
    levels = [
        0, 0.1, 0.5, 1, 2, 3, 5,
        8, 10, 15, 20, 25, 30, 35,
        40, 50, 60, 80, 100, 150, 200
    ]
    return np.array(levels)

def ncar_precip_cmap_7day_total():
    """
    NCAR经典降水色卡（适配7天累计降水，更柔和过渡）
    """
    colors = [
        "#ffffff",       # 0
        "#c7e9ff", "#9dd4ff", "#6fbcff",
        "#3aa8ff", "#0080ff", "#00f4ff",
        "#00dca8", "#00a800", "#00f600",
        "#80ff00", "#ffff00", "#ffd200",
        "#ffaa00", "#ff7d00", "#ff5400",
        "#ff0000", "#cc0000", "#990000",
        "#d40080", "#b400d4", "#9600d4"
    ]
    return mcolors.LinearSegmentedColormap.from_list("ncar_precip_7day", colors)

def precip_levels_7days_total():
    """
    7天累计降水量级（华北暴雨专用）
    单位：mm
    """
    levels = [
        0, 10, 25, 50, 75, 100,
        125, 150, 180, 200, 250,
        300, 350, 400, 450, 500
    ]
    return np.array(levels)

def calculate_total_precip(rain_series):
    """
    输入时序降水，输出7天累计降水
    """
    return rain_series.isel(Time=-1) - rain_series.isel(Time=0)

def plot_box_on_map(lon_min, lon_max, lat_min, lat_max, linecolor='red', linewidth=2, linestyle='-'):
    """
    在等值线/地图上画一个矩形框（用于标记关键区域）
    你只需要输入 经纬度范围，自动在图上画框
    
    参数：
    lon_min, lon_max : 经度范围
    lat_min, lat_max : 纬度范围
    linecolor        : 框的颜色（默认红色）
    linewidth        : 框粗细
    linestyle        : 线型
    """
    # 画四条边 → 形成矩形框
    # 底边
    plt.plot([lon_min, lon_max], [lat_min, lat_min], color=linecolor, lw=linewidth, ls=linestyle)
    # 顶边
    plt.plot([lon_min, lon_max], [lat_max, lat_max], color=linecolor, lw=linewidth, ls=linestyle)
    # 左边
    plt.plot([lon_min, lon_min], [lat_min, lat_max], color=linecolor, lw=linewidth, ls=linestyle)
    # 右边
    plt.plot([lon_max, lon_max], [lat_min, lat_max], color=linecolor, lw=linewidth, ls=linestyle)