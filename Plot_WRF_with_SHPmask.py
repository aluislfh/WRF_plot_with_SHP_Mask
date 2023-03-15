from mpl_toolkits.basemap import Basemap
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt
#from osgeo import gdal
import numpy as np
import shapefile
#import xarray as xr
import netCDF4 as netcdf
import matplotlib.colors as colors

##############################################################################

# https://basemaptutorial.readthedocs.io/en/latest/clip.html

##############################################################################

fig = plt.figure()
ax = fig.add_subplot(111)

###############################################################################
# Cargando shapefile y extrayendo la provincia deseada

sf = shapefile.Reader("PAN_adm1")

for shape_rec in sf.shapeRecords():

    if shape_rec.record[4] == 'Herrera':  # si quieres que lo haga para todo panama comenta esta linea
        vertices = []
        codes = []
        pts = shape_rec.shape.points
        prt = list(shape_rec.shape.parts) + [len(pts)]
        for i in range(len(prt) - 1):
            for j in range(prt[i], prt[i+1]):
                vertices.append((pts[j][0], pts[j][1]))
            codes += [Path.MOVETO]
            codes += [Path.LINETO] * (prt[i+1] - prt[i] -2)
            codes += [Path.CLOSEPOLY]
        clip = Path(vertices, codes)
        clip = PathPatch(clip, transform=ax.transData)

###############################################################################
# Read in data:
# -------------

# Open a netCDF data file using xarray default engine and load the data into xarrays, as well as extract slices for
# ``time=0`` and the ``lev=500`` hPa level
ds = netcdf.Dataset("wrfout_d03_2022-07-19_00:00:00")

# For convenience only, extract the U,V,T and lat and lon variables

Temp = ds["T2"][0,:,:]-273.15

lat = ds["XLAT"][0,:,:]
lon = ds["XLONG"][0,:,:]


###############################################################################
# Create map

m = Basemap(llcrnrlon=np.min(np.array(vertices)[:,0])-0.1, llcrnrlat=np.min(np.array(vertices)[:,1])-0.1, urcrnrlon=np.max(np.array(vertices)[:,0])+0.1, urcrnrlat=np.max(np.array(vertices)[:,1])+0.1, resolution = 'h', projection = 'cyl')


def cm_temp():

    a = np.array([0,2,4,6,8,10,12,14,16,17,18,19,19.5,20,20.5,21.0,21.5,22.0,22.5,23.0,23.5,24.0,25.0,25.5,26.0,26.5,27.0,27.5,28.0,28.5,29.0,29.7,30.7,31.5,32,33,34,35,36])

    # Bins normalized between 0 and 1
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    C = np.array([[140,140,140],
        [188,188,188],
        [230,230,230],
        [255,255,255],
        [190,190,255],
        [160,140,255],
        [112,96,220],
        [90,70,200],
        [55,40,165],
        [20,0,130],
        [20,100,210],
        [40,130,240],
        [80,165,245],
        [10,145,70],
        [40,170,85],
        [75,175,105],
        [120,195,110],
        [150,205,125],
        [190,225,135],
        [200,230,140],
        [220,240,150],
        [240,240,195],
        [240,235,140],
        [240,215,130],
        [245,200,90],
        [240,175,75],
        [230,155,60],
        [240,135,45],
        [225,115,0],
        [250,80,60],
        [240,15,105],
        [140,0,0],
        [190,0,0],
        [100,0,5],
        [120,80,70],
        [140,100,90],
        [180,140,130],
        [225,190,180],
        [248,219,214]])/255.

    # Create a tuple for every color indicating the normalized position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, C[i]))

    cmap = colors.LinearSegmentedColormap.from_list("Temperature", COLORS)

    return cmap,a

plt.title('Mapa de prueba con mascara del shapefile', fontsize = 8)

m.drawmeridians(range(0, 360, 1),labels=[1,0,0,1],fontsize=8, linewidth=0)
m.drawparallels(range(-180, 180, 1),labels=[1,0,0,1],fontsize=8, linewidth=0)

m.readshapefile('PAN_adm1', 'provincias', color='grey', linewidth=0.3)

#m.drawstates(color='gray', linewidth=0.25)
m.drawcoastlines(color='k', linewidth=0.9)
m.drawcountries(color='k', linewidth=0.9)

cmap1,clevs1=cm_temp()

cs = m.contourf(lon,lat,Temp,clevs1,cmap=cmap1, extend='both')

cs.cmap.set_under((1.0, 1.0, 1.0))
cs.cmap.set_over((255/255,0/255,0/255))

###############################################################################
# mascara del shapefile

for contour in cs.collections:
        contour.set_clip_path(clip)

m.colorbar(cs)

plt.savefig('mapa_prueba.png', dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()
