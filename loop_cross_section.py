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
# 文件夹路径（修改为你的WRF输出文件夹）
# ======================
file_path = r'wrf_data\3'  # 你的WRF输出文件夹
file_list = os.listdir(file_path)
file_list = [f for f in file_list if f.startswith("wrfout")]

# 按时间排序
file_list = sorted(file_list)

# 剖面起止点（固定不变）
start = (37.5, 110)  # 纬度, 经度
end = (45, 125)

# 输出文件夹
save_dir = r'cross_section\3'
os.makedirs(save_dir, exist_ok=True)

# ======================
# 批量循环处理每个文件
# ======================
for filename in file_list:
    full_path = os.path.join(file_path, filename)
    print("正在处理剖面：", filename)

    # 打开文件
    ncfile = Dataset(full_path)
    wrf_ds = xr.open_dataset(full_path)
    crs = project.get_projection(wrf_ds)

    # ======================
    # 提取时间标签
    # ======================
    parts = filename.split("_")
    month_day = parts[2][5:]
    hour = parts[3]
    domain_part = parts[1]
    result = f"{month_day}_{hour}_{domain_part}"

    # --- 1. 提取变量 ---
    pres = getvar(ncfile, "pressure")
    z = getvar(ncfile, "z", units="dm")
    tc = getvar(ncfile, "tc")
    ua = getvar(ncfile, "ua")
    va = getvar(ncfile, "va")
    wa = getvar(ncfile, "wa")
    theta = getvar(ncfile, "theta")
    q = getvar(ncfile, "QVAPOR")
    rh = getvar(ncfile, "rh")

    # 500hPa高度（用于小地图）
    z_500 = interplevel(z, pres, 500)
    lon_2d_orgin = z_500['XLONG']
    lat_2d_orgin = z_500['XLAT']

    # 高斯滤波
    sigma = 2.0
    z_500_smooth = gaussian_filter(z_500.values, sigma=sigma)

    # --- 2. 构造数据集用于剖面 ---
    ds_to_slice = xr.Dataset({
        "pres": pres,
        "temp_c": tc,
        "ua": ua,
        "va": va,
        'wa': wa,
        'theta': theta,
        'q': q,
        'rh': rh,
        'height': z
    })

    # 清理坐标
    if 'XTIME' in ds_to_slice.coords:
        ds_to_slice = ds_to_slice.drop_vars('XTIME')

    # 重命名经纬度
    ds_to_slice = ds_to_slice.rename({'XLAT': 'lat', 'XLONG': 'lon'})

    # 计算x/y米坐标
    dx = wrf_ds.attrs['DX']
    dy = wrf_ds.attrs['DY']
    nx = ds_to_slice.dims['west_east']
    ny = ds_to_slice.dims['south_north']

    ds_to_slice = ds_to_slice.assign_coords(
        x=('west_east', np.arange(0, nx * dx, dx)),
        y=('south_north', np.arange(0, ny * dy, dy))
    )
    ds_to_slice = ds_to_slice.rename({'south_north': 'y', 'west_east': 'x'})

    # 设置单位
    ds_to_slice.x.attrs['units'] = 'meter'
    ds_to_slice.y.attrs['units'] = 'meter'
    ds_to_slice.x.attrs['standard_name'] = 'projection_x_coordinate'
    ds_to_slice.y.attrs['standard_name'] = 'projection_y_coordinate'

    # 绑定投影
    ds_to_slice = ds_to_slice.metpy.assign_crs(crs.to_cf())
    ds_to_slice = ds_to_slice.metpy.parse_cf()

    # --- 3. 计算剖面 ---
    cross = cross_section(ds_to_slice, start, end).set_coords(('lat', 'lon'))

    # --- 4. 绘图 ---
    lons = cross['lon'].values
    pres = cross['pres'].values
    temp = cross['temp_c'].values
    q = cross['q'].values
    height = cross['height'].values

    lon_2d = np.broadcast_to(lons, pres.shape)

    fig = plt.figure(figsize=(12, 7), dpi=200)
    ax = fig.add_subplot(1, 1, 1)

    # 比湿填色
    levels = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 16, 20, 25]
    cf = ax.contourf(lon_2d, pres, q * 1000, levels=levels, cmap='RdYlBu_r', extend='both')
    cb = plt.colorbar(cf, ax=ax, label='Specific Humidity (g/kg)', shrink=0.8)

    # 填充地形
    ter_pres = pres[0, :]
    ax.fill_between(lons, ter_pres, 1000, color='gray', alpha=0.8)

    # 坐标轴设置
    ax.set_xlim(np.nanmin(lons), np.nanmax(lons))
    ax.set_ylim(1000, 100)
    ax.set_xlabel("Longitude (°E)", fontsize=14)
    ax.set_ylabel("Pressure (hPa)", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.4)

    # --- 小地图 ---
    ax_inset = fig.add_axes([0.1064, 0.6787, 0.2, 0.2], projection=crs)
    project.plot_background(lon_2d_orgin.min(), lon_2d_orgin.max(),
                            lat_2d_orgin.min(), lat_2d_orgin.max(), ax_inset)
    ax_inset.contour(lon_2d_orgin, lat_2d_orgin, z_500_smooth,
                     colors='purple', transform=ccrs.PlateCarree(), linewidths=1)

    # 画剖面线
    start_lat, start_lon = start
    end_lat, end_lon = end
    ax_inset.plot([start_lon, end_lon], [start_lat, end_lat],
                  color='black', linewidth=2, transform=ccrs.PlateCarree(), zorder=5)
    ax_inset.scatter([start_lon, end_lon], [start_lat, end_lat],
                     color='black', s=30, transform=ccrs.PlateCarree(), zorder=6)
    ax_inset.text(start_lon - 15, start_lat - 3, 'path->',
                  transform=ccrs.PlateCarree(), fontsize=12, color='green', fontweight='bold')

    # 保存图片
    save_path = os.path.join(save_dir, f'cross_section_{result}.pdf')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 关闭文件
    ncfile.close()
    wrf_ds.close()

print("✅ 所有剖面图画图完成！")