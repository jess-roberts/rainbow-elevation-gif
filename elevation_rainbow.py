import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import os
import glob 
from PIL import Image
import numpy as np

COUNTRY = 'Italy'
BACKGROUND_COLOR = '#1B1B1B'
COUNTRY_FILL_COLOR = '#0d0d0d'
ELELVATION_CAP = 3000
CRS = 'EPSG:3857'

plt.rcParams["font.family"] = "serif"

def make_gif_from_images(gif_title, img_list=None, img_search_key=None, remove_imgs=True, sort_numeric=True):
    """
    Create gif from a list of PNG iamges.
        Args:
            gif_title: Output filename of the gif
            img_list: List of PNG file pathways to merge into a gif (optional)
            img_search_key: PNG file pathways key to search for to create image list (optionl)
            remove_imgs: Option to remove PNG images after merging them into a gif
            sort_numeric: Option to sort the PNG images according to a numeric value in the title
        Returns: 
            N/A 
    """
    frames = []

    if not img_list:
        imgs = glob.glob(f"{img_search_key}*.png")
    else:
        imgs = img_list

    if sort_numeric:
        imgs = sorted(imgs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    else:
        imgs = img_list
    
    for i in imgs:
        new_frame = Image.open(i)
        frames.append(new_frame)
        frames[0].save(f'{gif_title}.gif', format='GIF',
                    append_images=frames[1:],
                    save_all=True,
                    duration=250, loop=0, dpi=500)
        if remove_imgs:
            os.remove(i)


# Read in contour and country shapefile (e.g. generated in QGIS)
contours = gpd.read_file('./italy_contours_100.shp').to_crs(CRS) # needs unzipping
country = gpd.read_file('./italy.shp').to_crs(CRS)
bbox = contours.total_bounds 

# Capping contours to a maximum value
all_values = sorted(contours['ELEV'].unique())
filtered_vals = list(filter(lambda all_values: all_values <= ELELVATION_CAP, all_values))
color = iter(cm.rainbow(np.linspace(0, 1, len(filtered_vals))))

### CREATE A PNG PER ELEVATION CONTOUR ###
outputs= []
for cont in filtered_vals:
    # Move along rainbow colormap
    c = next(color)

    # Set up new plot
    fig, fig_ax = plt.subplots(figsize=(6,6))
    fig.patch.set_facecolor(BACKGROUND_COLOR)

    # Plot country
    country.plot(ax=fig_ax, color=COUNTRY_FILL_COLOR, alpha=1, zorder=3)
    
    # Plot all contours up to elevation
    filtered = contours[contours["ELEV"] <= cont]  
    filtered.plot(ax=fig_ax, color='#4A4A4A', alpha=0.9, zorder=3, linewidth=0.2)
    
    # Plot contour at that elevation
    lead_contour = contours[contours["ELEV"] == cont]
    lead_contour.plot(ax=fig_ax, color=c, alpha=1, zorder=3, linewidth=1)
    
    # Format chart
    fig_ax.axis("off")
    fig_ax.set_ylim(bbox[1], bbox[3])
    fig_ax.set_xlim(bbox[0], bbox[2])
    plt.gca().set_position([0, 0, 1, 1])
    fig_ax.set_aspect('equal')
    
    # Add country title and elevation label at relative locations
    plt.text(0.1, 0.15, f'{COUNTRY}', fontsize=22, color='#fff', transform=fig_ax.transAxes, zorder=5)
    plt.text(0.1, 0.1, f'{round(cont)}m', fontsize=18, color=c, transform=fig_ax.transAxes, zorder=5)

    # Export
    output = f'./{COUNTRY}_for_gif_{round(cont)}.png'
    outputs.append(output)
    plt.savefig(output)
    print(f'{output} exported')
    plt.close()

### MAKE GIF FROM ELEVATION PNGS ###
make_gif_from_images(COUNTRY, outputs)
