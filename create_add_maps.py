import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Polygon
import numpy as np
import os

# ---------------------------------------------------------
# 1. Configuration & Coordinates
# ---------------------------------------------------------
locations = {
    'Orient Harbor': {'lon': -72.30675, 'lat': 41.13664, 'color': 'red'},
    'Cow Yard':      {'lon': -72.56537, 'lat': 40.9101,  'color': 'blue'}
}

extents = {
    'Northeast': [-82.0, -68.0, 38.0, 46.0],
    'NY_State':  [-80.0, -71.5, 40.0, 45.2],
    'NYC_LI':    [-74.5, -71.5, 40.3, 41.5],
    'LI_Tight':  [-73.5, -71.8, 40.5, 41.3],
    'Peconic':   [-72.7, -71.78, 40.74, 41.25],
    'Custom_1':  [-76.5, -71.5, 37.0, 41.5],
    'Custom_2':  [-76.5, -69.5, 37.0, 43.0],
    'Custom_3':  [-75.5, -71.5, 38.75, 41.5],
    'Custom_4':  [-75.5, -69.5, 38.75, 43.0]
}

land_color = '#cccccc'
water_color = '#ffffff'

output_folder = 'map_outputs'
os.makedirs(output_folder, exist_ok=True)

# ---------------------------------------------------------
# 2. Helper Functions
# ---------------------------------------------------------
def format_map(ax, extent, draw_states=True):
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='black', linewidth=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor=water_color)
    ax.add_feature(cfeature.LAKES, facecolor=water_color, edgecolor='black', linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=1.0, zorder=3)
    
    if draw_states:
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines',
            scale='10m', facecolor='none')
        ax.add_feature(states_provinces, edgecolor='black', linewidth=0.5, zorder=4)

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 9}
    gl.ylabel_style = {'size': 9}

def add_north_arrow(ax, x, y, size=0.08):
    """Adds a North arrow that mathematically corrects its width to prevent squishing."""
    # 1. Add the "N" text safely inside the map
    ax.text(x, y + 0.02, 'N', transform=ax.transAxes, ha='center', va='center',
            fontsize=16, fontweight='bold', zorder=10)
    
    # 2. Calculate the physical aspect ratio of the map frame
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    axes_aspect_ratio = (x1 - x0) / (y1 - y0)
    
    # 3. Calculate width/height to keep the diamond shape symmetric
    h = size   
    w = h * 0.18 / axes_aspect_ratio  # 0.18 is the visual ratio of width-to-height
    
    # 4. Draw polygons
    left_poly = Polygon([[x, y], [x-w, y-h*0.8], [x, y-h]], 
                        transform=ax.transAxes, facecolor='black', edgecolor='black', zorder=10)
    right_poly = Polygon([[x, y], [x+w, y-h*0.8], [x, y-h]], 
                         transform=ax.transAxes, facecolor='white', edgecolor='black', zorder=10)
    
    ax.add_patch(left_poly)
    ax.add_patch(right_poly)

def add_scale_bar(ax, extent, length_km, segments=2, loc='right'):
    lat_center = (extent[2] + extent[3]) / 2
    lon_degree_len = 111.32 * np.cos(np.radians(lat_center))
    length_degrees = length_km / lon_degree_len
    
    segment_degrees = length_degrees / segments
    segment_km = length_km / segments
    
    # Lowered Y-axis placement (0.06)
    y = extent[2] + (extent[3] - extent[2]) * 0.06
    y_offset = (extent[3] - extent[2]) * 0.02 
    
    if loc == 'left':
        x = extent[0] + (extent[1] - extent[0]) * 0.05
    else: 
        x = extent[1] - (extent[1] - extent[0]) * 0.05 - length_degrees
    
    ax.plot([x, x + length_degrees], [y, y], transform=ccrs.PlateCarree(), 
            color='black', linewidth=6, solid_capstyle='butt', zorder=9)
    
    for i in range(segments):
        color = 'black' if i % 2 == 0 else 'white'
        ax.plot([x + i*segment_degrees, x + (i+1)*segment_degrees], [y, y], 
                transform=ccrs.PlateCarree(), color=color, linewidth=4, 
                solid_capstyle='butt', zorder=10)
        
        val = i * segment_km
        ax.text(x + i*segment_degrees, y + y_offset, f"{val:g}", 
                transform=ccrs.PlateCarree(), ha='center', va='bottom', fontsize=9, zorder=11)
        
    ax.text(x + length_degrees, y + y_offset, f"{length_km:g} km", 
            transform=ccrs.PlateCarree(), ha='center', va='bottom', fontsize=9, zorder=11)

def plot_markers(ax):
    for data in locations.values():
        ax.plot(data['lon'], data['lat'], marker='o', color=data['color'], 
                markersize=10, markeredgecolor='black', transform=ccrs.PlateCarree(), zorder=15)

# ---------------------------------------------------------
# 3. Map Generation Configuration
# ---------------------------------------------------------
map_configs = [
    {
        'filename': 'Northeast_US.png',
        'title': 'Northeast US & NY State',
        'extent': extents['Northeast'],
        'scale_km': 200,
        'scale_loc': 'right',
        'draw_states': True  # Keep borders
    },
    {
        'filename': 'NY_State.png',
        'title': 'New York State',
        'extent': extents['NY_State'],
        'scale_km': 100,
        'scale_loc': 'left',
        'draw_states': True  # Keep borders
    },
    {
        'filename': 'NYC_and_Long_Island.png',
        'title': 'NYC & Long Island',
        'extent': extents['NYC_LI'],
        'scale_km': 50,
        'scale_loc': 'right',
        'draw_states': False # Remove borders
    },
    {
        'filename': 'Long_Island_Tight.png',
        'title': 'Long Island',
        'extent': extents['LI_Tight'],
        'scale_km': 25,
        'scale_loc': 'right',
        'draw_states': False # Remove borders
    },
    {
        'filename': 'Peconic_Bay.png',
        'title': 'Peconic Bay Survey Locations',
        'extent': extents['Peconic'],
        'scale_km': 10,
        'scale_loc': 'right',
        'draw_states': False # Remove borders
    },
    {
        'filename': 'Custom_1_Map.png',
        'title': 'Coastal Extent 1 (Lat 37-41.5)',
        'extent': extents['Custom_1'],
        'scale_km': 100,
        'scale_loc': 'right',
        'draw_states': True 
    },
    {
        'filename': 'Custom_2_Map.png',
        'title': 'Coastal Extent 2 (Lat 37-43)',
        'extent': extents['Custom_2'],
        'scale_km': 100,
        'scale_loc': 'right',
        'draw_states': True 
    },
    {
        'filename': 'Custom_3_Map.png',
        'title': 'Coastal Extent 3 (Lat 38.75-41.5)',
        'extent': extents['Custom_3'],
        'scale_km': 100,
        'scale_loc': 'right',
        'draw_states': True 
    },
    {
        'filename': 'Custom_4_Map.png',
        'title': 'Coastal Extent 4 (Lat 38.75-43)',
        'extent': extents['Custom_4'],
        'scale_km': 100,
        'scale_loc': 'right',
        'draw_states': True 
    }
]

# ---------------------------------------------------------
# 4. Map Generation Loop
# ---------------------------------------------------------
print(f"Generating maps and saving to '{output_folder}/'...")

for config in map_configs:
    print(f" -> Creating {config['filename']}...")
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    # We now pass the 'draw_states' config rule into the format function
    format_map(ax, config['extent'], draw_states=config['draw_states'])
    
    add_scale_bar(ax, config['extent'], length_km=config['scale_km'], loc=config['scale_loc'])
    
    # The arrow is now firmly attached to the inside of the map box at 10% right, 88% up.
    add_north_arrow(ax, x=0.1, y=0.88, size=0.08)
        
    plot_markers(ax)
    
    plt.title(config['title'], fontsize=14, fontweight='bold', pad=15)
    
    save_path = os.path.join(output_folder, config['filename'])
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

print("All maps generated successfully!")