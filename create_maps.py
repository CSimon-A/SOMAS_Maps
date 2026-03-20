import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle
from matplotlib.patches import Polygon
from matplotlib.patches import ConnectionPatch
import numpy as np

# ---------------------------------------------------------
# 1. Configuration & Coordinates
# ---------------------------------------------------------
# Longitude and Latitude for your three locations
locations = {
    'Orient Harbor, NY': {'lon': -72.30675, 'lat': 41.13664, 'color': 'red'},
    'Cowyard, NY':       {'lon': -72.56537, 'lat': 40.9101, 'color': 'blue'},
    'Wachapreague, VA':  {'lon': -75.68809, 'lat': 37.60437, 'color': 'green'}
}
40.9101

# Define the boundaries (extents) for each map: [lon_min, lon_max, lat_min, lat_max]
extent_main = [-77.5, -69.5, 36.0, 42.5]  # East Coast
extent_ny   = [-72.8, -71.8, 40.7, 41.3]  # Long Island Zoom
extent_va   = [-76.1, -75.3, 37.05, 37.9]  # Virginia Zoom

# Styling
land_color = '#cccccc'  # Gray
water_color = '#ffffff' # White

# ---------------------------------------------------------
# 2. Helper Functions
# ---------------------------------------------------------
def format_map(ax, extent, draw_states=False):
    """Applies common formatting to a map axes."""
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    # Add land and water features
    ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='black', linewidth=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor=water_color)
    ax.add_feature(cfeature.LAKES, facecolor=water_color, edgecolor='black', linewidth=0.5)
    
    if draw_states:
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines',
            scale='10m', facecolor='none')
        ax.add_feature(states_provinces, edgecolor='black', linewidth=0.5)

    # Add Gridlines (Lat/Lon)
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}

def add_north_arrow(ax, x, y, size=0.08):
    """Adds a classic two-tone compass needle North arrow."""
    # The 'N' label
    ax.text(x, y + 0.02, 'N', transform=ax.transAxes, ha='center', va='center',
            fontsize=15, fontweight='bold', zorder=10)
    
    # Compass needle geometry (width and height)
    w = 0.015  
    h = size   
    
    # Left half of the diamond (Black)
    left_poly = Polygon([[x, y], [x-w, y-h*0.8], [x, y-h]], 
                        transform=ax.transAxes, facecolor='black', edgecolor='black', zorder=10)
    # Right half of the diamond (White)
    right_poly = Polygon([[x, y], [x+w, y-h*0.8], [x, y-h]], 
                         transform=ax.transAxes, facecolor='white', edgecolor='black', zorder=10)
    
    ax.add_patch(left_poly)
    ax.add_patch(right_poly)

def add_scale_bar(ax, length_km, location=(0.5, 0.05), segments=2):
    """Adds a segmented alternating black/white scale bar with clean labels."""
    ext = ax.get_extent()
    lat_center = (ext[2] + ext[3]) / 2
    lon_degree_len = 111.32 * np.cos(np.radians(lat_center))
    length_degrees = length_km / lon_degree_len
    
    segment_degrees = length_degrees / segments
    segment_km = length_km / segments
    x, y = location
    
    # Slightly larger offset to lift the text further off the line
    y_offset = (ext[3] - ext[2]) * 0.025 
    
    # 1. Thick black background line
    ax.plot([x, x + length_degrees], [y, y], transform=ccrs.PlateCarree(), 
            color='black', linewidth=6, solid_capstyle='butt', zorder=9)
    
    # 2. Alternating segments
    for i in range(segments):
        color = 'black' if i % 2 == 0 else 'white'
        ax.plot([x + i*segment_degrees, x + (i+1)*segment_degrees], [y, y], 
                transform=ccrs.PlateCarree(), color=color, linewidth=4, 
                solid_capstyle='butt', zorder=10)
        
        # Add the tick numbers (formatted to drop trailing zeros)
        val = i * segment_km
        ax.text(x + i*segment_degrees, y + y_offset, f"{val:g}", 
                transform=ccrs.PlateCarree(), ha='center', va='bottom', fontsize=9, zorder=11)
        
    # 3. Final number with unit
    ax.text(x + length_degrees, y + y_offset, f"{length_km:g} km", 
            transform=ccrs.PlateCarree(), ha='center', va='bottom', fontsize=9, zorder=11)

# ---------------------------------------------------------
# 3. Figure Layout Setup
# ---------------------------------------------------------
fig = plt.figure(figsize=(14, 8))
# Create a grid: 1 row, 2 columns. The right column will be split into 2 rows later.
gs = fig.add_gridspec(2, 2, width_ratios=[1.5, 1]) 

# Create Axes using PlateCarree projection
ax_main = fig.add_subplot(gs[:, 0], projection=ccrs.PlateCarree())
ax_ny   = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())
ax_va   = fig.add_subplot(gs[1, 1], projection=ccrs.PlateCarree())

# ---------------------------------------------------------
# 4. Draw Main Map (East Coast)
# ---------------------------------------------------------
format_map(ax_main, extent_main, draw_states=True)
add_north_arrow(ax_main, x=0.1, y=0.85)
add_scale_bar(ax_main, length_km=150, location=(-72, 36.5), segments=3)

# Plot markers on main map
for name, data in locations.items():
    ax_main.plot(data['lon'], data['lat'], marker='o', color=data['color'], 
                 markersize=8, markeredgecolor='black', transform=ccrs.PlateCarree(), zorder=5)

# Add Bounding Boxes for the zoom regions
for ext in [extent_ny, extent_va]:
    rect = Rectangle((ext[0], ext[2]), ext[1]-ext[0], ext[3]-ext[2], 
                     linewidth=1.5, edgecolor='black', facecolor='none', 
                     transform=ccrs.PlateCarree(), zorder=6)
    ax_main.add_patch(rect)

# ---------------------------------------------------------
# 5. Draw Zoom Map 1 (Long Island, NY)
# ---------------------------------------------------------
format_map(ax_ny, extent_ny)
add_scale_bar(ax_ny, length_km=20, location=(-72.15, 40.725), segments=2)

# Plot NY markers
for name in ['Orient Harbor, NY', 'Cowyard, NY']:
    data = locations[name]
    ax_ny.plot(data['lon'], data['lat'], marker='o', color=data['color'], 
               markersize=10, markeredgecolor='black', transform=ccrs.PlateCarree(), zorder=5)
    ax_ny.text(data['lon'] + 0.02, data['lat'], name.split(',')[0], 
               transform=ccrs.PlateCarree(), fontsize=10, fontweight='bold', va='center')

# ---------------------------------------------------------
# 6. Draw Zoom Map 2 (Wachapreague, VA)
# ---------------------------------------------------------
format_map(ax_va, extent_va)
add_scale_bar(ax_va, length_km=20, location=(-75.7, 37.1), segments=2)

# Plot VA marker
data = locations['Wachapreague, VA']
ax_va.plot(data['lon'], data['lat'], marker='o', color=data['color'], 
           markersize=10, markeredgecolor='black', transform=ccrs.PlateCarree(), zorder=5)
ax_va.text(data['lon'] + 0.02, data['lat'], 'Wachapreague', 
           transform=ccrs.PlateCarree(), fontsize=10, fontweight='bold', va='center')

# ---------------------------------------------------------
# 7. Add Connecting Zoom Lines
# ---------------------------------------------------------
def add_zoom_lines(ax_main, ax_zoom, extent, color='black'):
    """Draws lines from the bounding box on the main map to the zoomed axes."""
    # Bounding box right-side corners on the main map (Data coordinates)
    # extent = [lon_min, lon_max, lat_min, lat_max]
    box_top_right = (extent[1], extent[3])
    box_bottom_right = (extent[1], extent[2])
    
    # ConnectionPatch connects points between two different axes perfectly
    # Top line: Top-Right of box -> Top-Left of zoomed axes
    con1 = ConnectionPatch(xyA=box_top_right, xyB=(0, 1), 
                           coordsA=ax_main.transData, coordsB=ax_zoom.transAxes,
                           axesA=ax_main, axesB=ax_zoom, 
                           color=color, linewidth=1, linestyle='--', alpha=0.6, zorder=10)
    
    # Bottom line: Bottom-Right of box -> Bottom-Left of zoomed axes
    con2 = ConnectionPatch(xyA=box_bottom_right, xyB=(0, 0), 
                           coordsA=ax_main.transData, coordsB=ax_zoom.transAxes,
                           axesA=ax_main, axesB=ax_zoom, 
                           color=color, linewidth=1, linestyle='--', alpha=0.6, zorder=10)
    
    # Add the lines to the figure
    ax_main.add_artist(con1)
    ax_main.add_artist(con2)

# Draw the lines for both regions
# add_zoom_lines(ax_main, ax_ny, extent_ny)
# add_zoom_lines(ax_main, ax_va, extent_va)

# ---------------------------------------------------------
# 8. Final Polish
# ---------------------------------------------------------
plt.subplots_adjust(wspace=0.1, hspace=0.2)
plt.suptitle("Project Map: Survey Locations", fontsize=16, fontweight='bold')

# Save the figure to your computer
plt.savefig('project_map_layout.png', dpi=300, bbox_inches='tight')
plt.show()

