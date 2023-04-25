import xarray as xr
import pandas as pd
import pyorc
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

ds = xr.open_dataset("ngwerere/ngwerere_masked.nc")

# also open the original video file
video_file = "ngwerere/ngwerere_20191103.mp4"
video = pyorc.Video(video_file, start_frame=0, end_frame=1)

# borrow the camera config from the velocimetry results
video.camera_config = ds.velocimetry.camera_config

# get the frame as rgb
da_rgb = video.get_frames(method="rgb")


cross_section = pd.read_csv("ngwerere/ngwerere_cross_section.csv")
x = cross_section["x"]
y = cross_section["y"]
z = cross_section["z"]
cross_section2 = pd.read_csv("ngwerere/ngwerere_cross_section_2.csv")
x2 = cross_section2["x"]
y2 = cross_section2["y"]
z2 = cross_section2["z"]

# let's have a look at the cross sections, the coordinates of the cross sections are in UTM 35S coordinates, 
# so we have to tell the axes that the coordinates need to be transformed from that crs into the crs of the axes.
# we also make a very very small buffer of 0.00005 degrees around the area of interest, so that we can 
# clearly see the cross sections.
ax = ds.velocimetry.camera_config.plot(tiles="GoogleTiles", tiles_kwargs={"style": "satellite"}, buffer=0.00005)
ax.plot(x, y, "g--", transform=ccrs.UTM(zone=35, southern_hemisphere=True), label="Cross section #1")
ax.plot(x2, y2, "y--", transform=ccrs.UTM(zone=35, southern_hemisphere=True), label="Cross section #2")
ax.legend()



ds_points = ds.velocimetry.get_transect(x, y, z, crs=32735, rolling=4)
ds_points2 = ds.velocimetry.get_transect(x2, y2, z2, crs=32735, rolling=4)
ds_points


ds_points_q = ds_points.transect.get_q(fill_method="log_interp")
ds_points_q2 = ds_points2.transect.get_q(fill_method="log_interp")
ds_points_q


ax = plt.axes()
ds_points_q["v_eff"].isel(quantile=2).plot(ax=ax)
ds_points_q2["v_eff"].isel(quantile=2).plot(ax=ax)
plt.grid()


# plot the rgb frame first. We use the "camera" mode to plot the camera perspective.
norm = Normalize(vmin=0., vmax=0.6, clip=False)

p = da_rgb[0].frames.plot(mode="camera")

# extract mean velocity and plot in camera projection
ds.mean(dim="time", keep_attrs=True).velocimetry.plot(
    ax=p.axes,
    mode="camera",
    cmap="rainbow",
    scale=200,
    width=0.001,
    alpha=0.3,
    norm=norm,
)

# plot velocimetry point results in camera projection
ds_points_q.isel(quantile=2).transect.plot(
    ax=p.axes,
    mode="camera",
    cmap="rainbow",
    scale=100,
    width=0.003,
    norm=norm,
)
ds_points_q2.isel(quantile=2).transect.plot(
    ax=p.axes,
    mode="camera",
    cmap="rainbow",
    scale=100,
    width=0.003,
    norm=norm,
    add_colorbar=True
)

# store figure in a JPEG
p.axes.figure.savefig("ngwerere.jpg", dpi=200)


# again plot the projected background
from matplotlib.colors import Normalize
norm = Normalize(vmin=0, vmax=0.6, clip=False)
ds_mean = ds.mean(dim="time", keep_attrs=True)
p = da_rgb.frames.project()[0].frames.plot(mode="local")

# plot velocimetry point results in local projection
ds_points_q.isel(quantile=2).transect.plot(
    ax=p.axes,
    mode="local",
    cmap="rainbow",
    scale=10,
    width=0.003,
    norm=norm,
    add_colorbar=True,
)

ds_points_q2.isel(quantile=2).transect.plot(
    ax=p.axes,
    mode="local",
    cmap="rainbow",
    scale=10,
    width=0.003,
    norm=norm,
    add_colorbar=True,
)
# to ensure streamplot understands the directions correctly, all values must 
# be flipped upside down and up-down velocities become down-up velocities.
ds_mean.velocimetry.plot.streamplot(
    ax=p.axes,
    mode="local",
    density=3.,
    minlength=0.05,
    linewidth_scale=2,
    cmap="rainbow",
    norm=norm,
    add_colorbar=True
)


ds_points_q.transect.get_river_flow()
print(ds_points_q["river_flow"])
ds_points_q2.transect.get_river_flow()
print(ds_points_q2["river_flow"])