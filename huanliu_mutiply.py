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

# ======================
# 文件夹路径
# ======================
file_path = r'wrf_data\3'
file_list = os.listdir(file_path)
file_list = [f for f in file_list if f.startswith("wrfout")]

# 按时间排序（非常重要）
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
    # ✅ 提取时间 + 自动区分 d01/d02
    # ======================
    parts = filename.split("_")
    month_day = parts[2][5:]
    hour = parts[3]
    domain_part = parts[1]  # ✅ 这里提取 d01 / d02

    # 最终文件名：时间 + d01/d02
    result = f"{month_day}_{hour}_{domain_part}"

    # --- 1. 提取变量 ---
    pres = getvar(ncfile, "pressure")
    z = getvar(ncfile, "z", units="dm")
    tc = getvar(ncfile, "tc")
    ua = getvar(ncfile, "ua")
    va = getvar(ncfile, "va")

    # --- 2. 插值 ---
    z_500  = interplevel(z, pres, 500)
    t_500  = interplevel(tc, pres, 500)
    ua_500 = interplevel(ua, pres, 500)
    va_500 = interplevel(va, pres, 500)

    z_850  = interplevel(z, pres, 850)
    t_850  = interplevel(tc, pres, 850)
    ua_850 = interplevel(ua, pres, 850)
    va_850 = interplevel(va, pres, 850)

    lon_2d = z_500['XLONG']
    lat_2d = z_500['XLAT']

    # --- 高斯滤波 ---
    sigma = 2
    z_500_smooth = gaussian_filter(z_500, sigma=sigma)
    t_500_smooth = gaussian_filter(t_500, sigma=sigma)
    z_850_smooth = gaussian_filter(z_850, sigma=sigma)
    t_850_smooth = gaussian_filter(t_850, sigma=sigma)

    # --- 画图 ---
    fig, axarray = plt.subplots(nrows=1, ncols=2, figsize=(12,6), subplot_kw={'projection': crs}, dpi=200)
    axlist = axarray.flatten()

    for ax in axlist:
        project.plot_background(lon_2d[0,0], lon_2d[0,-1], lat_2d[0,0], lat_2d[-1,0], ax)
        
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.3, linestyle=':', color='green',x_inline=False, y_inline=True)
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 8}

    # --------------------
    # 左图 500hPa
    # --------------------
    cf1 = axlist[0].contour(lon_2d, lat_2d, z_500_smooth, 
                            colors='purple', transform=ccrs.PlateCarree(), linewidths=1.3)
    ct1 = axlist[0].contour(lon_2d, lat_2d, t_500_smooth, 
                            colors='red', transform=ccrs.PlateCarree(), linestyles='--', linewidths=1.3)
    axlist[0].clabel(ct1, inline=True, fontsize=10, fmt='%1.0f')
    axlist[0].clabel(cf1, inline=True, fontsize=10, fmt='%1.0f')

    axlist[0].text(lon_2d.min()+0.2, lat_2d.min()+0.2, 
                   f'{result}_500hPa', fontsize=10, color='green', 
                   transform=ccrs.PlateCarree())

    skip = 12
    axlist[0].barbs(
        lon_2d[::skip,::skip].values, lat_2d[::skip,::skip].values,
        ua_500[::skip,::skip].values, va_500[::skip,::skip].values,
        transform=ccrs.PlateCarree(), length=5.5, linewidth=1, color='black')

    # --------------------
    # 右图 850hPa
    # --------------------
    cf2 = axlist[1].contour(lon_2d, lat_2d, z_850_smooth, 
                            colors='purple', transform=ccrs.PlateCarree(), linewidths=1.3)
    ct2 = axlist[1].contour(lon_2d, lat_2d, t_850_smooth, 
                            colors='red', transform=ccrs.PlateCarree(), linestyles='--', linewidths=1.3)
    axlist[1].clabel(ct2, inline=True, fontsize=10, fmt='%1.0f')
    axlist[1].clabel(cf2, inline=True, fontsize=10, fmt='%1.0f')

    axlist[1].text(lon_2d.min()+0.2, lat_2d.min()+0.2, 
                   f'{result}_850hPa', fontsize=10, color='green', 
                   transform=ccrs.PlateCarree())

    axlist[1].barbs(
        lon_2d[::skip,::skip].values, lat_2d[::skip,::skip].values,
        ua_850[::skip,::skip].values, va_850[::skip,::skip].values,
        transform=ccrs.PlateCarree(), length=5.5, linewidth=1, color='black')

    plt.tight_layout()

    os.makedirs('huanliu', exist_ok=True)
    # ✅ 保存时自动区分 d01/d02
    fig.savefig(f'huanliu3\\hl_{result}_500_850.pdf', dpi=200, bbox_inches='tight')
    
    plt.close()
    ncfile.close()

print("✅ 所有文件处理完成！")