import xarray as xr
import pyorc
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

## 1 - Configura o Video. atraves de parametrizacoes e marcacoes 


# - STEP 1 - Pega o primeiro frame do video 
#%matplotlib notebook
video_file = "ngwerere/ngwerere_20191103.mp4"
video = pyorc.Video(video_file, start_frame=0, end_frame=1)  # we only need one frame
frame = video.get_frame(0, method="rgb")

# plot frame on a notebook-style window
f = plt.figure(figsize=(10, 6))
plt.imshow(frame)

gcps = dict(
    src=[
        [1421, 1001],
        [1251, 460],
        [421, 432],
        [470, 607]
    ]
)

f = plt.figure(figsize=(16, 9))
plt.imshow(frame)
plt.plot(*zip(*gcps["src"]), "rx", markersize=20, label="Control points")
plt.legend()


# first add our UTM 35S coordinates. This MUST be in precisely the same order as the src coordinates.
gcps["dst"] = [
    [642735.8076, 8304292.1190],  # lowest right coordinate
    [642737.5823, 8304295.593],  # highest right coordinate
    [642732.7864, 8304298.4250],  # highest left coordinate
    [642732.6705, 8304296.8580]  # highest right coordinate
]

# # if we would use this video as survey in video, the lines below are also needed, 
# # and proper values need to be filled in. They are now commented out.
# gcps["h_ref"] = <your locally measured water level during survey in>
gcps["z_0"] = 1182.2

# set the height and width
height, width = frame.shape[0:2]

# now we use everything to make a camera configuration
cam_config = pyorc.CameraConfig(height=height, width=width, gcps=gcps, crs=32735)

ax = cam_config.plot(tiles="GoogleTiles", tiles_kwargs={"style": "satellite"})
corners = [
    [292, 817],
    [50, 166],
    [1200, 236],
    [1600, 834]
]
cam_config.set_bbox_from_corners(corners)
cam_config.resolution = 0.01
cam_config.window_size = 25

f = plt.figure(figsize=(10, 6))
plt.imshow(frame)
plt.plot(*zip(*gcps["src"]), "rx", markersize=20, label="Control points")
plt.plot(*zip(*corners), "co", label="Corners of AOI")
plt.legend()

ax1 = cam_config.plot(tiles="GoogleTiles", tiles_kwargs={"style": "satellite"})

f = plt.figure()
ax2 = plt.axes()
ax2.imshow(frame)
cam_config.plot(ax=ax2, camera=True)

plt.savefig("ngwerere_camconfig.jpg", bbox_inches="tight", dpi=72)
print(cam_config)
cam_config.to_file("ngwerere.json")

plt.savefig('foo.png', bbox_inches='tight')