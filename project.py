import cartopy.crs as ccrs
import cartopy.feature as cfeature


def get_projection(ds):
    crs = ccrs.LambertConformal(
    central_longitude=ds.CEN_LON,
    central_latitude=ds.CEN_LAT,
    standard_parallels=(ds.TRUELAT1, ds.TRUELAT2),
    globe=ccrs.Globe(ellipse='sphere', semimajor_axis=6370000, semiminor_axis=6370000)
    )
    return crs

def plot_background(lon_min, lon_max, lat_min, lat_max, ax):
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.gridlines(draw_labels=True,dms=True)
    return ax