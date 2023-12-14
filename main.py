from shapely import Polygon, Point, LineString, get_coordinates
import matplotlib.pyplot as plt
import geopandas as gpd
# chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.cs.cmu.edu/~motionplanning/lecture/Chap6-CellDecomp_howie.pdf
p = Polygon(([3, 1], [1, 3], [3, 5], [6, 4], [7, 1]))

t = gpd.GeoSeries([p])
plt.plot(t)

print(p)