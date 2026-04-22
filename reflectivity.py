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
from metpy.plots import ctables

# ======================
# 文件夹路径（修改为你的wrfout所在文件夹）
# ======================
file_path = r'wrf_data\3'  # 你的原始文件路径文件夹
file_list = os.listdir(file_path)
file_list = [f for f in file_list if f.startswith("wrfout")]

# 按时间排序（非常重要）
file_list = sorted(file_list)

# ======================
# 开始循环绘图（700hPa 雷达反射率）
# ======================
for filename in file_list:
    full_path = os.path.join(file_path, filename)
    print("正在处理：", filename)

    # 打开文件
    ncfile = Dataset(full_path)
    wrf_ds = xr.open_dataset(full_path)
    crs = project.get_projection(wrf_ds)

    # ======================
    # 提取时间 + 区域 d01/d02
    # ======================
    parts = filename.split("_")
    month_day = parts[2][5:]
    hour = parts[3]
    domain_part = parts[1]
    result = f"{month_day}_{hour}_{domain_part}"

    # --- 1. 提取变量（雷达反射率）---
    pres = getvar(ncfile, "pressure")      # 全层气压 (hPa)
    z = getvar(ncfile, "z", units="dm")    # 位势高度
    reflectivity = getvar(ncfile, "dbz")   # 雷达反射率 (dBZ)

    # 插值到 700 hPa
    reflectivity_700 = interplevel(reflectivity, pres, 700)

    # 经纬度
    lon_2d, lat_2d = getvar(ncfile, "lon"), getvar(ncfile, "lat")

    # --- 2. 画图 ---
    fig, ax = plt.subplots(figsize=(12,8), subplot_kw={'projection':crs}, dpi=150)

    # 绘制地图底图
    project.plot_background(lon_2d[0,0], lon_2d[0,-1], lat_2d[0,0], lat_2d[-1,0], ax)

    # 添加经纬度网格（可选，更美观）
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.3,
                      linestyle=':', color='green', x_inline=False, y_inline=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 8}

    # 绘制 700hPa 雷达反射率填色图
    cf = ax.contourf(lon_2d, lat_2d, reflectivity_700,
                     levels=np.arange(0, 60, 5), cmap='jet',
                     transform=ccrs.PlateCarree())
    ax.text(lon_2d.min()+7.5, lat_2d.min()+0.2,
            f'{result}_700hPa_Reflectivity', fontsize=13, color='green',
            transform=ccrs.PlateCarree(), weight='bold')
    # 色条
    cbar = plt.colorbar(cf, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('Reflectivity (dBZ)', fontsize=10)

    plt.tight_layout()

    # --- 3. 保存图片 ---
    os.makedirs('reflectivity\\3', exist_ok=True)  # 保存到这个文件夹
    fig.savefig(f'reflectivity\\3\\dbz_{result}_700hPa.pdf', dpi=150, bbox_inches='tight')

    # 关闭释放内存
    plt.close()
    ncfile.close()
    wrf_ds.close()

print("✅ 所有 700hPa 雷达反射率绘图完成！")