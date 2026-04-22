import numpy as np
import xarray as xr
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import metpy
import project
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os

from wrf import getvar, interplevel
import metpy.calc as mpcalc
from metpy.interpolate import cross_section

# ======================
# 文件夹路径（你自己改）
# ======================
file_path = r'wrf_data\3'  # 你的wrfout文件夹
file_list = os.listdir(file_path)
file_list = [f for f in file_list if f.startswith("wrfout")]

# 按时间排序（必须）
file_list = sorted(file_list)

# ======================
# 开始循环绘图
# ======================
for filename in file_list:
    full_path = os.path.join(file_path, filename)
    print("正在处理：", filename)

    # 打开文件
    ncfile = Dataset(full_path)
    ds = xr.open_dataset(full_path)
    crs = project.get_projection(ds)

    # ======================
    # 提取时间 + 域名 d01/d02
    # ======================
    parts = filename.split("_")
    month_day = parts[2][5:]
    hour = parts[3]
    domain_part = parts[1]
    result = f"{month_day}_{hour}_{domain_part}"

    # --- 1. 提取所有必要的 3D 诊断变量 ---
    pres = getvar(ncfile, "pressure")      # 全层气压 (hPa)
    z = getvar(ncfile, "z", units="dm")    # 全层位势高度 (dm)
    ua = getvar(ncfile, "ua")              # 全层 U 风分量
    va = getvar(ncfile, "va")              # 全层 V 风分量
    wa = getvar(ncfile, "wa") 
    q = getvar(ncfile, "QVAPOR")    # 混合比
    rh = getvar(ncfile, "rh")  

    # --- 2. 插值到 700 hPa ---
    q_700 = interplevel(q, pres, 700)
    ua_700 = interplevel(ua, pres, 700)
    va_700 = interplevel(va, pres, 700)

    lon_2d = q_700['XLONG']
    lat_2d = q_700['XLAT']

    # --- 3. 计算 700hPa 水汽通量 ---
    g = 9.81
    vlocity_700 = np.sqrt(ua_700**2 + va_700**2)
    qflux_700 = (q_700 * vlocity_700) / g
    qflux_700 = qflux_700 * 1000  # 转成常用单位

    # ======================
    # 画图（单张水汽通量图）
    # ======================
    fig, ax = plt.subplots(figsize=(12,8), subplot_kw={'projection': crs}, dpi=150)

    # 画底图
    project.plot_background(lon_2d[0,0], lon_2d[0,-1], lat_2d[0,0], lat_2d[-1,0], ax)

    # 经纬度网格
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, 
                      linewidth=0.3, linestyle=':', color='gray',
                      x_inline=False, y_inline=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 9}

    # --- 画水汽通量填色 ---
    levels = np.arange(0, 35, 2)
    cf = ax.contourf(lon_2d, lat_2d, qflux_700, 
                     cmap='rainbow', levels=levels, 
                     transform=ccrs.PlateCarree())

    # 保存
    os.makedirs('qflux_output', exist_ok=True)
    fig.savefig(f'水汽3/qflux_700_{result}.pdf', dpi=150, bbox_inches='tight')
    
    plt.close()
    ncfile.close()

print("✅ 所有水汽通量图绘制完成！")