import pyorc
import matplotlib.pyplot as plt
import xarray as xr
import cartopy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from dask.diagnostics import ProgressBar

cam_config = pyorc.load_camera_config("ngwerere/ngwerere.json")
video_file = "ngwerere/ngwerere_20191103.mp4"
video = pyorc.Video(video_file, camera_config=cam_config, start_frame=0, end_frame=125, stabilize="fixed", h_a=0.)
video

da = video.get_frames()
da

frm = da[0]
plt.imshow(frm)
plt.savefig("2-frame_or.jpg", bbox_inches="tight", dpi=72)

da[0].frames.plot(cmap="gray")

da_norm = da.frames.normalize()
da_norm[0].frames.plot(cmap="gray")

f = plt.figure(figsize=(16, 9))
da_norm_proj = da_norm.frames.project()
da_norm_proj[0].frames.plot(cmap="gray")

frm = da_norm_proj[0]
plt.imshow(frm)
plt.savefig("2-frame.jpg", bbox_inches="tight", dpi=72)


# extract frames again, but now with rgb
da_rgb = video.get_frames(method="rgb")
# project the rgb frames, same as before
da_rgb_proj = da_rgb.frames.project()
# plot the first frame in geographical mode
p = da_rgb_proj[0].frames.plot(mode="geographical")

plt.imshow(da_rgb_proj[0])
plt.savefig("2-geo.jpg", bbox_inches="tight", dpi=72)

# for fun, let's also add a satellite background from cartopy
import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
tiles = cimgt.GoogleTiles(style="satellite")
p.axes.add_image(tiles, 19)
# zoom out a little bit so that we can actually see a bit
p.axes.set_extent([
    da_rgb_proj.lon.min() - 0.0001,
    da_rgb_proj.lon.max() + 0.0001,
    da_rgb_proj.lat.min() - 0.0001,
    da_rgb_proj.lat.max() + 0.0001],
    crs=ccrs.PlateCarree()
)

plt.imshow(da_norm_proj[0])
plt.savefig("2-tiled_b.jpg", bbox_inches="tight", dpi=72)

exit()

piv = da_norm_proj.frames.get_piv()
delayed_obj = piv.to_netcdf("ngwerere_piv.nc", compute=False)
with ProgressBar():
    results = delayed_obj.compute()

    